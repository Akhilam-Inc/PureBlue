frappe.ui.form.on("Sales Order", {
    refresh(frm) {
        if (!frm.doc.customer) return;

        frappe.db.get_doc("Customer", frm.doc.customer).then(cust => {
            let license_attachment = cust.custom_drug_license_;
            let license_no = cust.custom_license_no;
            let license_expiry = cust.custom_license_expiry;

            // If any field missing → Show dialog
            if (!license_attachment || !license_no || !license_expiry) {
                const d = new frappe.ui.Dialog({
                    title: "Missing Drug License Details",
                    fields: [
                        {
                            fieldtype: "Section Break",
                            label: "Customer Drug License Info"
                        },
                        {
                            fieldtype: "Attach",
                            label: "Drug License Attachment",
                            fieldname: "custom_drug_license_",
                            reqd:1
                        },
                        {
                            fieldtype: "Data",
                            label: "License Number",
                            fieldname: "custom_license_no",
                            reqd:1
                        },
                        {
                            fieldtype: "Date",
                            label: "License Expiry Date",
                            fieldname: "custom_license_expiry",
                            reqd:1
                        }
                    ],
                    primary_action_label: "Update Customer",
                    primary_action(values) {
                        frappe.call({
                            method: "frappe.client.set_value",
                            args: {
                                doctype: "Customer",
                                name: cust.name,
                                fieldname: {
                                    custom_drug_license_: values.custom_drug_license_,
                                    custom_license_no: values.custom_license_no,
                                    custom_license_expiry: values.custom_license_expiry,
                                }
                            },
                            callback() {
                                frappe.show_alert("Customer Details Updated");
                                d.hide();
                            }
                        });
                    }
                });

                d.show();
            }
        });
    }
});
