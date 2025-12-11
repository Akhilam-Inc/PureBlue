# Copyright (c) 2025, Akhilam Inc. and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "Sales Person", "fieldname": "sales_person", "fieldtype": "Data", "width": 180},
        {"label": "Total Assigned Lead", "fieldname": "total_assigned", "fieldtype": "Int", "width": 150},
        {"label": "Visited Lead", "fieldname": "visited_lead", "fieldtype": "Int", "width": 150},
        {"label": "Converted Lead", "fieldname": "converted_lead", "fieldtype": "Int", "width": 150},
        {"label": "Lost Lead", "fieldname": "lost_lead", "fieldtype": "Int", "width": 150},
        {"label": "Conversion Rate %", "fieldname": "conversion_rate", "fieldtype": "Data", "width": 150},
    ]



def get_data(filters):
    sales_person = filters.get("sales_person")

    conditions = ""
    values = {}

    # Apply sales person filter only if selected
    if sales_person:
        conditions += "WHERE custom_assigned_to_person = %(sales_person)s"
        values["sales_person"] = sales_person

    query = f"""
        SELECT
            custom_assigned_to_person AS sales_person,
            COUNT(name) AS total_assigned,

            -- Count status = Visited
            SUM(CASE WHEN status = 'Visited' THEN 1 ELSE 0 END) AS visited_lead,

            -- Count status = Converted
            SUM(CASE WHEN status = 'Converted' THEN 1 ELSE 0 END) AS converted_lead,

            -- Count status = Lost
            SUM(CASE WHEN status = 'Lost Quotation' THEN 1 ELSE 0 END) AS lost_lead

        FROM `tabLead`
        {conditions}
        GROUP BY custom_assigned_to_person
    """

    data = frappe.db.sql(query, values, as_dict=1)

    # Calculate conversion %
    for row in data:
        if row.total_assigned > 0:
            row.conversion_rate = f"{(row.converted_lead / row.total_assigned) * 100:.2f}%"
        else:
            row.conversion_rate = "0%"

    return data

    sales_person = filters.get("sales_person")

    data = frappe.db.sql("""
        SELECT
            custom_assigned_to_person AS sales_person,
            COUNT(name) AS total_assigned,

            -- Count status = Visited
            SUM(CASE WHEN status = 'Visited' THEN 1 ELSE 0 END) AS visited_lead,

            -- Count status = Converted
            SUM(CASE WHEN status = 'Converted' THEN 1 ELSE 0 END) AS converted_lead,

            -- Count status = Lost
            SUM(CASE WHEN status = 'Lost Quotation' THEN 1 ELSE 0 END) AS lost_lead

        FROM `tabLead`
        GROUP BY custom_assigned_to_person
    """, {}, as_dict=1)

    # Calculate conversion %
    for row in data:
        if row.total_assigned > 0:
            row.conversion_rate = f"{(row.converted_lead / row.total_assigned) * 100:.2f}%"
        else:
            row.conversion_rate = "0%"

    return data

