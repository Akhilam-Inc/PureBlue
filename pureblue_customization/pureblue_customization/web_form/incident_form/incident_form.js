frappe.ready(function() {
	// bind events here
})

// frappe.web_form.after_save = () => {
//     if (!frappe.web_form.doc || !frappe.web_form.doc.name) {
//         console.error("Web Form doc not available");
//         return;
//     }

//     frappe.call({
//         method: "pureblue_customization.api.submit_incident",
//         args: {
//             docname: frappe.web_form.doc.name
//         },
//         freeze: true,
//         freeze_message: __("Submitting Incident..."),
//         callback: function (r) {
//             if (r && r.message) {
//                 console.log("Incident auto-submitted:", r.message);
//             }
//         },
//         error: function (err) {
//             console.error("Incident auto-submit failed:", err);
//             frappe.msgprint({
//                 title: __("Submission Error"),
//                 message: __("Incident was saved but could not be submitted. Please contact administrator."),
//                 indicator: "red"
//             });
//         }
//     });
// };
