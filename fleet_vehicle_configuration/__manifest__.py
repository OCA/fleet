# Copyright 2022 Camptocamp (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Fleet Vehicle Configuration",
    "version": "16.0.1.0.0",
    "depends": ["fleet"],
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "summary": "add vehicle configuration capacity",
    "website": "https://github.com/OCA/fleet",
    "license": "AGPL-3",
    "category": "Fleet",
    "data": [
        "security/ir.model.access.csv",
        "views/fleet_vehicle.xml",
        "views/fleet_vehicle_configuration.xml",
    ],
    "installable": True,
}
