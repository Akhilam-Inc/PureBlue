frappe.ui.form.on('Lead', {
	refresh(frm) {
		// your code here
		frm.add_custom_button("Create Visit", () => {
            console.log("Create Visit button clicked");
               let dialog = new frappe.ui.Dialog({
                title: "Assign Employee for Visit",
                fields: [
                    {
                        fieldname: "sales_person",
                        label: "Sales Person",
                        fieldtype: "Link",
                        options: "Sales Person",
                        reqd: 1,
                       get_query() {
                            return {
                                filters: {
                                    name: ["!=", "Sales Team"]   // Remove ONLY Sales Team
                                }
                            };
			            }
                    },
                    {
                        fieldname: "assign_date",
                        label: "Assign Date",
                        fieldtype: "Date",
                        reqd: 1,
                        default: frappe.datetime.get_today()
                    }
                ],
                primary_action_label: "Submit",
                primary_action(values) {
                    // frappe.msgprint(`
                    //     <b>Sales Person:</b> ${values.sales_person}<br>
                    //     <b>Date:</b> ${values.assign_date}
                    // `);
                    frappe.call({
                        method: "pureblue_customization.pureblue_customization.override.lead.create_todo",  
                        args: {
                            lead_name: frm.doc.name,   
                            sales_person: values.sales_person,
                            assign_date: values.assign_date
                            
                        },
                        callback: function(response) {
                            // frappe.msgprint("Visit created successfully.");
                        },
                    })

                    dialog.hide();
    
                    frappe.call({
                        method: "frappe.client.set_value",
                        args: {
                            doctype: "Lead",
                            name: cur_frm.doc.name,
                            fieldname: "custom_assigned_to_person",
                            value: values.sales_person
                        },
                        callback: function() {
                            cur_frm.reload_doc();
                        }
                    });

                    d.hide();
                }
            });

            

            dialog.show();
        });

        if(!frm.doc.custom_brochure_sent){
            frm.add_custom_button("Send Brochure",function(){
                frm.trigger("send_brochure_btn")
            })
        }
        
	},


    send_brochure_btn: function(frm) {
        // Validate email exists
        if (!frm.doc.email_id && !frm.doc.email && !frm.doc.contact_email) {
            frappe.msgprint({
                title: __('Email Required'),
                message: __('Please add an email address before sending the brochure'),
                indicator: 'red'
            });
            return;
        }
        
        // Confirm before sending
        frappe.confirm(
            __('Send brochure email to {0}?', [frm.doc.email_id || frm.doc.email || frm.doc.contact_email]),
            function() {
                // User confirmed
                frappe.call({
                    method: 'pureblue_customization.pureblue_customization.override.lead.send_brochure_email',
                    args: {
                        doc_name: frm.doc.name,
                        doctype_name: frm.doctype
                    },
                    freeze: true,
                    freeze_message: __('Sending Brochure Email...'),
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            frappe.show_alert({
                                message: __('Brochure email sent successfully!'),
                                indicator: 'green'
                            }, 5);
                            frm.reload_doc();
                        }
                    },
                    error: function(r) {
                        frappe.show_alert({
                            message: __('Failed to send email'),
                            indicator: 'red'
                        }, 5);
                    }
                });
            }
        );
    }
});