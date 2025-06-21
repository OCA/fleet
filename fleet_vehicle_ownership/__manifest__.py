# Copyright 2023 RPSJR
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Fleet Vehicle Ownership",
    "summary": "Add vehicle ownership, linking partners to vehicles",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "RPSJR,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/fleet",
    "maintainers": ["cubells"],
    "depends": ["fleet"],
    "data": [
        "views/res_partner_views.xml",
        "views/fleet_vehicle_views.xml",
    ],
    "demo": [
        "demo/fleet_vehicle.xml",
    ],
}
