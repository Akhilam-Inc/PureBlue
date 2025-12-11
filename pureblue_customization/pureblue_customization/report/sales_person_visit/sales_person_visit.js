// Copyright (c) 2025, Akhilam Inc. and contributors
// For license information, please see license.txt

frappe.query_reports["Sales Person Visit"] = {
	"filters": [
		{
			fieldname: "sales_person",
            label: __("Sales Person"),
            fieldtype: "Link",
            options: "Sales Person",
			get_query() {
				return {
					filters: {
						name: ["!=", "Sales Team"]   // Remove ONLY Sales Team
					}
				};
			}
		}
	]
};
