import frappe
# Income Expense Cost Center Group Wise
# Query Report for displaying Parent and Child Cost Centers separately

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "Account", "fieldname": "account", "fieldtype": "Data", "width": 250},
        {"label": "Parent Cost Center", "fieldname": "parent_cost_center", "fieldtype": "Data", "width": 200},
        {"label": "Child Cost Center", "fieldname": "child_cost_center", "fieldtype": "Data", "width": 200},
        {"label": "Total Amount", "fieldname": "total_amount", "fieldtype": "Currency", "width": 150},
    ]


def get_data(filters):
    conditions = ""
    if filters.get("from_date") and filters.get("to_date"):
        conditions += f"AND gl.posting_date BETWEEN '{filters.get('from_date')}' AND '{filters.get('to_date')}'"

    query = f"""
        SELECT
            cc1.parent_cost_center AS parent_cost_center,
            cc1.name AS child_cost_center,
            gl.account AS account,
            SUM(gl.debit) - SUM(gl.credit) AS total_amount
        FROM `tabGL Entry` gl
        JOIN `tabCost Center` cc1 ON gl.cost_center = cc1.name
        WHERE cc1.is_group = 0 {conditions}
        GROUP BY cc1.parent_cost_center, cc1.name, gl.account
        ORDER BY cc1.parent_cost_center, cc1.name;
    """

    results = frappe.db.sql(query, as_dict=True)
    
    formatted_data = []
    current_parent = None

    for row in results:
        if row.parent_cost_center != current_parent:
            formatted_data.append({
                "account": row.account,
                "parent_cost_center": row.parent_cost_center,
                "child_cost_center": "",
                "total_amount": "",
            })
            current_parent = row.parent_cost_center

        formatted_data.append({
            "account": row.account,
            "parent_cost_center": "",
            "child_cost_center": row.child_cost_center,
            "total_amount": row.total_amount,
        })

    return formatted_data

