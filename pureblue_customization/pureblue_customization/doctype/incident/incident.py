# Copyright (c) 2025, Akhilam Inc. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Incident(Document):
	pass

@frappe.whitelist()
def get_permission_query_conditions_for_incident(user):
	roles = frappe.get_roles(user)

	# Full access users
	if "Incident Admin" in roles:
		return None

	# HR users → non-confidential only
	if "HR User" in roles or "HR Manager" in roles:
		return "`tabIncident`.is_confidential = 0"

	return None


