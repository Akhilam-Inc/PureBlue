frappe.ui.form.on('Contact', {
    refresh(frm) {
        if (!frm.doc.custom_brochure_sent) {
            frm.add_custom_button("Send Brochure", function () {
                frm.trigger("send_brochure_btn");
            });
        }
    },

    send_brochure_btn: function (frm) {
        let emails = [];

        // 1. Child table email_ids
        if (frm.doc.email_ids && frm.doc.email_ids.length > 0) {
            frm.doc.email_ids.forEach(row => {
                if (row.email_id) emails.push(row.email_id);
            });
        }

        // 2. Main email fields (avoid duplicates)
        ["email_id", "email", "contact_email"].forEach(f => {
            if (frm.doc[f] && !emails.includes(frm.doc[f])) {
                emails.push(frm.doc[f]);
            }
        });

        // No email found → error
        if (emails.length === 0) {
            frappe.msgprint({
                title: __("Email Required"),
                message: __("Please add an email address before sending the brochure"),
                indicator: "red"
            });
            return;
        }

        // 🚀 CASE 1: Only one email → send directly
        if (emails.length === 1) {
            let only_email = emails[0];

            frappe.confirm(
                __("Send brochure email to <b>{0}</b>?", [only_email]),
                function () {
                    frappe.call({
                        method: "pureblue_customization.pureblue_customization.override.contact.send_brochure_email",
                        args: {
                            doc_name: frm.doc.name,
                            doctype_name: frm.doctype,
                            email_to: only_email
                        },
                        freeze: true,
                        freeze_message: __("Sending Brochure Email..."),

                        callback(r) {
                            if (r.message && r.message.success) {
                                frappe.show_alert({
                                    message: __("Brochure email sent successfully!"),
                                    indicator: "green"
                                }, 5);
                                frm.reload_doc();
                            }
                        },
                        error() {
                            frappe.show_alert({
                                message: __("Failed to send email"),
                                indicator: "red"
                            }, 5);
                        }
                    });
                }
            );
            return;
        }

        // 🚀 CASE 2: Multiple emails → show selection dialog
        let dialog = new frappe.ui.Dialog({
            title: __("Select Email to Send Brochure"),
            fields: [
                {
                    fieldtype: "Select",
                    fieldname: "selected_email",
                    label: __("Email"),
                    options: emails.join("\n"),
                    reqd: 1
                }
            ],
            primary_action_label: __("Send"),
            primary_action(values) {
                dialog.hide();

                
                    frappe.call({
                        method: "pureblue_customization.pureblue_customization.override.contact.send_brochure_email",
                        args: {
                            doc_name: frm.doc.name,
                            doctype_name: frm.doctype,
                            email_to: values.selected_email
                        },
                        freeze: true,
                        freeze_message: __("Sending Brochure Email..."),

                        callback(r) {
                            if (r.message && r.message.success) {
                                frappe.show_alert({
                                    message: __("Brochure email sent successfully!"),
                                    indicator: "green"
                                }, 5);
                                frm.reload_doc();
                            }
                        },
                        error() {
                            frappe.show_alert({
                                message: __("Failed to send email"),
                                indicator: "red"
                            }, 5);
                        }
                    });
            }
        });

        dialog.show();
    }
});
