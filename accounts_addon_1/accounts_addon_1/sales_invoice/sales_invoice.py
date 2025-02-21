import frappe

def custom_invoice_logic(self, method=None):
    """Automatically creates a Journal Entry to adjust tax accounts in Sales Invoice"""

    frappe.msgprint("Starting Journal Entry Creation...")

    tax_dict = {}  # Dictionary to store tax amounts per tax account

    for tax in self.taxes:
        if tax.account_head:
            if tax.account_head not in tax_dict:
                tax_dict[tax.account_head] = 0  # Ensure all accounts are included
            tax_dict[tax.account_head] += tax.tax_amount  # Accumulate tax amounts

    if not tax_dict:
        frappe.msgprint("No applicable tax accounts found in this Sales Invoice.", alert=True)
        return

    # Create a Journal Entry only if there are taxes
    jv = frappe.new_doc("Journal Entry")
    jv.voucher_type = "Journal Entry"
    jv.posting_date = self.posting_date
    jv.company = self.company
    jv.remark = f"Adjustment Entry for {self.name}"

    for tax_account, tax_amount in tax_dict.items():
        account_status = frappe.db.exists("Account", {"name": tax_account, "company": self.company, "disabled": 0})
        
        if not account_status:
            frappe.throw(f"Account {tax_account} does not exist or is disabled. Please check your Chart of Accounts.")

        balance_must_be = frappe.db.get_value("Account", tax_account, "balance_must_be")
        supplier = frappe.db.get_value("Account", tax_account, "custom_supplier")

        min_amount = max(tax_amount, 0.01)  # Ensure at least 0.01 is entered

        if balance_must_be == "Credit":
            jv.append("accounts", {
                "account": tax_account,
                "debit_in_account_currency": min_amount,
                "party_type": "Supplier" if supplier else None,
                "party": supplier if supplier else None,
                "cost_center": self.cost_center
            })
            jv.append("accounts", {
                "account": "Cash - SAH",  # Adjust with correct Cash/Bank account
                "credit_in_account_currency": min_amount,
                "cost_center": self.cost_center
            })
        elif balance_must_be == "Credit":
            jv.append("accounts", {
                "account": tax_account,
                "credit_in_account_currency": min_amount,
                "party_type": "Supplier" if supplier else None,
                "party": supplier if supplier else None,
                "cost_center": self.cost_center
            })
            jv.append("accounts", {
                "account": "Cash - SAH",  # Adjust with correct Cash/Bank account
                "debit_in_account_currency": min_amount,
                "cost_center": self.cost_center
            })
        else:
            jv.append("accounts", {
                "account": tax_account,
                "debit_in_account_currency": min_amount,
                "party_type": "Supplier" if supplier else None,
                "party": supplier if supplier else None,
                "cost_center": self.cost_center
            })
            jv.append("accounts", {
                "account": "Cash - SAH",  # Adjust with correct Cash/Bank account
                "credit_in_account_currency": min_amount,
                "cost_center": self.cost_center
            })

    # Save & Submit the Journal Entry
    jv.insert()
    jv.submit()

    frappe.msgprint(f"Journal Entry {jv.name} created successfully!", alert=True)
