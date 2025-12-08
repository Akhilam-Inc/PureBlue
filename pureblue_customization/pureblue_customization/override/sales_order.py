import frappe
from frappe.utils import today

def validate(self):
    """Validate customer license details before saving the document"""

    if not self.customer:
        return

    cust = frappe.get_doc("Customer", self.customer)

    missing = []

    if not cust.custom_drug_license_:
        missing.append("• Drug License Type")

    if not cust.custom_license_no:
        missing.append("• License Number")

    if not cust.custom_license_expiry:
        missing.append("• License Expiry Date")
    else:
        if cust.custom_license_expiry <= today():
            missing.append("• License Expired")

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
