# Copyright 2022 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Fleet Vehicle Log Fuel",
    "summary": "Add Log Fuels for your vehicles.",
    "version": "14.0.1.0.1",
    "category": "Human Resources/Fleet",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/fleet",
    "license": "AGPL-3",
    "depends": ["fleet"],
    "data": [
        "security/ir.model.access.csv",
        "security/fleet_security.xml",
        "views/fleet_board_view.xml",
        "views/fleet_vehicle_cost_views.xml",
        "views/fleet_vehicle_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
