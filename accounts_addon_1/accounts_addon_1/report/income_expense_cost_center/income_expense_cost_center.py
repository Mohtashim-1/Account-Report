import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data

def get_columns():
    return [
        {"label": "Cost Center", "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 250},
        {"label": "Income", "fieldname": "income", "fieldtype": "Currency", "width": 150},
        {"label": "Expense", "fieldname": "expense", "fieldtype": "Currency", "width": 150},
        {"label": "Difference", "fieldname": "difference", "fieldtype": "Currency", "width": 150},
    ]

def get_data(filters):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    if not from_date or not to_date:
        frappe.throw("Please select From Date and To Date")

    data = frappe.db.sql("""
        SELECT 
            gle.cost_center, 
            SUM(CASE WHEN account.root_type = 'Income' THEN gle.credit ELSE 0 END) AS income,
            SUM(CASE WHEN account.root_type = 'Expense' THEN gle.debit ELSE 0 END) AS expense,
            SUM(CASE WHEN account.root_type = 'Income' THEN gle.credit ELSE 0 END) - 
            SUM(CASE WHEN account.root_type = 'Expense' THEN gle.debit ELSE 0 END) AS difference
        FROM `tabGL Entry` gle
        JOIN `tabAccount` account ON gle.account = account.name
        WHERE gle.posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY gle.cost_center
        ORDER BY gle.cost_center
    """, {"from_date": from_date, "to_date": to_date}, as_dict=True)

    return data
