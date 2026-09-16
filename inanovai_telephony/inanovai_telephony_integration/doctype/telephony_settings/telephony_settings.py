# Copyright (c) 2026, Inanovai and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class TelephonySettings(Document):
	def validate(self):
		self.validate_unique_target_doctypes()

	def validate_unique_target_doctypes(self):
		seen = set()
		for row in self.telephony_actions:
			if not row.target_doctype:
				continue
			if row.target_doctype in seen:
				frappe.throw(
					_("Telephony Action is configured more than once for {0} (row {1}).").format(
						row.target_doctype, row.idx
					)
				)
			seen.add(row.target_doctype)

	def get_actions_for(self, target_doctype):
		"""Return the enabled telephony actions for a given DocType.

		Always returns the same shape, so callers never need to special-case
		"not configured" vs "configured but disabled" vs "settings off".
		"""
		result = {
			"enabled": bool(self.enabled),
			"make_a_call": False,
			"send_sms": False,
			"send_otp": False,
		}

		if not self.enabled or not target_doctype:
			return result

		for row in self.telephony_actions:
			if row.target_doctype == target_doctype:
				result["make_a_call"] = bool(row.make_a_call)
				result["send_sms"] = bool(row.send_sms)
				result["send_otp"] = bool(row.send_otp)
				break

		return result
