// Copyright (c) 2025, mohtashim and contributors
// For license information, please see license.txt

frappe.query_reports["Income Expense Cost Center"] = {
	"filters": [
        {
            "fieldname": "cost_center",
            "label": __("Cost Center"),
            "fieldtype": "Link",
            "options": "Cost Center",
            "default": "",
            "reqd": 0
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        }
    ]	
};
