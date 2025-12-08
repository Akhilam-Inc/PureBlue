import frappe
from frappe.utils import today, now_datetime

def validate_todo(doc, method):
    """Validate employee check-in/out when closing a ToDo."""

    # Only run when user closes the todo
    if doc.status != "Closed":
        return

    # Identify employee from current user
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        return  # No employee mapping → skip validation

    # Get today's last check-in/out log
    last_log = frappe.db.get_value(
        "Employee Checkin",
        filters={
            "employee": employee,
            "time": ["between", (today() + " 00:00:00", today() + " 23:59:59")]
        },
        fieldname=["name", "log_type"],
        order_by="time desc"
    )

    # 1️⃣ No check-in record → Block closing ToDo
    if not last_log:
        frappe.throw("❗ You must <b>Check-in</b> before closing a ToDo.")

    log_name, log_type = last_log

    # 2️⃣ Last log is OUT → Block closing again
    if log_type == "OUT":
        frappe.throw("❗ Your last log is <b>OUT</b>. Please Check-in first before closing a ToDo.")

    # 3️⃣ Last log is IN → Allow closing ToDo and ask for checkout
    # (Use msgprint since validate() cannot do confirm popup)
    create_checkout(employee)

    frappe.msgprint(
        "✔ ToDo closed successfully.<br><b>Checkout entry created automatically.</b>",
        indicator="green"
    )


def create_checkout(employee):
    """Automatically create checkout when ToDo is closed."""
    checkin = frappe.new_doc("Employee Checkin")
    checkin.employee = employee
    checkin.log_type = "OUT"
    checkin.time = now_datetime()
    checkin.save(ignore_permissions=True)
