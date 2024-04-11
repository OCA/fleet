# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Fleet Vehicle Purchase",
    "summary": """
        Allow to integrate Purcase with Fleet Vehicles""",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "author": "Dixmit,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/fleet",
    "depends": [
        "account_fleet",
        "purchase",
    ],
    "data": [
        "views/fleet_vehicle.xml",
        "views/purchase_order.xml",
    ],
    "demo": [],
}
