# Copyright (c) 2025, Akhilam Inc. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Incident(Document):
	pass


@frappe.whitelist()
def get_permission_query_conditions_for_incident(user):
	# System Manager → no restriction
	# if "System Manager" in frappe.get_roles(user):
	# 	return None

	roles = frappe.get_roles(user)

	conditions = []

	# HR users can see only non-confidential records
	if "HR User" in roles or "HR Manager" in roles:
		conditions.append("`tabIncident`.is_confidential = 0")

	if conditions:
		return " AND ".join(conditions)

	return None
