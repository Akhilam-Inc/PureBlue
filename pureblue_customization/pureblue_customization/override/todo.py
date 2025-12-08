import frappe
from frappe.utils import today

def validate(doc, method):

    if doc.status == "Closed" and doc.has_value_changed("status"):

        # ---- CHECK-IN VALIDATION ----
        employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
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

        # No Check-in today → block closing
        if not last_log:
            frappe.throw("❗ No Check-In found today.<br>Please Check-In before closing this ToDo.")

        # Last log is OUT → block closing
        if last_log == "OUT":
            frappe.throw("❗ You are already Checked-Out.<br>Please Check-In before closing this ToDo.")

        # ---- STATUS CHANGED TO CLOSED → SHOW MESSAGE ----
        frappe.msgprint(
            "✔ ToDo closed successfully.<br><b>You can Checkout from the app now.</b>",
            indicator="blue"
        )
