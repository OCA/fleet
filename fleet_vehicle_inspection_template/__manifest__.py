# Copyright 2021 to TODAY, Escodoo (https://www.escodoo.com.br)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Fleet Vehicle Inspection Template",
    "summary": """
        This module extend module fleet_vehicle_inspection enable
        inspection templates feature""",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "author": "Escodoo, Odoo Community Association (OCA)",
    "category": "Human Resources",
    "maintainers": ["marcelsavegnago"],
    "images": ["static/description/banner.png"],
    "website": "https://github.com/OCA/fleet",
    "depends": ["fleet_vehicle_inspection"],
    "data": [
        "views/fleet_vehicle_inspection_template_line.xml",
        "security/fleet_vehicle_inspection_template_line.xml",
        "security/fleet_vehicle_inspection_template.xml",
        "views/fleet_vehicle_inspection_template.xml",
        "views/fleet_vehicle_inspection.xml",
    ],
    "demo": ["demo/fleet_vehicle_inspection_template.xml"],
}
