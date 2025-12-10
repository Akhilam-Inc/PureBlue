import frappe
from frappe.utils import today

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
        frappe.throw("No check-in found today. Please check in before creating a Quotation.")

    if last_log == "OUT":
        frappe.throw("You are already checked out. Please check in before creating a Quotation.")