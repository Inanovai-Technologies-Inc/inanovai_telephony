import frappe


@frappe.whitelist()
def get_supplier_phone(supplier):
    if not supplier:
        return {"phone": None}

    phone = None

    if frappe.db.has_column("Supplier", "mobile_no"):
        phone = frappe.db.get_value(
            "Supplier",
            supplier,
            "mobile_no",
        )

    if not phone and frappe.db.has_column("Supplier", "phone"):
        phone = frappe.db.get_value(
            "Supplier",
            supplier,
            "phone",
        )

    return {"phone": phone}
