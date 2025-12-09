# Copyright (c) 2025, Akhilam Inc. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 150},
		{"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 120},
		{"label": "From Time", "fieldname": "in_time", "fieldtype": "Datetime", "width": 150},
		{"label": "To Time", "fieldname": "out_time", "fieldtype": "Datetime", "width": 150},
		{"label": "Duration", "fieldname": "duration", "fieldtype": "Time", "width": 120},

		{"label": "In Location", "fieldname": "in_location", "fieldtype": "Data", "width": 150},
		{"label": "Out Location", "fieldname": "out_location", "fieldtype": "Data", "width": 150},

		{"label": "In Image", "fieldname": "in_image", "fieldtype": "Attach Image", "width": 120},
		{"label": "Out Image", "fieldname": "out_image", "fieldtype": "Attach Image", "width": 120},

		# New Activity Columns
		{"label": "Activity Type", "fieldname": "activity_type", "fieldtype": "Data", "width": 120},
		{"label": "Reference", "fieldname": "reference", "fieldtype": "Dynamic Link", "options": "activity_type", "width": 150},
		{"label": "Detail", "fieldname": "detail", "fieldtype": "Data", "width": 250}
	]


def get_data(filters):
    # --- 1️⃣ VALIDATE DATE FILTERS ---
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    if not from_date or not to_date:
        frappe.throw("Please select both <b>From Date</b> and <b>To Date</b>.")

    if from_date > to_date:
        frappe.throw("<b>From Date</b> cannot be greater than <b>To Date</b>.")

    # --- 2️⃣ CHECK IF CHECKIN RECORDS EXIST ---
    checkins_exist = frappe.db.exists(
        "Employee Checkin",
        {
            "time": ["between", [from_date + " 00:00:00", to_date + " 23:59:59"]]
        }
    )

    if not checkins_exist:
        frappe.throw("No Employee Checkin records found for the selected date range.")

    # --- 3️⃣ FETCH CHECKINS ---
    checkins = frappe.get_all(
        "Employee Checkin",
        fields=[
            "employee", "time", "log_type", "employee_name",
            "log_location", "attendance_image"
        ],
        filters=build_filters(filters),
        order_by="employee, time"
    )

    data = []
    last_in = {}

    for c in checkins:

        # IN punch
        if c.log_type == "IN":
            last_in[c.employee] = c

        # OUT punch
        elif c.log_type == "OUT" and c.employee in last_in:

            in_log = last_in[c.employee]

            duration = None
            if in_log.time and c.time:
                duration = c.time - in_log.time

            # Fetch activities within the time window
            activities = get_employee_activities(
                c.employee,
                in_log.time,
                c.time
            )

            # No activity → blank row
            if not activities:
                data.append(base_row(in_log, c, duration))
            else:
                for act in activities:
                    row = base_row(in_log, c, duration)
                    row.update(act)
                    data.append(row)

            # Clear IN log
            del last_in[c.employee]

    return data



def base_row(in_log, out_log, duration):
	"""Base row for IN/OUT block."""
	return {
		"employee": in_log.employee,
		"employee_name":in_log.employee_name,
		"in_time": in_log.time,
		"out_time": out_log.time,
		"duration": duration,

		"in_location": in_log.log_location,
		"out_location": out_log.log_location,

		"in_image": in_log.attendance_image,
		"out_image": out_log.attendance_image,
	}


def get_employee_activities(employee, start, end):
	"""Fetch SO, Quotation, ToDo activity using employee's user_id."""
	activities = []

	# Fetch employee → user_id
	user_id = frappe.db.get_value("Employee", employee, "user_id")

	if not user_id:
		return activities

	# -----------------------------------
	# SALES ORDER (owner OR modified_by)
	# -----------------------------------
	sos = frappe.get_all(
		"Sales Order",
		filters={
			"modified": ["between", [start, end]],
			"owner": ["in", [user_id]],
		},
		fields=["name", "customer", "status","workflow_state"]
	)

	sos_modified = frappe.get_all(
		"Sales Order",
		filters={
			"modified": ["between", [start, end]],
			"modified_by": ["in", [user_id]],
		},
		fields=["name", "customer", "status","workflow_state"]
	)

	# Merge without duplicate names
	so_list = {x.name: x for x in sos}
	for x in sos_modified:
		so_list[x.name] = x

	for so in so_list.values():
		activities.append({
			"activity_type": "Sales Order",
			"reference": so.name,
			"detail": f"{so.customer} ({so.status}) ({so.workflow_state})"
		})

	# -----------------------------------
	# QUOTATION (owner OR modified_by)
	# -----------------------------------
	quotations = frappe.get_all(
		"Quotation",
		filters={
			"modified": ["between", [start, end]],
			"owner": ["in", [user_id]],
		},
		fields=["name", "customer_name", "status"]
	)

	quotations_modified = frappe.get_all(
		"Quotation",
		filters={
			"modified": ["between", [start, end]],
			"modified_by": ["in", [user_id]],
		},
		fields=["name", "customer_name", "status"]
	)

	# Merge without duplicates
	q_list = {x.name: x for x in quotations}
	for x in quotations_modified:
		q_list[x.name] = x

	for q in q_list.values():
		activities.append({
			"activity_type": "Quotation",
			"reference": q.name,
			"detail": f"{q.customer_name} ({q.status})" 
		})

	# -----------------------------------
	# TODO (only modified_by)
	# -----------------------------------
	todos = frappe.get_all(
		"ToDo",
		filters={
			"modified_by": user_id,
			"modified": ["between", [start, end]]
		},
		fields=["name", "description", "status"]
	)
	for td in todos:
		activities.append({
			"activity_type": "ToDo",
			"reference": td.name,
			"detail": f"{(td.description or '')[:80]}... ({td.status})"
		})

	return activities


def build_filters(filters):
	"""
	Build filters for Employee Checkin query.
	Accepts filters dict with optional keys:
	- employee (Employee name)
	- from_date (Date string 'YYYY-MM-DD' or Date object)
	- to_date   (Date string 'YYYY-MM-DD' or Date object)
	"""
	f = {}

	if not filters:
		return f

	# Employee filter (exact match)
	if filters.get("employee"):
		f["employee"] = filters.get("employee")

	# Date / datetime range for 'time' field
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	if from_date and to_date:
		# include whole to_date day by setting time to 23:59:59
		start = "{} 00:00:00".format(getdate(from_date))
		end = "{} 23:59:59".format(getdate(to_date))
		f["time"] = ["between", [start, end]]

	elif from_date:
		start = "{} 00:00:00".format(getdate(from_date))
		f["time"] = [">=", start]

	elif to_date:
		end = "{} 23:59:59".format(getdate(to_date))
		f["time"] = ["<=", end]

	return f
