import frappe
from frappe.utils import today

def validate(doc, method):

    # only when status CHANGED to Closed
    if doc.status == "Closed" and doc.has_value_changed("status"):

        # employee check-in logic
        employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
        if not employee:
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
            frappe.throw("❗ No Check-In found today.<br>Please Check-In first before closing this ToDo.")

        if last_log == "OUT":
            frappe.throw("❗ You are already Checked-Out.<br>Please Check-In first before closing this ToDo.")

        # ✔ Show alert instead of msgprint
        frappe.show_alert({
            "message": "✔ ToDo closed successfully.<br><b>You can Checkout from the app now.</b>",
            "indicator": "blue"
        })

