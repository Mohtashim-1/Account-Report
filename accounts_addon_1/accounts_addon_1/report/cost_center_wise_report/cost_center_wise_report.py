import frappe
from frappe import _

def execute(filters=None):
    # Get the cost centers dynamically
    cost_centers = get_cost_centers(filters)
    columns = get_columns(cost_centers)
    data = get_data(filters, cost_centers)

    return columns, data

def get_columns(cost_centers):
    # Define initial columns
    columns = [
        {
            "label": _("Account"),
            "fieldname": "account",
            "fieldtype": "Link",
            "options": "Account",
            "width": 150
        }
    ]

    # Add Debit and Credit columns for each cost center
    for cost_center in cost_centers:
        scrubbed_cc = frappe.scrub(cost_center)
        columns.append({
            "label": _(f"{cost_center} Debit"),
            "fieldname": f"{scrubbed_cc}_debit",
            "fieldtype": "Float",
            "width": 200
        })
        columns.append({
            "label": _(f"{cost_center} Credit"),
            "fieldname": f"{scrubbed_cc}_credit",
            "fieldtype": "Float",
            "width": 200
        })

    return columns

def get_cost_centers(filters):
    # Fetch unique cost centers
    query = """
        SELECT DISTINCT cost_center
        FROM `tabGL Entry`
        WHERE {conditions}
        ORDER BY cost_center
    """.format(conditions=get_conditions(filters))

    cost_centers = frappe.db.sql(query, filters, as_list=True)
    return [row[0] for row in cost_centers]

def get_data(filters, cost_centers):
    # Fetch data grouped by account and cost center for both debit and credit
    query = """
        SELECT
            account,
            cost_center,
            SUM(debit) AS debit,
            SUM(credit) AS credit
        FROM `tabGL Entry`
        WHERE {conditions}
        GROUP BY account, cost_center
    """.format(conditions=get_conditions(filters))

    raw_data = frappe.db.sql(query, filters, as_dict=True)

    # Organize data to have cost centers as headings for both debit and credit
    grouped_data = {}
    for row in raw_data:
        account = row["account"]
        cost_center = row["cost_center"]
        debit = row["debit"]
        credit = row["credit"]

        if account not in grouped_data:
            grouped_data[account] = {f"{frappe.scrub(cc)}_debit": 0 for cc in cost_centers}
            grouped_data[account].update({f"{frappe.scrub(cc)}_credit": 0 for cc in cost_centers})
            grouped_data[account]["account"] = account

        scrubbed_cc = frappe.scrub(cost_center)
        grouped_data[account][f"{scrubbed_cc}_debit"] = debit
        grouped_data[account][f"{scrubbed_cc}_credit"] = credit

    # Convert grouped data to a list of dictionaries for report rendering
    return list(grouped_data.values())

def get_conditions(filters):
    # Construct WHERE clause based on filters
    conditions = []
    if filters.get("account"):
        conditions.append("account = %(account)s")
    if filters.get("cost_center"):
        conditions.append("cost_center = %(cost_center)s")
    if filters.get("from_date"):
        conditions.append("posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("posting_date <= %(to_date)s")

    return " AND ".join(conditions) if conditions else "1=1"
