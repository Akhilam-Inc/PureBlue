import frappe
import random
from frappe import _
from frappe.model.workflow import apply_workflow

@frappe.whitelist()
def generate_and_send_otp(reference_doctype, reference_name, contact_email=None, customer=None, mobile_no=None,against_sales_orders=None):
    # -------------------------------
    # 1️⃣ Resolve Email
    # -------------------------------
    email = contact_email

    if not email and customer:
        email = frappe.db.get_value("Customer", customer, "email_id")

    if not email:
        frappe.throw(_("No email found for delivery OTP notification."))

    # -------------------------------
    # 2️⃣ Generate OTP
    # -------------------------------
    otp = str(random.randint(100000, 999999))

    # -------------------------------
    # 3️⃣ Create OTP Code Doc
    # -------------------------------
    frappe.get_doc({
        "doctype": "OTP Code",
        "email": email,
        "mobile_no": mobile_no or "",
        "otp": otp,
        "is_verified": 0,
        "reference_doctype": reference_doctype,
        "reference_name": reference_name
    }).insert(ignore_permissions=True)

    # -------------------------------
    # 4️⃣ Send Email
    # -------------------------------
    frappe.sendmail(
        recipients=[email],
        subject=_("Your Order Is Out for Delivery – OTP Required"),
        template="out_for_delivery_otp",
        args={
            "otp": otp,
            "reference": against_sales_orders or reference_name,
            "company": frappe.defaults.get_global_default("company")
        },
        header=_("Out for Delivery 🚚")
    )

    return {
        "status": "success",
        "email": email
    }


@frappe.whitelist()
def verify_delivery_otp(reference_doctype, reference_name, otp):
    """
    Validate OTP and apply workflow for the given document
    """

    # -------------------------------
    # 1️⃣ Validate OTP
    # -------------------------------
    otp_doc = frappe.db.get_value(
        "OTP Code",
        {
            "reference_doctype": reference_doctype,
            "reference_name": reference_name,
            "otp": otp,
            "is_verified": 0
        },
        "name",
    )

    if not otp_doc:
        frappe.throw(_("Invalid or already used OTP."))

    # -------------------------------
    # 2️⃣ Mark OTP as verified
    # -------------------------------
    frappe.db.set_value("OTP Code", otp_doc, "is_verified", 1)

    # -------------------------------
    # 3️⃣ Apply Workflow
    # -------------------------------
    # -------------------------------
    # 3️⃣ Apply Workflow (SAFE)
    # -------------------------------
    doc = frappe.get_doc(reference_doctype, reference_name)

    apply_workflow(doc, "Mark Delivered")

    return {
        "status": "verified",
        "workflow_applied": "Mark Delivered",
        "document": reference_name
    }



@frappe.whitelist()
def is_delivery_otp_verified(reference_doctype, reference_name):
    return frappe.db.exists(
        "OTP Code",
        {
            "reference_doctype": reference_doctype,
            "reference_name": reference_name,
            "is_verified": 1
        }
    )
