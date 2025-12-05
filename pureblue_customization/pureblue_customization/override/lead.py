import frappe
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