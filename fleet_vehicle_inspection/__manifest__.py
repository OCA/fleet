# Copyright 2020 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Fleet Vehicle Inspection",
    "summary": """
        This module extends the Fleet module allowing the registration
        of vehicle entry and exit inspections.""",
    "version": "14.0.3.0.2",
    "license": "AGPL-3",
    "category": "Human Resources",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "maintainers": ["marcelsavegnago"],
    "images": ["static/description/banner.png"],
    "website": "https://github.com/OCA/fleet",
    "depends": ["fleet"],
    "data": [
        "security/fleet_vehicle_inspection_line_image.xml",
        "views/assets_backend.xml",
        "views/fleet_vehicle.xml",
        "security/fleet_vehicle_inspection_line.xml",
        "views/fleet_vehicle_inspection_line.xml",
        "security/fleet_vehicle_inspection_item.xml",
        "views/fleet_vehicle_inspection_item.xml",
        "security/fleet_vehicle_inspection.xml",
        "views/fleet_vehicle_inspection.xml",
        "data/fleet_vehicle_inspection.xml",
    ],
    "demo": ["demo/fleet_vehicle_inspection.xml"],
}
