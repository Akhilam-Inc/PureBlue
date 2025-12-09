import frappe
from frappe.utils import today

def validate(self,method):
    """Validate customer license details before saving the document"""

    if not self.customer:
        return

    cust = frappe.get_doc("Customer", self.customer)

    missing = []

    if not cust.custom_drug_license:
        missing.append("Drug License Type")

    if not cust.custom_license_no:
        missing.append("License Number")

    if not cust.custom_license_expiry_date:
        missing.append("License Expiry Date")
    else:
        if str(cust.custom_license_expiry_date) <= today():
            missing.append("License Expired")

    # If something missing → Block save
    if missing:
        message = (
            "Customer <b>{0}</b> has incomplete or expired license information:<br><br>"
            "<ul>{1}</ul>"
            "<br>Please update the customer's license details before saving."
        ).format(
            self.customer,
            "".join([f"<li>{m}</li>" for m in missing])
        )

        frappe.throw(message, title="License Validation Error")


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
        frappe.throw("❗ No Check-In found today.<br>Please Check-In before creating this Sales Order.")

    if last_log == "OUT":
        frappe.throw("❗ You are already Checked-Out.<br>Please Check-In before creating this Sales Order.")