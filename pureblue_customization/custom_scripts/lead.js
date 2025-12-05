frappe.ui.form.on('Lead', {
	refresh(frm) {
		// your code here
		frm.page.add_button("Create Visit", () => {
            console.log("Create Visit button clicked");
               let dialog = new frappe.ui.Dialog({
                title: "Assign Employee",
                fields: [
                    {
                        fieldname: "employee",
                        label: "Employee",
                        fieldtype: "Link",
                        options: "Employee",
                        reqd: 1,
                        get_query() {
                            return {
                                filters: {
                                    designation: "Field Sales"
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
                    frappe.msgprint(`
                        <b>Employee:</b> ${values.employee}<br>
                        <b>Date:</b> ${values.assign_date}
                    `);
                    frappe.call({
                        method: "pureblue_customization.pureblue_customization.override.lead.create_todo",  
                        args: {
                            lead_name: frm.doc.name,   
                            employee: values.employee,
                            assign_date: values.assign_date
                            
                        },
                        callback: function(response) {
                            frappe.msgprint("Visit created successfully.");
                        },
                    })

                    dialog.hide();
                }
            });

            dialog.show();
        });
	}
});