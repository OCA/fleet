# Copyright 2023 RPSJR
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Fleet Vehicle Ownership",
    "summary": "Add vehicle ownership, linking partners to vehicles",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "RPSJR,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/fleet",
    "depends": ["fleet"],
    "data": [
        "views/res_partner.xml",
        "views/fleet_vehicle.xml",
    ],
    "demo": [
        "demo/fleet_vehicle.xml",
    ],
}
