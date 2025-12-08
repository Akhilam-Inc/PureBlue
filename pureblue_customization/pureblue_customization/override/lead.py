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
    """Send brochure email to customer with fixed logo and responsive layout"""
    try:
        doc = frappe.get_doc(doctype_name, doc_name)
        recipient_email = doc.email_id or doc.email or doc.contact_email

        if not recipient_email:
            frappe.throw(_("Email address not found for this contact"))

        customer_name = doc.lead_name or "Sir/Madam"
        doc.db_set("custom_brochure_sent", True)
        customer_registration_url = frappe.utils.get_url("/customer_registration")

        html_content = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Pure Blue Meds Pvt Ltd</title>
            <style>
                /* Reset and Base Styles */
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
                    background-color: #F5F5F5;
                    padding: 10px; /* Reduced from 20px */
                    -webkit-text-size-adjust: 100%;
                    -ms-text-size-adjust: 100%;
                }}
                .container {{
                    width: 100%;
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #FFFFFF;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    border-radius: 8px;
                    overflow: hidden;
                }}
                /* Header Styles */
                .header {{
                    background-color: #083278;
                    padding: 20px;
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    flex-wrap: wrap;
                }}
                .logo {{
                    width: 70px;
                    height: 70px;
                    background-color: white;
                    padding: 5px;
                    border-radius: 5px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    overflow: hidden;
                    flex-shrink: 0;
                }}
                .logo img {{
                    max-width: 100%;
                    max-height: 100%;
                    display: block;
                    object-fit: contain;
                    border: 0;
                }}
                .header-content {{
                    flex: 1;
                }}
                .header-content h1 {{
                    color: white;
                    font-size: 22px;
                    margin-bottom: 5px;
                    line-height: 1.2;
                    margin-top: 0;
                }}
                .header-content p {{
                    color: white;
                    font-size: 12px;
                    opacity: 0.9;
                    line-height: 1.4;
                    margin: 0;
                }}
                /* Content Styles */
                .content {{
                    padding: 20px; /* Reduced from 25px 30px */
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
                /* Table Styles - Desktop Default */
                .portfolio-table, .comparison-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                    background-color: white;
                    border: 1px solid #DEE2E6;
                    table-layout: fixed;
                }}
                .portfolio-table th {{
                    background-color: white;
                    color: #0D3C7D;
                    padding: 15px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: 700;
                    border-bottom: 2px solid #DEE2E6;
                    border-right: 1px solid #DEE2E6;
                }}
                .portfolio-table th:last-child {{
                    border-right: none;
                }}
                .portfolio-table td, .comparison-table td {{
                    padding: 15px;
                    color: #333;
                    font-size: 13px;
                    line-height: 1.6;
                    border-right: 1px solid #DEE2E6;
                    background-color: white;
                    vertical-align: top;
                }}
                .portfolio-table td:last-child, .comparison-table td:last-child {{
                    border-right: none;
                }}
                /* Comparison Section */
                .comparison-section {{
                    margin-top: 25px;
                }}
                .comparison-table td {{
                    border-bottom: 1px solid #DEE2E6;
                    width: 33.33%;
                }}
                .comparison-table tr:last-child td {{
                    border-bottom: none;
                }}
                .comparison-table td strong {{
                    display: block;
                    color: #0D3C7D;
                    font-weight: 700;
                    margin-bottom: 8px;
                    font-size: 14px;
                }}
                .tagline {{
                    color: #666;
                    font-style: italic;
                    margin: 20px 0;
                    text-align: center;
                }}
                /* Buttons */
                .button-container {{
                    text-align: center;
                    margin: 20px 0;
                }}
                .button {{
                    display: inline-block;
                    background-color: #083278;
                    color: #fff !important;
                    text-decoration: none;
                    padding: 12px 25px;
                    border-radius: 5px;
                    margin: 5px;
                    font-size: 14px;
                }}
                /* Contact & Footer */
                .contact-section {{
                    margin-top: 25px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                }}
                .contact-section h3 {{
                    color: #999;
                    font-size: 14px;
                    margin-bottom: 8px;
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
                    background-color: #F9F9F9;
                    padding: 15px;
                    text-align: center;
                    color: #999;
                    font-size: 12px;
                }}
                .footer a {{
                    color: #083278;
                    text-decoration: none;
                }}
                /* MOBILE RESPONSIVENESS FIXES */
                @media only screen and (max-width: 480px) {{
                    /* Body padding reduced to gain width */
                    body {{
                        padding: 5px !important; /* Reduced from 10px */
                    }}
                    .content {{
                        padding: 15px 10px !important; /* Reduced from 20px 15px */
                    }}
                    /* Header */
                    .header {{
                        flex-direction: column;
                        align-items: flex-start;
                    }}
                    .logo {{
                        margin-bottom: 10px;
                    }}
                    .header-content h1 {{
                        font-size: 20px;
                    }}
                    /* TABLE FIXES: Stack content vertically, removing horizontal constraints */
                    table, thead, tbody, th, td, tr {{
                        display: block !important;
                        width: 100% !important;
                        box-sizing: border-box !important;
                    }}
                    /* Hide headers (visual only, data remains) */
                    thead tr {{
                        position: absolute;
                        top: -9999px;
                        left: -9999px;
                    }}
                    /* Style the stacked cells */
                    td {{
                        border: none !important;
                        border-bottom: 1px solid #eee !important;
                        position: relative !important;
                        padding: 10px 0 !important;
                        text-align: left !important;
                        /* Removed word-break: break-word to fix aggressive breaking */
                    }}
                    /* Add context Labels */
                    .portfolio-table td:nth-of-type(1):before {{
                        content: "Common Fluids";
                        display: block;
                        font-weight: bold;
                        color: #083278;
                        margin-bottom: 4px;
                    }}
                    .portfolio-table td:nth-of-type(2):before {{
                        content: "Infusions";
                        display: block;
                        font-weight: bold;
                        color: #083278;
                        margin-bottom: 4px;
                    }}
                    .portfolio-table td:nth-of-type(3):before {{
                        content: "Pack Types";
                        display: block;
                        font-weight: bold;
                        color: #083278;
                        margin-bottom: 4px;
                    }}
                    /* Reset Comparison Table borders for stack */
                    .comparison-table td {{
                        border-bottom: 1px solid #eee !important;
                    }}
                    .button {{
                        width: 100%;
                        box-sizing: border-box;
                    }}
                }}
            </style>

        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">
                        <img src="{ frappe.utils.get_url('/files/pureblue-meds-logo.png') }" alt="Pure Blue Meds Logo">
                    </div>
                    <div class="header-content">
                        <h1>Pure Blue Meds Pvt Ltd</h1>
                        <p>Premium IV Fluids • Sterile Filling • Global Compliance</p>
                    </div>
                </div>

                <div class="content">
                    <p class="greeting">Dear {customer_name},</p>
                    <p class="greeting">
                        I'm reaching out to introduce <strong>Pure Blue Meds Pvt Ltd</strong> — a pharmaceutical company focused on high-quality IV fluid manufacturing using advanced ISBM technology and premium closure systems.
                    </p>

                    <h2>About Us</h2>
                    <p class="about-text">
                        We manufacture SlimPort & MediPort IV fluids, supported by validated sterilisation, precision-moulded ports, high clarity bottles and global standard compliance.
                    </p>

                    <h2>Product Portfolio (Highlights)</h2>
                    <table class="portfolio-table">
                        <thead>
                            <tr>
                                <th>Common IV Fluids</th>
                                <th>Infusions</th>
                                <th>Pack Types</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>NS • DNS • RL • Dextrose • Mannitol • D10 • D25</td>
                                <td>Paracetamol • Metronidazole • Ciprofloxacin • Levofloxacin</td>
                                <td>MediPort • SlimPort • FFS</td>
                            </tr>
                        </tbody>
                    </table>

                    <div class="comparison-section">
                        <h2>Why ISBM Is Better Than FFS</h2>
                        <table class="comparison-table">
                            <tbody>
                                <tr>
                                    <td>
                                        <strong>Superior Material</strong>
                                        High clarity PET/PP with lower leachables than FFS film.
                                    </td>
                                    <td>
                                        <strong>High Transparency</strong>
                                        Crystal clear bottles allow easy visual inspection.
                                    </td>
                                    <td>
                                        <strong>Stronger & Rigid</strong>
                                        Better transport durability & handling strength.
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <strong>Precision Ports</strong>
                                        SlimPort / MediPort ensure consistent sealing.
                                    </td>
                                    <td>
                                        <strong>Better Sterilisation</strong>
                                        Stable at 121°C vs FFS films which may deform.
                                    </td>
                                    <td>
                                        <strong>Hospital Preferred</strong>
                                        Better appearance, safety & reliability.
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    <p class="tagline"><strong>ISBM = safer, stronger, clearer and more reliable than FFS.</strong></p>
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
