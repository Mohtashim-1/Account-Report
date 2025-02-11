# Copyright (c) 2025, mohtashim and contributors
# For license information, please see license.txt


import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    columns, cost_centers = get_columns()
    data = get_data(filters, cost_centers)

    return columns, data

def get_columns():
    # Get all Parent Cost Centers
    parent_cost_centers = frappe.db.sql("""
        SELECT DISTINCT parent_cost_center 
        FROM `tabCost Center`
        WHERE parent_cost_center IS NOT NULL
    """, as_dict=True)

    columns = [{"label": "Account", "fieldname": "account", "fieldtype": "Data", "width": 200}]

    cost_center_map = {}  # {Parent: [Child1, Child2, Child3]}
    
    for parent in parent_cost_centers:
        parent_name = parent["parent_cost_center"]
        cost_center_map[parent_name] = frappe.db.sql("""
            SELECT name FROM `tabCost Center` 
            WHERE parent_cost_center = %s
        """, (parent_name,), as_dict=True)

        for child in cost_center_map[parent_name]:
            columns.append({
                "label": child["name"], 
                "fieldname": child["name"], 
                "fieldtype": "Currency", 
                "width": 150
            })
    
    # Add Total Column
    columns.append({"label": "Total", "fieldname": "total", "fieldtype": "Currency", "width": 200})

    return columns, cost_center_map

def get_data(filters, cost_center_map):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    if not from_date or not to_date:
        frappe.throw("Please select From Date and To Date")

    final_data = []
    categories = ["Income", "Expense"]

    for category in categories:
        accounts = frappe.db.sql("""
            SELECT DISTINCT gle.account FROM `tabGL Entry` gle
            JOIN `tabAccount` account ON gle.account = account.name
            WHERE account.root_type = %s
            AND gle.posting_date BETWEEN %s AND %s
        """, (category, from_date, to_date), as_dict=True)

        for acc in accounts:
            row = {"account": acc["account"], "total": 0}

            for parent, children in cost_center_map.items():
                for child in children:
                    cost_center = child["name"]

                    value = frappe.db.sql("""
                        SELECT SUM(gle.credit - gle.debit) AS amount
                        FROM `tabGL Entry` gle
                        JOIN `tabAccount` account ON gle.account = account.name
                        WHERE gle.account = %s
                        AND gle.cost_center = %s
                        AND gle.posting_date BETWEEN %s AND %s
                    """, (acc["account"], cost_center, from_date, to_date), as_dict=True)

                    row[cost_center] = value[0]["amount"] or 0
                    row["total"] += row[cost_center]
            
            final_data.append(row)
        
        # Add total row for each category
        total_row = {"account": f"Total {category}", "total": 0}
        for parent, children in cost_center_map.items():
            for child in children:
                total_row[child["name"]] = sum(row[child["name"]] for row in final_data if row["account"] in [a["account"] for a in accounts])
                total_row["total"] += total_row[child["name"]]

        final_data.append(total_row)
    
    return final_data
