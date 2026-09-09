import frappe


@frappe.whitelist()
def get_supplier_phone(supplier):
    if not supplier:
        return {"phone": None}

    phone = frappe.db.get_value(
        "Supplier",
        supplier,
        "mobile_no",
    )

    if not phone:
        phone = frappe.db.get_value(
            "Supplier",
            supplier,
            "phone",
        )

    return {"phone": phone}
