import frappe

EMPTY_ACTIONS = {
    "enabled": False,
    "make_a_call": False,
    "send_sms": False,
    "send_otp": False,
}


@frappe.whitelist()
def get_telephony_actions(doctype):
    """Return which telephony actions are enabled for the given DocType, per
    the "Telephony Settings" Single. Safe to call for any DocType, whether or
    not it's configured:

      - doctype missing/not a real DocType      -> all actions False
      - Telephony Settings doesn't exist yet     -> all actions False
      - Telephony Settings.enabled is unchecked  -> all actions False
      - no Telephony Action row for this doctype -> all actions False
      - a row exists but every checkbox is off   -> those actions False
    """
    if not doctype or not frappe.db.exists("DocType", doctype):
        return EMPTY_ACTIONS

    if not frappe.db.exists("DocType", "Telephony Settings"):
        return EMPTY_ACTIONS

    settings = frappe.get_cached_doc("Telephony Settings")
    return settings.get_actions_for(doctype)


# Fields checked directly on a document before looking at any linked record.
DIRECT_PHONE_FIELDS = ["mobile_no", "contact_mobile", "phone", "mobile"]

# Linked doctypes this resolver knows how to read a phone number from, once
# it has followed a Link/Dynamic Link field to one. Deliberately small and
# explicit: it's the set of "phone-bearing" doctypes, not a list of every
# doctype telephony is enabled for.
LINKED_PHONE_DOCTYPES = {"Contact", "Customer", "Supplier"}

# How many hops of Link/Dynamic Link fields to follow (e.g. Payment Entry ->
# Supplier is 1 hop; Payment Entry -> Supplier -> Contact would be 2). Kept
# small on purpose — this is a best-effort lookup, not a general graph walk.
MAX_RESOLUTION_DEPTH = 2

EMPTY_PHONE = {"phone": "", "source": ""}


@frappe.whitelist()
def resolve_phone_number(doctype, docname):
    """Best-effort, generic phone-number lookup for any document.

    This is called only at click-time by the telephony buttons — button
    *visibility* is decided entirely by get_telephony_actions() above and
    never depends on whether this finds anything.

    Resolution order (see _resolve_phone_from_doc):
      1. A direct phone-shaped field on the document itself
         (mobile_no / contact_mobile / phone / mobile).
      2. Supplier: reuses the existing, already-proven
         inanovai_telephony.api.purchase_order.get_supplier_phone() rather
         than reimplementing its Supplier-field-then-Contact-fallback logic.
      3. Any Dynamic Link field on the document (e.g. Payment Entry's
         party/party_type) — the target doctype is read from the doc's own
         metadata, not hardcoded to "party_type"/"party" by name, so this
         also covers other doctypes using the same standard Frappe pattern.
      4. contact_person, if present (a common Link -> Contact field across
         selling/buying transaction doctypes).
      5. Any other Link field on the document whose target doctype is one
         this resolver knows how to read a phone from (LINKED_PHONE_DOCTYPES),
         found via the DocType's own field metadata — not a hardcoded list
         of source doctypes like Payment Entry/Purchase Order/Quotation.

    Returns {"phone": "...", "source": "..."}; phone is "" (with source "")
    if nothing was found anywhere in that chain.
    """
    if not doctype or not frappe.db.exists("DocType", doctype):
        return EMPTY_PHONE

    if not docname or not frappe.db.exists(doctype, docname):
        return EMPTY_PHONE

    doc = frappe.get_doc(doctype, docname)
    return _resolve_phone_from_doc(doc)


def _resolve_phone_from_doc(doc, depth=0):
    if depth > MAX_RESOLUTION_DEPTH:
        return EMPTY_PHONE

    for fieldname in DIRECT_PHONE_FIELDS:
        value = doc.get(fieldname)
        if value:
            return {"phone": value, "source": f"{doc.doctype}.{fieldname}"}

    if doc.doctype == "Supplier":
        from inanovai_telephony.api.purchase_order import get_supplier_phone

        phone = (get_supplier_phone(doc.name) or {}).get("phone")
        if phone:
            return {"phone": phone, "source": f"Supplier.{doc.name}"}
        return EMPTY_PHONE

    meta = frappe.get_meta(doc.doctype)

    for df in meta.get("fields", {"fieldtype": "Dynamic Link"}):
        target_doctype = doc.get(df.options)
        value = doc.get(df.fieldname)
        if not target_doctype or not value or not frappe.db.exists(target_doctype, value):
            continue
        result = _resolve_phone_from_doc(frappe.get_doc(target_doctype, value), depth + 1)
        if result["phone"]:
            return result

    contact_person = doc.get("contact_person")
    if contact_person and frappe.db.exists("Contact", contact_person):
        result = _resolve_phone_from_doc(frappe.get_doc("Contact", contact_person), depth + 1)
        if result["phone"]:
            return result

    for df in meta.get_link_fields():
        if df.options not in LINKED_PHONE_DOCTYPES:
            continue
        value = doc.get(df.fieldname)
        if not value or not frappe.db.exists(df.options, value):
            continue
        result = _resolve_phone_from_doc(frappe.get_doc(df.options, value), depth + 1)
        if result["phone"]:
            return result

    return EMPTY_PHONE
