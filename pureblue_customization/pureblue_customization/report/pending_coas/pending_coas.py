# Copyright (c) 2025, Akhilam Inc. and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    filters = filters or {}

    # Ensure key always exists (this fixes KeyError forever)
    item = filters.get("item")

    columns = [
        {
            "label": "Batch No",
            "fieldname": "batch_no",
            "fieldtype": "Link",
            "options": "Batch",
            "width": 120
        },
        {
            "label": "Item",
            "fieldname": "item",
            "fieldtype": "Link",
            "options": "Item",
            "width": 150
        },
        {
            "label": "Item Name",
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 200
        }
    ]

    query = """
        SELECT
            name AS batch_no,
            item,
            item_name
        FROM
            `tabBatch`
        WHERE
            custom_is_coa_completed = 0
    """

    # Apply filter only if item is selected
    if item:
        query += " AND item = %(item)s"

    data = frappe.db.sql(query, {"item": item}, as_dict=True)

    return columns, data
