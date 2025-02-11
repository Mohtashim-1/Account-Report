# Copyright (c) 2025, Mohtashim and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    # Unpacking all three values returned from get_columns()
    columns, cost_center_map, parent_mapping = get_columns()
    data = get_data(filters, cost_center_map, parent_mapping)

    return columns, data

def get_columns():
    # Fetch all cost centers with their parents
    cost_centers = frappe.db.sql("""
        SELECT name, parent_cost_center
        FROM `tabCost Center`
    """, as_dict=True)

    columns = [{"label": "Account", "fieldname": "account", "fieldtype": "Data", "width": 200}]
    cost_center_map = {}  # {Parent: [Child1, Child2, Child3]}
    parent_mapping = {}  # {Child: Parent}

    for cc in cost_centers:
        child_name = cc["name"]
        parent_name = cc["parent_cost_center"] or "Uncategorized"

        if parent_name not in cost_center_map:
            cost_center_map[parent_name] = []

        cost_center_map[parent_name].append(child_name)
        parent_mapping[child_name] = parent_name

    # Add columns dynamically for each parent cost center and its children
    for parent, children in cost_center_map.items():
        for child in children:
            columns.append({
                "label": f"{parent} - {child}",
                "fieldname": child,
                "fieldtype": "Currency",
                "width": 150
            })

    # Add a Total Column
    columns.append({"label": "Total", "fieldname": "total", "fieldtype": "Currency", "width": 200})

    return columns, cost_center_map, parent_mapping

def get_data(filters, cost_center_map, parent_mapping):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    if not from_date or not to_date:
        frappe.throw("Please select From Date and To Date")

    final_data = []
    categories = ["Income", "Expense"]

    for category in categories:
        accounts = frappe.db.sql("""
            SELECT DISTINCT gle.account 
            FROM `tabGL Entry` gle
            JOIN `tabAccount` account ON gle.account = account.name
            WHERE account.root_type = %s
            AND gle.posting_date BETWEEN %s AND %s
        """, (category, from_date, to_date), as_dict=True)

        for acc in accounts:
            row = {"account": acc["account"], "total": 0}

            for parent, children in cost_center_map.items():
                for child in children:
                    cost_center = child

                    value = frappe.db.sql("""
                        SELECT SUM(gle.credit - gle.debit) AS amount
                        FROM `tabGL Entry` gle
                        JOIN `tabAccount` account ON gle.account = account.name
                        WHERE gle.account = %s
                        AND gle.cost_center = %s
                        AND gle.posting_date BETWEEN %s AND %s
                    """, (acc["account"], cost_center, from_date, to_date), as_dict=True)

                    amount = value[0]["amount"] or 0
                    row[cost_center] = amount
                    row["total"] += amount

            final_data.append(row)

        # Add total row for each category
        total_row = {"account": f"Total {category}", "total": 0}
        for parent, children in cost_center_map.items():
            for child in children:
                total_row[child] = sum(row[child] for row in final_data if row["account"] in [a["account"] for a in accounts])
                total_row["total"] += total_row[child]

        final_data.append(total_row)

    return final_data
