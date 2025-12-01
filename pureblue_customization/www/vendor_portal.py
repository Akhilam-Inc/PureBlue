import frappe
from frappe import _

def get_context(context):
    context.title = "Vendor Registration"
    context.no_cache = 1
    return context


@frappe.whitelist(allow_guest=True)
def create_supplier(data):
    """Create Supplier record from public vendor registration form"""
    import json
    data = json.loads(data)

    # Basic validation
    if not data.get("supplier_name"):
        frappe.throw(_("Supplier Name is required"))
    if not data.get("email"):
        frappe.throw(_("Email is required"))

    # Check duplicate
    if frappe.db.exists("Supplier", {"supplier_name": data["supplier_name"]}):
        frappe.throw(_("Supplier with this name already exists."))

    try:
        # Handle file upload (save temporarily)
        file_url = None
        if frappe.request.files:
            file = frappe.request.files.get("file")
            if file:
                # Save file unattached first
                file_url = save_uploaded_file(file)

        # Create Supplier
        supplier = frappe.get_doc({
            "doctype": "Supplier",
            "supplier_name": data["supplier_name"],
            "supplier_group": data.get("supplier_group") or "All Supplier Groups",
            "supplier_type": data.get("supplier_type") or "Company",
            "tax_id": data.get("tax_id"),
            "website": data.get("website"),
        })

        # Add custom fields if they exist in Supplier doctype
        if data.get("licence_no"):
            supplier.licence_no = data.get("licence_no")
        if data.get("licence_expiry"):
            supplier.licence_expiry = data.get("licence_expiry")

        supplier.insert(ignore_permissions=True)

        # Attach file to Supplier if uploaded
        if file_url:
            attach_file_to_doc("Supplier", supplier.name, file_url)

        # Create Contact for email and mobile
        if data.get("email") or data.get("mobile") or data.get("phone"):
            create_contact(supplier.name, data)

        # Create Address if provided
        address_data = data.get("address", {})
        if address_data.get("address_line1") or address_data.get("city"):
            create_address(supplier.name, address_data)

        # Create Bank Account if provided
        bank_data = data.get("bank_details", {})
        if bank_data.get("bank_name") or bank_data.get("bank_account_no"):
            create_bank_account(supplier.name, bank_data, data.get("supplier_name"))

        frappe.db.commit()

        return {
            "message": "Supplier registered successfully! We will contact you soon.",
            "supplier_name": supplier.name
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), _("Supplier Registration Error"))
        frappe.throw(_("An error occurred while registering. Please try again or contact support."))


def create_address(supplier_name, address_data):
    """Create Address record for supplier"""
    if not address_data:
        return

    try:
        address = frappe.get_doc({
            "doctype": "Address",
            "address_title": supplier_name,
            "address_type": "Billing",
            "address_line1": address_data.get("address_line1"),
            "address_line2": address_data.get("address_line2"),
            "city": address_data.get("city"),
            "state": address_data.get("state"),
            "pincode": address_data.get("pincode"),
            "country": address_data.get("country") or "India",
            "links": [{
                "link_doctype": "Supplier",
                "link_name": supplier_name
            }]
        })
        address.insert(ignore_permissions=True)
        return address.name
    except Exception:
        frappe.log_error(frappe.get_traceback(), _("Address Creation Error"))


def create_contact(supplier_name, data):
    """Create Contact record for supplier with email and phone details"""
    try:
        contact = frappe.get_doc({
            "doctype": "Contact",
            "first_name": data.get("supplier_name"),
            "status": "Passive",
            "links": [{
                "link_doctype": "Supplier",
                "link_name": supplier_name
            }]
        })

        if data.get("email"):
            contact.append("email_ids", {
                "email_id": data.get("email"),
                "is_primary": 1
            })

        if data.get("mobile"):
            contact.append("phone_nos", {
                "phone": data.get("mobile"),
                "is_primary_mobile_no": 1
            })

        if data.get("phone"):
            contact.append("phone_nos", {
                "phone": data.get("phone"),
                "is_primary_phone": 1 if not data.get("mobile") else 0
            })

        contact.insert(ignore_permissions=True)
        return contact.name
    except Exception:
        frappe.log_error(frappe.get_traceback(), _("Contact Creation Error"))


def create_bank_account(supplier_name, bank_data, supplier_display_name):
    """Create Bank Account record for supplier"""
    if not bank_data or not bank_data.get("bank_account_no"):
        return

    try:
        bank_name = bank_data.get("bank_name")
        account_type = bank_data.get("bank_account_type")

        if bank_name and not frappe.db.exists("Bank", bank_name):
            bank = frappe.get_doc({
                "doctype": "Bank",
                "bank_name": bank_name
            })
            bank.insert(ignore_permissions=True)
            frappe.db.commit()

        if account_type and not frappe.db.exists("Bank Account Type", account_type):
            bank_acc_type = frappe.get_doc({
                "doctype": "Bank Account Type",
                "account_type": account_type
            })
            bank_acc_type.insert(ignore_permissions=True)
            frappe.db.commit()

        bank_account = frappe.get_doc({
            "doctype": "Bank Account",
            "account_name": f"{supplier_display_name} - {bank_name or 'Bank'}",
            "bank": bank_name,
            "bank_account_no": bank_data.get("bank_account_no"),
            "branch_code": bank_data.get("ifsc_code"),
            "branch": bank_data.get("branch_name"),
            "account_type": account_type,
            "party_type": "Supplier",
            "party": supplier_name
        })
        bank_account.insert(ignore_permissions=True)
        return bank_account.name
    except Exception:
        frappe.log_error(frappe.get_traceback(), _("Bank Account Creation Error"))


def save_uploaded_file(file):
    """Save uploaded file temporarily (unattached) and return file URL"""
    try:
        from frappe.utils.file_manager import save_file

        file_content = file.read()
        filename = file.filename

        # Save file temporarily (unattached)
        file_doc = save_file(
            fname=filename,
            content=file_content,
            dt=None,
            dn=None,
            is_private=1
        )

        return file_doc.file_url
    except Exception:
        frappe.log_error(frappe.get_traceback(), _("File Upload Error"))
        return None


def attach_file_to_doc(doctype, docname, file_url):
    """Attach previously uploaded file to a document"""
    try:
        file_name = frappe.db.get_value("File", {"file_url": file_url}, "name")
        if file_name:
            file_doc = frappe.get_doc("File", file_name)
            file_doc.attached_to_doctype = doctype
            file_doc.attached_to_name = docname
            file_doc.save(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), _("File Attachment Error"))
