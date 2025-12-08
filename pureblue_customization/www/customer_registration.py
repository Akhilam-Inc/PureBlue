import frappe
from frappe import _
from frappe.utils import getdate
import re

def get_context(context):
    context.title = "Customer Registration"
    context.no_cache = 1
    return context


@frappe.whitelist(allow_guest=True)
def create_customer(data):
    try:
        if not data:
            return {"success": False, "message": "No data provided"}

        data = frappe.parse_json(data)

        # Comprehensive validation
        validation_result = validate_customer_data(data)
        if not validation_result["valid"]:
            return {
                "success": False,
                "message": validation_result["message"],
                "field": validation_result.get("field")
            }

        # Check for duplicates
        duplicate_check = check_duplicates(data)
        if not duplicate_check["valid"]:
            return {
                "success": False,
                "message": duplicate_check["message"],
                "field": duplicate_check.get("field")
            }

        # Validate file
        file = None
        if frappe.request.files:
            file = frappe.request.files.get("file")
        
        if not file:
            return {
                "success": False,
                "message": "Drug License document is required. Please upload a valid document.",
                "field": "document_file"
            }

        # Validate file type and size
        file_validation = validate_file(file)
        if not file_validation["valid"]:
            return {
                "success": False,
                "message": file_validation["message"],
                "field": "document_file"
            }

        # Create Customer
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": data["customer_name"],
            "customer_group": data.get("customer_group") or "All Customer Groups",
            "customer_type": data.get("customer_type") or "Individual",
            "gstin": data.get("tax_id"),
            "tax_id": data.get("tax_id"),
            "website": data.get("website"),
            "custom_licence_no": data.get("licence_no"),
            "custom_licence_expiry": frappe.utils.getdate(data.get("licence_expiry"))
        })

        customer.insert(ignore_permissions=True)

        # Address
        address_data = data.get("address", {})
        if address_data.get("address_line1") or address_data.get("city"):
            create_address(customer.name, address_data)

        # Contact
        if data.get("email") or data.get("mobile") or data.get("phone"):
            create_contact(customer.name, data)

        # Bank Account
        bank_data = data.get("bank_details", {})
        if bank_data.get("bank_account_no"):
            bank_validation = validate_bank_details(bank_data)
            if not bank_validation["valid"]:
                # Rollback customer creation
                frappe.delete_doc("Customer", customer.name, ignore_permissions=True)
                return {
                    "success": False,
                    "message": bank_validation["message"],
                    "field": bank_validation.get("field")
                }
            create_bank_account(customer.name, bank_data, data["customer_name"])

        # File Attachment
        file_url = save_uploaded_file(file)
        if file_url:
            attach_file_to_doc("Customer", customer.name, file_url)
            frappe.db.set_value("Customer", customer.name, "custom_drug_license_", file_url)

        frappe.db.commit()

        return {
            "success": True,
            "message": "Customer registered successfully! We will contact you soon.",
            "customer_name": customer.name
        }

    except Exception as e:
        frappe.db.rollback()
        log_error_with_data(
            title=f"Customer Registration Error - {data.get('customer_name', 'Unknown')}",
            data=data
        )
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }


def validate_customer_data(data):
    """Comprehensive validation of customer data"""
    
    # Required fields validation
    if not data.get("customer_name") or not data["customer_name"].strip():
        return {"valid": False, "message": "Customer Name is required", "field": "customer_name"}
    
    if len(data["customer_name"].strip()) < 3:
        return {"valid": False, "message": "Customer Name must be at least 3 characters", "field": "customer_name"}

    # Email validation
    email = data.get("email", "").strip()
    if not email:
        return {"valid": False, "message": "Email is required", "field": "email"}
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return {"valid": False, "message": "Please enter a valid email address", "field": "email"}

    # Tax ID/GSTIN validation
    tax_id = data.get("tax_id", "").strip()
    if tax_id:
        if len(tax_id) != 15:
            return {"valid": False, "message": "Tax ID/GSTIN must be exactly 15 characters", "field": "tax_id"}
        
        gstin_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        if not re.match(gstin_pattern, tax_id.upper()):
            return {"valid": False, "message": "Invalid GSTIN format. Example: 27ABCDE1234F1Z5", "field": "tax_id"}

    # Licence validation
    if not data.get("licence_no") or not data["licence_no"].strip():
        return {"valid": False, "message": "Licence Number is required", "field": "licence_no"}

    if not data.get("licence_expiry"):
        return {"valid": False, "message": "Licence Expiry Date is required", "field": "licence_expiry"}

    # Check if licence is expired
    try:
        licence_expiry = getdate(data["licence_expiry"])
        if licence_expiry < getdate():
            return {"valid": False, "message": "Licence has already expired. Please renew before registration.", "field": "licence_expiry"}
    except Exception:
        return {"valid": False, "message": "Invalid date format for Licence Expiry", "field": "licence_expiry"}

    # Phone validation (if provided)
    mobile = data.get("mobile", "").strip()
    if mobile:
        # Remove common separators
        mobile_clean = re.sub(r'[\s\-\(\)\+]', '', mobile)
        if not mobile_clean.isdigit() or len(mobile_clean) < 10:
            return {"valid": False, "message": "Mobile number must contain at least 10 digits", "field": "mobile"}

    # Pincode validation (if provided)
    pincode = data.get("address", {}).get("pincode", "").strip()
    if pincode and not re.match(r'^\d{6}$', pincode):
        return {"valid": False, "message": "PIN Code must be exactly 6 digits", "field": "pincode"}

    return {"valid": True}


def check_duplicates(data):
    """Check for duplicate records"""
    
    # Check customer name
    if frappe.db.exists("Customer", {"customer_name": data["customer_name"]}):
        return {
            "valid": False,
            "message": f"Customer '{data['customer_name']}' already exists. Please use a different name.",
            "field": "customer_name"
        }

    # Check email
    email = data.get("email", "").strip()
    if email:
        existing_contact = frappe.db.sql("""
            SELECT c.name, cl.link_name 
            FROM `tabContact` c
            JOIN `tabContact Email` ce ON ce.parent = c.name
            JOIN `tabDynamic Link` cl ON cl.parent = c.name
            WHERE ce.email_id = %s 
            AND cl.link_doctype = 'Customer'
            LIMIT 1
        """, (email,), as_dict=True)
        
        if existing_contact:
            return {
                "valid": False,
                "message": f"Email '{email}' is already registered with another customer.",
                "field": "email"
            }

    # Check Tax ID/GSTIN
    tax_id = data.get("tax_id", "").strip()
    if tax_id:
        if frappe.db.exists("Customer", {"tax_id": tax_id}):
            return {
                "valid": False,
                "message": f"Tax ID '{tax_id}' is already registered.",
                "field": "tax_id"
            }

    # Check Licence Number
    licence_no = data.get("licence_no", "").strip()
    if licence_no:
        if frappe.db.exists("Customer", {"custom_licence_no": licence_no}):
            return {
                "valid": False,
                "message": f"Licence Number '{licence_no}' is already registered.",
                "field": "licence_no"
            }

    return {"valid": True}


def validate_file(file):
    """Validate uploaded file"""
    if not file:
        return {"valid": False, "message": "No file uploaded"}

    # Check file size (5MB max)
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > 5 * 1024 * 1024:
        return {"valid": False, "message": "File size must not exceed 5MB"}

    # Check file extension
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
    filename = file.filename.lower()
    
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        return {
            "valid": False,
            "message": "Invalid file format. Allowed: PDF, JPG, PNG, DOC, DOCX"
        }

    return {"valid": True}


def validate_bank_details(bank_data):
    """Validate bank account details"""
    
    account_no = bank_data.get("bank_account_no", "").strip()
    if account_no:
        # Remove spaces
        account_no_clean = account_no.replace(" ", "")
        if not account_no_clean.isdigit():
            return {
                "valid": False,
                "message": "Bank Account Number must contain only digits",
                "field": "bank_account_no"
            }
        
        if len(account_no_clean) < 9 or len(account_no_clean) > 18:
            return {
                "valid": False,
                "message": "Bank Account Number must be between 9 and 18 digits",
                "field": "bank_account_no"
            }

    # IFSC Code validation
    ifsc = bank_data.get("ifsc_code", "").strip()
    if ifsc:
        ifsc_pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
        if not re.match(ifsc_pattern, ifsc.upper()):
            return {
                "valid": False,
                "message": "Invalid IFSC Code format. Example: HDFC0001234",
                "field": "ifsc_code"
            }

    return {"valid": True}


def create_address(customer_name, address_data):
    """Create Address linked to Customer"""
    if not address_data:
        return

    try:
        state = (address_data.get("state") or "").strip()
        if state:
            state = state[0].upper() + state[1:]

        address = frappe.get_doc({
            "doctype": "Address",
            "address_title": customer_name,
            "address_type": "Billing",
            "address_line1": address_data.get("address_line1"),
            "address_line2": address_data.get("address_line2"),
            "city": address_data.get("city"),
            "state": state,
            "pincode": address_data.get("pincode"),
            "country": address_data.get("country") or "India",
            "links": [{
                "link_doctype": "Customer",
                "link_name": customer_name
            }]
        })
        address.insert(ignore_permissions=True)
        return address.name
    except Exception:
        frappe.log_error(frappe.get_traceback(), _("Address Creation Error"))


def create_contact(customer_name, data):
    """Create Contact linked to Customer"""
    try:
        contact = frappe.get_doc({
            "doctype": "Contact",
            "first_name": data.get("customer_name"),
            "status": "Passive",
            "links": [{
                "link_doctype": "Customer",
                "link_name": customer_name
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


def create_bank_account(customer_name, bank_data, customer_display_name):
    try:
        bank_name = bank_data.get("bank_name")
        account_type = bank_data.get("bank_account_type") or "Savings"

        bank_account = frappe.get_doc({
            "doctype": "Bank Account",
            "account_name": bank_data.get("account_holder_name") or customer_display_name,
            "bank": bank_name,
            "bank_account_no": bank_data.get("bank_account_no"),
            "branch_code": bank_data.get("ifsc_code"),
            "branch": bank_data.get("branch_name"),
            "account_type": account_type,
            "party_type": "Customer",
            "party": customer_name
        })
        bank_account.insert(ignore_permissions=True)

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Bank Account Creation Error")


def save_uploaded_file(file):
    """Save uploaded file temporarily and return file URL"""
    try:
        from frappe.utils.file_manager import save_file

        file_content = file.read()
        filename = file.filename

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
    """Attach uploaded file to Customer"""
    try:
        file_name = frappe.db.get_value("File", {"file_url": file_url}, "name")
        if file_name:
            file_doc = frappe.get_doc("File", file_name)
            file_doc.attached_to_doctype = doctype
            file_doc.attached_to_name = docname
            file_doc.attached_to_field = "custom_drug_license_"
            file_doc.save(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), _("File Attachment Error"))


@frappe.whitelist(allow_guest=True)
def get_customer_groups():
    """Return Customer Groups for guest"""
    rows = frappe.db.sql("SELECT `name` FROM `tabCustomer Group` ORDER BY `name`", as_list=True)
    return [r[0] for r in rows]


@frappe.whitelist(allow_guest=True)
def get_banks():
    """Return Banks for guest"""
    rows = frappe.db.sql("SELECT `name` FROM `tabBank` ORDER BY `name`", as_list=True)
    return [r[0] for r in rows]


def log_error_with_data(title, data):
    try:
        frappe.log_error(
            message=frappe.as_json({
                "incoming_data": data,
                "traceback": frappe.get_traceback()
            }, indent=2),
            title=title
        )
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Error Logging Failed")