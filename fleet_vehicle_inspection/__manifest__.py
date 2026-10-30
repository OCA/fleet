# Copyright 2020 - 2025, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Fleet Vehicle Inspection",
    "summary": "Manage vehicle inspections.",
    "version": "20.0.1.0.0",
    "license": "AGPL-3",
    "category": "Fleet",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "maintainers": ["marcelsavegnago"],
    "images": ["static/description/banner.png"],
    "website": "https://github.com/OCA/fleet",
    "depends": ["fleet"],
    "data": [
        "security/ir.access.csv",
        "views/fleet_vehicle_views.xml",
        "views/fleet_vehicle_inspection_line_views.xml",
        "views/fleet_vehicle_inspection_item_views.xml",
        "views/fleet_vehicle_inspection_views.xml",
        "data/fleet_vehicle_inspection.xml",
    ],
    "demo": ["demo/fleet_vehicle_inspection.xml"],
}
