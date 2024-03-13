# Copyright 2023 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Create an activity to vehicle fleet manager days before service date",
    "summary": "Activity alerts for fleet services",
    "category": "Human Resources/Fleet",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "development_status": "Production/Stable",
    "website": "https://github.com/OCA/fleet",
    "license": "AGPL-3",
    "version": "16.0.1.0.0",
    "depends": ["fleet"],
    "data": [
        "data/fleet_data.xml",
        "data/mail_data.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
