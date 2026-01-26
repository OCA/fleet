# Copyright 2020 - 2024, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Fleet Vehicle Inspection",
    "summary": """
        This module extends the Fleet module allowing the registration
        of vehicle entry and exit inspections.""",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "category": "Fleet",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "maintainers": ["marcelsavegnago"],
    "images": ["static/description/banner.png"],
    "website": "https://github.com/OCA/fleet",
    "depends": ["fleet"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/fleet_vehicle.xml",
        "views/fleet_vehicle_inspection_line.xml",
        "views/fleet_vehicle_inspection_item.xml",
        "views/fleet_vehicle_inspection.xml",
        "data/fleet_vehicle_inspection.xml",
    ],
    "demo": ["demo/fleet_vehicle_inspection.xml"],
}
