
import frappe
from frappe import _


@frappe.whitelist()
def send_brochure_email(doc_name, doctype_name,email_to):
    """Send brochure email to customer with fixed logo and responsive layout"""
    try:
        doc = frappe.get_doc(doctype_name, doc_name)
        recipient_email = email_to

        if not recipient_email:
            frappe.throw(_("Email address not found for this contact"))

        customer_name = doc.first_name + " " + doc.last_name if doc.last_name else doc.first_name or "Sir/Madam"

        context = {
            "company_name": "Pure Blue Meds Pvt Ltd",
            "tagline": "Premium IV Fluids • Sterile Filling • Global Compliance",
            "customer_name": customer_name,
            "logo_img": frappe.utils.get_url("/files/pureblue-meds-logo.png"),
            "customer_registration_url": frappe.utils.get_url("/customer_registration"),
            "year": frappe.utils.nowdate()[:4],
        }

        html_content = frappe.render_template(
            "pureblue_customization/templates/emails/brochure.html",
            context
        )

        frappe.sendmail(
            recipients=[recipient_email],
            subject="Introducing Pure Blue Meds - Premium IV Fluid Solutions",
            message=html_content,
            now=True,
            header=["Pure Blue Meds Pvt Ltd", "blue"]
        )

        frappe.msgprint(_("Brochure email sent successfully to {0}").format(recipient_email), indicator="green")
        doc.add_comment("Comment", f"Brochure email sent to {recipient_email}")

        return {"success": True, "message": f"Email sent successfully to {recipient_email}"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Pure Blue Brochure Email Error")
        frappe.throw(_("Failed to send email: {0}").format(str(e)))
