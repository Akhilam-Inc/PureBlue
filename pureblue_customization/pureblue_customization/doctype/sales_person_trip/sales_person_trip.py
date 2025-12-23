# Copyright (c) 2025, Akhilam Inc. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import math
from collections import defaultdict
from frappe.utils import getdate


class SalesPersonTrip(Document):
	pass

logger = frappe.logger("sales_person_trip")


# --------------------------------------------------
# Distance calculation (Haversine)
# --------------------------------------------------
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # KM

    lat1, lon1, lat2, lon2 = map(
        math.radians, [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 3)


def parse_location(location):
    lat, lon = location.split(",")
    return float(lat.strip()), float(lon.strip())


# --------------------------------------------------
# Scheduler Job
# --------------------------------------------------
def generate_sales_person_trips():

    try:
        checkins = frappe.db.sql(
            """
            SELECT
                ec.employee,
                ec.time,
                ec.location,
                sp.name AS sales_person
            FROM `tabEmployee Checkin` ec
            INNER JOIN `tabSales Person` sp
                ON sp.employee = ec.employee
            WHERE
                ec.log_type = 'IN'
                AND ec.location IS NOT NULL
                AND ec.location != ''
            ORDER BY ec.employee, ec.time
            """,
            as_dict=True,
        )

        if not checkins:
            logger.info("No employee checkins found")
            return

        grouped = defaultdict(list)

        for row in checkins:
            date = getdate(row["time"])
            grouped[(row["employee"], date)].append(row)

        for (employee, date), rows in grouped.items():
            try:
                rows = sorted(rows, key=lambda x: x["time"])

                if len(rows) < 2:
                    logger.info(
                        f"Skipping distance calculation | Employee={employee} Date={date} Reason=Single checkin"
                    )
                    continue

                # Parse locations
                start_lat, start_lon = parse_location(rows[0]["location"])
                end_lat, end_lon = parse_location(rows[-1]["location"])

                distance_km = haversine_distance(
                    start_lat, start_lon,
                    end_lat, end_lon
                )

                logger.info(
                    f"""
					Distance Calculated
					Employee      : {employee}
					Sales Person  : {rows[0]['sales_person']}
					Date          : {date}
					Start Loc     : {rows[0]['location']}
					End Loc       : {rows[-1]['location']}
					Start (lat,lng): {start_lat}, {start_lon}
					End   (lat,lng): {end_lat}, {end_lon}
					Distance (KM) : {distance_km}
					"""
				)

                # Ignore GPS noise
                if distance_km < 0.1:
                    logger.info(
                        f"Distance ignored due to GPS noise | Employee={employee} Date={date} Distance={distance_km}"
                    )
                    distance_km = 0

                # Prevent duplicate
                if frappe.db.exists(
                    "Sales Person Trip",
                    {"employee": employee, "date": date},
                ):
                    continue

                trip = frappe.new_doc("Sales Person Trip")
                trip.employee = employee
                trip.sales_person = rows[0]["sales_person"]
                trip.date = date
                trip.start_location = rows[0]["location"]
                trip.end_location = rows[-1]["location"]
                trip.distance = distance_km

                trip.insert(ignore_permissions=True)

                logger.info(
                    f"Sales Person Trip created | Employee={employee} Date={date} Distance={distance_km}"
                )

            except Exception:
                frappe.log_error(
                    title="Sales Person Trip Calculation Failed",
                    message=f"""
					Employee: {employee}
					Date: {date}
					Traceback:
					{frappe.get_traceback()}
										""",
				)

                logger.error(
                    f"Calculation failed | Employee={employee} Date={date}",
                    exc_info=True,
                )

                continue

        frappe.db.commit()

    except Exception:
        frappe.log_error(
            title="Sales Person Trip Scheduler Crashed",
            message=frappe.get_traceback(),
        )