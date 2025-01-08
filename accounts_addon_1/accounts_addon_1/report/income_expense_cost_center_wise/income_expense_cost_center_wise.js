// Copyright (c) 2025, mohtashim and contributors
// For license information, please see license.txt

frappe.query_reports["Income Expense Cost Center Wise"] = {
    "filters": {
        "fiscal_year": {
            "label": __("Fiscal Year"),
            "fieldname": "fiscal_year",
            "fieldtype": "Link",
            "options": "Fiscal Year",
            "default": frappe.defaults.get_default("fiscal_year"),
            "reqd": 1
        },
        "from_date": {
            "label": __("From Date"),
            "fieldname": "from_date",
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        "to_date": {
            "label": __("To Date"),
            "fieldname": "to_date",
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        "account": {
            "label": __("Account"),
            "fieldname": "account",
            "fieldtype": "Link",
            "options": "Account",
            "reqd": 0
        }
    },
};
