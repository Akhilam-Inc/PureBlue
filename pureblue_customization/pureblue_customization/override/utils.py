import frappe


@frappe.whitelist()
def send_alerts_for_pending_coas():
    try:
        today = frappe.utils.nowdate()
        fifteen_days_ago = frappe.utils.add_days(today, -15)

        # Fetch batches created within last 15 days
        batches = frappe.get_all(
            "Batch",
            filters={
                "status": "Active",
                "custom_is_coa_completed": 0,
                "creation": ["between", (fifteen_days_ago, today)]
            },
            fields=["name", "creation"]
        )

        if not batches:
            return frappe.log_error("No pending COA batches found in last 15 days.", "Pending COA Log")

        # Fetch stock manager users excluding Administrator
        stock_managers = frappe.get_all(
            "Has Role",
            filters={"role": "Stock Manager"},
            fields=["parent"]
        )

        if not stock_managers:
            return frappe.log_error("No Stock Managers found.", "COA Alert")

        emails = []
        for sm in stock_managers:
            user_id = sm.parent

            # Skip Administrator
            if user_id.lower() == "administrator":
                continue

            user = frappe.db.get_value("User", user_id, ["email", "enabled"], as_dict=True)

            if user and user.enabled and user.email:
                emails.append(user.email)

        if not emails:
            return frappe.log_error("No valid Stock Manager emails found (Administrator excluded).", "COA Alert")

        # Prepare email content
        subject = "Pending COA Alerts - Batches in Last 15 Days"
        message = "<h4>The following batches have COA pending in the last 15 days:</h4><ul>"

        for b in batches:
            message += f"<li>{b.name} — Created on {b.creation}</li>"
        message += "</ul>"

        # Send email
        frappe.sendmail(
            recipients=emails,
            subject=subject,
            message=message
        )

        return frappe.log_error(
            f"Alerts sent successfully to: {', '.join(emails)}",
            "Pending COA Log"
        )

    except Exception:
        return frappe.log_error(frappe.get_traceback(), "Pending COA Alerts Error")




