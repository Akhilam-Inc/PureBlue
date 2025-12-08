import frappe
from frappe.utils import today

def validate(doc, method):
    """Todo Checkin Validation in Single Validate Event"""

    # Only run when ToDo is being closed
    if doc.status != "Closed":
        return

    # Get employee of current user
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        return  # Skip if no employee linked

    # Find today's last check-in/out log
    last_log = frappe.db.get_value(
        "Employee Checkin",
        filters={
            "employee": employee,
            "time": ["between", (today() + " 00:00:00", today() + " 23:59:59")]
        },
        fieldname="log_type",
        order_by="time desc"
    )

    # 1️⃣ No check-in today → Ask to create check-in
    if not last_log:
        frappe.throw("❗ No Check-In found for today.<br>Please Check-In first to close this ToDo.")

    # 2️⃣ Last record is OUT → Ask to create check-in
    if last_log == "OUT":
        frappe.throw("❗ You are currently Checked-Out.<br>Please Check-In first to close this ToDo.")

    # 3️⃣ Last log is IN → allow closing
    # After allowing user to close ToDo → Ask manually to Checkout
    frappe.msgprint(
        "✔ ToDo closed successfully.<br><b>Please Checkout now.</b>",
        indicator="blue"
    )


