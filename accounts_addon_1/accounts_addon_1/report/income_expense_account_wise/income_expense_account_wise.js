// Copyright (c) 2025, mohtashim and contributors
// For license information, please see license.txt

// frappe.query_reports["Income Expense Account Wise"] = {
// 	"filters": [

// 	]
// };

// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Income Expense Account Wise"] = $.extend({}, erpnext.financial_statements);

erpnext.utils.add_dimensions("Income Expense Account Wise", 10);

frappe.query_reports["Income Expense Account Wise"]["filters"].push({
	fieldname: "selected_view",
	label: __("Select View"),
	fieldtype: "Select",
	options: [
		{ value: "Report", label: __("Report View") },
		{ value: "Growth", label: __("Growth View") },
		{ value: "Margin", label: __("Margin View") },
	],
	default: "Report",
	reqd: 1,
});

frappe.query_reports["Income Expense Account Wise"]["filters"].push({
	fieldname: "accumulated_values",
	label: __("Accumulated Values"),
	fieldtype: "Check",
	default: 1,
});

frappe.query_reports["Income Expense Account Wise"]["filters"].push({
	fieldname: "include_default_book_entries",
	label: __("Include Default FB Entries"),
	fieldtype: "Check",
	default: 1,
});
