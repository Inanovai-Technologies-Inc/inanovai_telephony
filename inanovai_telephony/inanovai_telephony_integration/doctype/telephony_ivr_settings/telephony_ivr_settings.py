# Copyright (c) 2026, Inanovai and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class TelephonyIVRSettings(Document):
	def validate(self):
		self.validate_menu_destinations()

	def validate_menu_destinations(self):
		"""Every row needs a single-digit Press Key, and no two rows may
		share one — an ambiguous or missing key would make the IVR routing
		undefined for that digit."""
		seen = set()

		for row in self.menu_destinations:
			key = (row.press_key or "").strip()

			if not key:
				frappe.throw(_("Row {0}: Press Key is required.").format(row.idx))

			if not (key.isdigit() and len(key) == 1):
				frappe.throw(
					_("Row {0}: Press Key must be a single digit (0-9).").format(row.idx)
				)

			if key in seen:
				frappe.throw(_("Press Key {0} is configured more than once.").format(key))

			seen.add(key)
