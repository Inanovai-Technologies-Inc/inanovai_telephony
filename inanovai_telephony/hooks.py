app_name = "inanovai_telephony"
app_title = "Inanovai Telephony Integration"
app_publisher = "Akshitha"
app_description = "Custom Twilio and Frappe CRM/Telephony integration"
app_email = "akshitha.nr@inanovai.com"
app_license = "mit"
required_apps = ["crm", "telephony"]

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "inanovai_telephony",
# 		"logo": "/assets/inanovai_telephony/logo.png",
# 		"title": "Inanovai Telephony Integration",
# 		"route": "/inanovai_telephony",
# 		"has_permission": "inanovai_telephony.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/inanovai_telephony/css/inanovai_telephony.css"
# app_include_js = "/assets/inanovai_telephony/js/inanovai_telephony.js"

# include js, css files in header of web template
# web_include_css = "/assets/inanovai_telephony/css/inanovai_telephony.css"
# web_include_js = "/assets/inanovai_telephony/js/inanovai_telephony.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "inanovai_telephony/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "inanovai_telephony/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "inanovai_telephony.utils.jinja_methods",
# 	"filters": "inanovai_telephony.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "inanovai_telephony.install.before_install"
# after_install = "inanovai_telephony.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "inanovai_telephony.uninstall.before_uninstall"
# after_uninstall = "inanovai_telephony.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "inanovai_telephony.utils.before_app_install"
# after_app_install = "inanovai_telephony.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "inanovai_telephony.utils.before_app_uninstall"
# after_app_uninstall = "inanovai_telephony.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "inanovai_telephony.notifications.get_notification_config"

# Awesome Bar
# -----------
# Extra search results: list of dicts with label, description, route, index.
# route: ["List", "ToDo"], "/desk/docs/some/page", or "https://example.com"
# awesomebar_search = ["inanovai_telephony.search.awesomebar_results"]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"inanovai_telephony.tasks.all"
# 	],
# 	"daily": [
# 		"inanovai_telephony.tasks.daily"
# 	],
# 	"hourly": [
# 		"inanovai_telephony.tasks.hourly"
# 	],
# 	"weekly": [
# 		"inanovai_telephony.tasks.weekly"
# 	],
# 	"monthly": [
# 		"inanovai_telephony.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "inanovai_telephony.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "inanovai_telephony.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "inanovai_telephony.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["inanovai_telephony.utils.before_request"]
# after_request = ["inanovai_telephony.utils.after_request"]

# Job Events
# ----------
# before_job = ["inanovai_telephony.utils.before_job"]
# after_job = ["inanovai_telephony.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"inanovai_telephony.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []
app_include_js = [
    "/assets/inanovai_telephony/js/twilio.min.js",
]

doctype_js = {
    "Lead": "public/js/lead_telephony.js",
    "Purchase Order": "public/js/purchase_order_telephony.js",
}
