import frappe
from frappe import _

@frappe.whitelist()
def create_todo(lead_name,employee,assign_date):
    lead = frappe.get_doc("Lead", lead_name)
    user = frappe.db.get_value("Employee", employee, "user_id")
    
    # frappe.msgprint(f"Creating ToDo for lead: {lead.lead_name}")
    if not user:
        frappe.throw("Selected employee does not have a linked User.")
    else:
        Description = (
        f"Visit {lead.name} \n"
        f"Email: {lead.email_id}\n"
        f"Phone: {lead.mobile_no}\n"
        f"Industry: {lead.industry}"
        )
        todo = frappe.get_doc({
        "doctype": "ToDo",
        "description": Description,
        "reference_type": "Lead",
        "reference_name": lead.name,
        "allocated_to": user,
        "assigned_by": frappe.session.user
    })
    todo.insert()
    frappe.msgprint(f"ToDo created for {lead.name}")
    return todo.name


@frappe.whitelist()
def send_brochure_email(doc_name, doctype_name):
    """Send brochure email to customer"""
    try:
        # Get the document
        doc = frappe.get_doc(doctype_name, doc_name)
        
        # Get recipient email (adjust field name as per your DocType)
        recipient_email = doc.email_id or doc.email or doc.contact_email
        
        if not recipient_email:
            frappe.throw(_("Email address not found for this contact"))
        
        # Get customer name
        customer_name = doc.lead_name or "Sir/Madam"
        doc.db_set("custom_brochure_sent" ,True)

        customer_registration_url = frappe.utils.get_url("/customer_registration")
        
        # HTML Email Content
        html_content = f"""<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Pure Blue Meds Pvt Ltd</title>
                <style>
                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }}
                    body {{
                        font-family: "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI",
                                    Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue",
                                    sans-serif;
                        font-weight: 400;
                        background-color: #f5f5f5;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        background-color: #083278;
                        padding: 20px;
                        display: flex;
                        align-items: center;
                        gap: 15px;
                    }}
                    .logo {{
                        background-color: white;
                        padding: 10px;
                        border-radius: 5px;
                        width: 60px;
                        height: 60px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }}
                    .logo-text {{
                        color: #083278;
                        font-size: 10px;
                        font-weight: bold;
                        text-align: center;
                        line-height: 1.2;
                    }}
                    .header-content h1 {{
                        color: white;
                        font-size: 24px;
                        margin-bottom: 5px;
                    }}
                    .header-content p {{
                        color: white;
                        font-size: 12px;
                    }}
                    .content {{
                        padding: 30px;
                    }}
                    .greeting {{
                        color: #333;
                        margin-bottom: 20px;
                        line-height: 1.6;
                    }}
                    h2 {{
                        color: #083278;
                        font-size: 18px;
                        margin: 25px 0 15px 0;
                    }}
                    .about-text {{
                        color: #666;
                        line-height: 1.6;
                        margin-bottom: 20px;
                    }}
                    .portfolio-grid {{
                        display: flex;
                        gap: 10px;
                        margin-bottom: 20px;
                    }}
                    .portfolio-column {{
                        flex: 1;
                    }}
                    .portfolio-column h3 {{
                        color: #083278;
                        font-size: 14px;
                        margin-bottom: 10px;
                    }}
                    .portfolio-column p {{
                        color: #666;
                        font-size: 12px;
                        line-height: 1.6;
                    }}
                    .comparison-section {{
                        margin-top: 30px;
                    }}
                    .comparison-grid {{
                        display: flex;
                        gap: 15px;
                        margin-bottom: 15px;
                    }}
                    .comparison-item {{
                        flex: 1;
                    }}
                    .comparison-item h3 {{
                        color: #083278;
                        font-size: 14px;
                        margin-bottom: 8px;
                    }}
                    .comparison-item p {{
                        color: #666;
                        font-size: 12px;
                        line-height: 1.5;
                    }}
                    .tagline {{
                        color: #666;
                        font-style: italic;
                        margin: 20px 0;
                        text-align: center;
                    }}
                    .button-container {{
                        text-align: center; 
                        margin: 20px 0;
                    }}

                    .button-container .button {{
                        display: inline-block; 
                        color: #ffffff !important;
                        text-decoration: none;
                        padding: 10px 20px;
                        border-radius: 4px;
                        margin: 0 20px;   /* acts as gap */
                        font-size: 14px;
                    }}
                    .button {{
                        background-color: #083278;
                        color: white;
                        padding: 12px 30px;
                        text-decoration: none;
                        border-radius: 5px;
                        font-size: 14px;
                        display: inline-block;
                    }}
                    .contact-section {{
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #ddd;
                    }}
                    .contact-section h3 {{
                        color: #999;
                        font-size: 14px;
                        margin-bottom: 10px;
                        font-weight: normal;
                    }}
                    .contact-section p {{
                        color: #333;
                        font-size: 14px;
                        line-height: 1.6;
                        margin-bottom: 5px;
                    }}
                    .contact-section a {{
                        color: #083278;
                        text-decoration: none;
                    }}
                    .footer {{
                        background-color: #f9f9f9;
                        padding: 15px;
                        text-align: center;
                        color: #999;
                        font-size: 12px;
                    }}
                    .footer a {{
                        color: #083278;
                        text-decoration: none;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">
                            <div class="logo-text">
                                <img src="{ frappe.utils.get_url('/files/pureblue-meds-logo.png') }">
                            </div>
                        </div>
                        <div class="header-content">
                            <h1>Pure Blue Meds Pvt Ltd</h1>
                            <p>Premium IV Fluids • Sterile Filling • Global Compliance</p>
                        </div>
                    </div>

                    <div class="content">
                        <p class="greeting">
                            Dear {customer_name},
                        </p>

                        <p class="greeting">
                            I'm reaching out to introduce <strong>Pure Blue Meds Pvt Ltd</strong> — a pharmaceutical company focused on high-quality IV fluid manufacturing using advanced ISBM technology and premium closure systems.
                        </p>

                        <h2>About Us</h2>
                        <p class="about-text">
                            We manufacture SlimPort & MediPort IV fluids, supported by validated sterilisation, precision-moulded ports, high clarity bottles and global standard compliance.
                        </p>

                        <h2>Product Portfolio (Highlights)</h2>
                        <div class="portfolio-grid">
                            <div class="portfolio-column">
                                <h3>Common IV Fluids</h3>
                                <p>NS • DNS • RL • Dextrose • Mannitol • D10 • D25</p>
                            </div>
                            <div class="portfolio-column">
                                <h3>Infusions</h3>
                                <p>Paracetamol • Metronidazole • Ciprofloxacin • Levofloxacin</p>
                            </div>
                            <div class="portfolio-column">
                                <h3>Pack Types</h3>
                                <p>MediPort • SlimPort • FFS</p>
                            </div>
                        </div>

                        <div class="comparison-section">
                            <h2>Why ISBM Is Better Than FFS</h2>
                            
                            <div class="comparison-grid">
                                <div class="comparison-item">
                                    <h3>Superior Material</h3>
                                    <p>High grade PET/PP with lower leachables than FFS film.</p>
                                </div>
                                <div class="comparison-item">
                                    <h3>High Transparency</h3>
                                    <p>Crystal clear bottles allow easy visual inspection.</p>
                                </div>
                                <div class="comparison-item">
                                    <h3>Stronger & Rigid</h3>
                                    <p>Better transport durability & handling strength.</p>
                                </div>
                            </div>

                            <div class="comparison-grid">
                                <div class="comparison-item">
                                    <h3>Precision Ports</h3>
                                    <p>SlimPort / MediPort ensure consistent sealing.</p>
                                </div>
                                <div class="comparison-item">
                                    <h3>Better Sterilisation</h3>
                                    <p>Stable at 121°C vs FFS films which may deform.</p>
                                </div>
                                <div class="comparison-item">
                                    <h3>Hospital Preferred</h3>
                                    <p>Better appearance, safety & reliability.</p>
                                </div>
                            </div>

                            <p class="tagline">
                                <strong>ISBM = safer, stronger, clearer and more reliable than FFS.</strong>
                            </p>
                        </div>

                        <div class="button-container">
                            <a href="{ customer_registration_url }" class="button">Register / Enquiry</a>
                            <a href="https://pureblue.m.erpnext.com/files/Broucher.pdf" class="button">Download Brochure</a>
                        </div>

                        <div class="contact-section">
                            <h3>Contact</h3>
                            <p><strong>Pure Blue Meds Pvt Ltd</strong></p>
                            <p>Palace Cross Road, Vasanth Nagar, Bengaluru, Karnataka</p>
                            <p>+91 99000 33838 • +91 76195 65022 • <a href="mailto:info@pureblue.co.in">info@pureblue.co.in</a></p>
                        </div>
                    </div>

                    <div class="footer">
                        © Pure Blue Meds Pvt Ltd - <a href="http://pureblue.co.in">pureblue.co.in</a>
                    </div>
                </div>
            </body>
            </html>"""
        
        # Send email
        frappe.sendmail(
            recipients=[recipient_email],
            subject="Introducing Pure Blue Meds - Premium IV Fluid Solutions",
            message=html_content,
            now=True,
            header=["Pure Blue Meds Pvt Ltd", "blue"]
        )
        
        # Log the email activity
        frappe.msgprint(_("Brochure email sent successfully to {0}").format(recipient_email), indicator="green")
        
        # Optional: Add a comment to the document
        doc.add_comment("Comment", f"Brochure email sent to {recipient_email}")
        
        return {"success": True, "message": f"Email sent successfully to {recipient_email}"}
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Pure Blue Brochure Email Error")
        frappe.throw(_("Failed to send email: {0}").format(str(e)))