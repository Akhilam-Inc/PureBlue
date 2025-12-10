frappe.ui.form.on("Batch", {
    custom_coa_attachment:function(frm){
        if(frm.doc.custom_coa_attachment){
            frm.set_value("custom_is_coa_completed",1)
            frm.refresh_fields("custom_is_coa_completed")
            frm.save()
        }else{
            frm.set_value("custom_is_coa_completed",0)
            frm.refresh_fields("custom_is_coa_completed")
            frm.save()
        }
    }
});