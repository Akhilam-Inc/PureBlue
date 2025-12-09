import frappe
from frappe.utils import today

def before_validate(self,method):
    # Skip validation for system managers
    if frappe.session.user in frappe.permissions.get_roles(frappe.session.user):
        if "System Manager" in frappe.permissions.get_roles(frappe.session.user):
            return
    
    user = frappe.session.user
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if not employee:
        return  # Skip if no employee mapping

    last_log = frappe.db.get_value(
        "Employee Checkin",
        filters={
            "employee": employee,
            "time": ["between", (today() + " 00:00:00", today() + " 23:59:59")]
        },
        fieldname="log_type",
        order_by="time desc"
    )

    if not last_log:
        frappe.throw("❗ No Check-In found today.<br>Please Check-In before creating this Quotation.")

    if last_log == "OUT":
        frappe.throw("❗ You are already Checked-Out.<br>Please Check-In before creating this Quotation.")