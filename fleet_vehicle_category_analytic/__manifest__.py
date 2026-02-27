# Copyright 2026 Arnaud Layec (<arnaud.layec@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Fleet Vehicle Analytic",
    "summary": """
        Define Analytic Account per vehicle category
    """,
    "version": "18.0.1.0.0",
    "category": "Human Resources",
    "author": "Arnaud Layec, Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/fleet",
    "license": "AGPL-3",
    "depends": ["account_fleet", "fleet_vehicle_category"],
    "data": ["views/fleet_vehicle_category_views.xml"],
    "installable": True,
    "auto_install": False,
}
