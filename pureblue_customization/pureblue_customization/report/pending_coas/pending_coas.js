// Copyright (c) 2025, Akhilam Inc. and contributors
// For license information, please see license.txt

frappe.query_reports["Pending COAs"] = {
    filters: [
        {
            fieldname: "item",
            label: __("Item"),
            fieldtype: "Link",
            options: "Item"
        }
    ]
};

