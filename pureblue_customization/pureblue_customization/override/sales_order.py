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
        missing_list = "<br>".join([f"• {item}" for item in missing])
        message = (
            f"Customer <b>{self.customer}</b> has incomplete or expired license information:<br>"
            f"{missing_list}<br>"
            f"Please update the customer's license details before saving."
        )

        frappe.throw(message, title="License Validation Error")


def before_validate(self, method):

    user = frappe.session.user

    # 1️⃣ Check if user is linked to Employee
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if not employee:
        return

    sales_person = frappe.db.get_value(
        "Sales Person",
        {"employee": employee},
        "name"
    )

    if not sales_person:
        return

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
        frappe.throw("No check-in found today. Please check in before creating a Sales Order.")

    if last_log == "OUT":
        frappe.throw("You are already checked out. Please check in before creating a Sales Order.")

