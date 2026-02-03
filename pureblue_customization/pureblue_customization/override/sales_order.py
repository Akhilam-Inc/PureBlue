import frappe
from frappe.utils import today,getdate
from datetime import timedelta
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice


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
    
    low_stock_warning(self)


def on_submit(self, method):
    try:
        if self.workflow_state == "Approved":
            si = make_sales_invoice(self.name)
            # Set Posting Date
            si.posting_date = today()
            si.due_date = getdate(si.posting_date) + timedelta(days=7)

            si.insert(ignore_permissions=True)

            # Clickable link to Sales Invoice
            link = f'<a href="/app/sales-invoice/{si.name}" target="_blank">{si.name}</a>'

            frappe.msgprint(f"Sales Invoice {link} has been created as Draft.")

    except Exception:
        frappe.log_error(frappe.get_traceback(), f"Error in Sales Order on_submit ({self.name})")
        frappe.throw("Failed to create Sales Invoice. Check error logs.")


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


def low_stock_warning(doc):
    messages = []

    for item in doc.items:
        if not item.item_code or not item.warehouse:
            continue

        actual_qty = frappe.db.get_value(
            "Bin",
            {
                "item_code": item.item_code,
                "warehouse": item.warehouse
            },
            "actual_qty"
        ) or 0

        if item.qty > actual_qty:
            messages.append(
                f"""
                Item Code: {item.item_code}<br>
                Required Quantity: {item.qty}<br>
                Available Quantity: {actual_qty}<br>
                Warehouse: {item.warehouse}
                """
            )

    if messages:
        frappe.throw(
            "The following items do not have sufficient stock to fulfill this Sales Order:<br><br>"
            + "<br><br>".join(messages),
            title="Insufficient Stock"
        )