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
        "security/res_partner.xml",
        "views/res_partner.xml",
        "security/fleet_vehicle.xml",
        "views/fleet_vehicle.xml",
    ],
    "demo": [
        "demo/res_partner.xml",
        "demo/fleet_vehicle.xml",
    ],
}
