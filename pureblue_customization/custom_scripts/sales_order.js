frappe.ui.form.on("Sales Order", {
    refresh(frm) {
        if (!frm.doc.customer || frm.doc.docstatus >= 1) return;

        frappe.db.get_doc("Customer", frm.doc.customer).then(cust => {
            let license_attachment = cust.custom_drug_license;
            let license_no = cust.custom_license_no;
            let license_expiry = cust.custom_license_expiry_date;

            // Check if missing any required values
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
                            fieldname: "custom_drug_license",
                            default: license_attachment || "",
                            reqd: 1
                        },
                        {
                            fieldtype: "Data",
                            label: "License Number",
                            fieldname: "custom_license_no",
                            default: license_no || "",
                            reqd: 1
                        },
                        {
                            fieldtype: "Date",
                            label: "License Expiry Date",
                            fieldname: "custom_license_expiry_date",
                            default: license_expiry || "",
                            reqd: 1
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
                                    // FIXED fieldnames
                                    custom_drug_license: values.custom_drug_license,
                                    custom_license_no: values.custom_license_no,
                                    custom_license_expiry_date: values.custom_license_expiry_date
                                }
                            },
                            callback() {
                                frappe.show_alert("Customer Details Updated");
                                d.hide();
                                frm.reload_doc();
                            }
                        });
                    }
                });

                d.show();
            }
        });
    }
});

