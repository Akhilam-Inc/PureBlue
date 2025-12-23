frappe.ui.form.on("Delivery Note", {
	refresh(frm) {
		// your code here
        if(frm.doc.workflow_state==="Out for Delivery"){
            hide_actions(frm);
            add_mark_delivered_button(frm);
        }
		
	},
    onload_post_render: function (frm) {
        if (frm.doc.workflow_state === "Out for Delivery") {
            hide_actions(frm);
            add_mark_delivered_button(frm);
        }
        if(frm.doc.workflow_state==="Delivered"){
            frm.clear_custom_buttons();
        }
    },
	before_workflow_action: async function (frm) {


        if(frm.selected_workflow_action === "Update Transport Details"){
            return new Promise((resolve, reject) => {
                if(!frm.doc.transporter){
                    frappe.throw({
                        title: __("Update Transport Details Validation Error"),
                        message: __("Transporter is required to update transport details."),
                        indicator: "red",
                    });
                    reject();
                    return;
                }
                resolve();
            });
        }
		/* --------------------------------
        SEND FOR DELIVERY → Generate OTP
        ---------------------------------*/
		if (frm.selected_workflow_action === "Send for Delivery") {
			return new Promise(async (resolve, reject) => {
				try {

                     const against_sales_orders = [
                        ...new Set(
                            (frm.doc.items || [])
                                .map(row => row.against_sales_order)
                                .filter(Boolean)
                        )
                    ].join(",");
					const r = await frappe.call({
						method:
							"pureblue_customization.pureblue_customization.override.delivery_note.generate_and_send_otp",
						args: {
							reference_doctype: frm.doctype,
							reference_name: frm.doc.name,
							contact_email:frm.doc.contact_email,
							customer: frm.doc.customer,
							mobile_no: frm.doc.mobile_no,
                            against_sales_orders: against_sales_orders
						},
					});

					frappe.msgprint(
						__("OTP has been sent to <b>{0}</b>", [r.message.email])
					);

					resolve();
				} catch (err) {
					reject(err);
				}
			});
		}

		/* --------------------------------
        MARK DELIVERED → Verify OTP
        ---------------------------------*/
		if (frm.selected_workflow_action === "Mark Delivered") {
			return new Promise(async (resolve, reject) => {
				try {
					const r = await frappe.call({
						method:
							"pureblue_customization.pureblue_customization.override.delivery_note.is_delivery_otp_verified",
						args: {
							reference_doctype: frm.doctype,
							reference_name: frm.doc.name,
						},
					});

					// ❌ OTP NOT VERIFIED
					if (!r.message) {
						frappe.throw({
							title: __("Verification Pending"),
							message: __(
								"OTP verification is pending for this Delivery Note.<br><br>" +
									"Please click on <b>Mark Delivery</b> button to complete the delivery verification."
							),
							indicator: "orange",
						});

						reject(); // 🚨 HARD STOP workflow
						return;
					}

					resolve(); // ✅ OTP verified → allow workflow
				} catch (e) {
					reject(); // 🚨 safety block
				}
			});
		}
	},
});

function open_delivery_otp_dialog(frm) {
	const dialog = new frappe.ui.Dialog({
		title: __("Verify Delivery OTP"),
		fields: [
			{
				fieldname: "otp",
				label: __("Enter OTP"),
				fieldtype: "Data",
				reqd: 1,
			},
		],
		primary_action_label: __("Verify & Deliver"),
		primary_action: async (values) => {
			try {
				dialog.get_primary_btn().prop("disabled", true);

				await frappe.call({
					method:
						"pureblue_customization.pureblue_customization.override.delivery_note.verify_delivery_otp",
					args: {
						reference_doctype: frm.doctype,
						reference_name: frm.doc.name,
						otp: values.otp,
					},
				});

				dialog.hide();
				frappe.msgprint(__("OTP verified successfully"));

				frm.reload_doc();
			} catch (e) {
				dialog.get_primary_btn().prop("disabled", false);
			}
		},
	});

	dialog.show();
}
function hide_actions(frm) {

    // Desktop toolbar
    $('.actions-btn-group').hide();

    // Mobile primary action
    if (frappe.ui.toolbar && frappe.ui.toolbar.clear_actions) {
        frappe.ui.toolbar.clear_actions();
    }

    // Hide mobile floating action button (FAB)
    $('.page-actions .primary-action').hide();
}

function add_mark_delivered_button(frm) {

    frm.clear_custom_buttons();

    frm.add_custom_button(__("Mark Delivered"), function () {
        open_delivery_otp_dialog(frm);
    }).addClass("btn btn-success").css({
                backgroundColor: "#28a745",
                borderColor: "#28a745",
                color: "#fff",
            });;

    // Mobile support
    if (frappe.ui.toolbar && frappe.ui.toolbar.add_action_button) {
        frappe.ui.toolbar.add_action_button(
            __("Mark Delivered"),
            () => open_delivery_otp_dialog(frm)
        );
    }
}
