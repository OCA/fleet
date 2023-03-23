# Copyright 2021 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Fleet Vehicle Fuel Capacity",
    "summary": """
        This module extends the functionality of fleet management. It allows the
        registration of a vehicle's fuel capacity.""",
    "version": "15.0.1.0.1",
    "license": "AGPL-3",
    "category": "Human Resources/Fleet",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "maintainers": ["marcelsavegnago"],
    "images": ["static/description/banner.png"],
    "website": "https://github.com/OCA/fleet",
    "depends": [
        "fleet",
    ],
    "data": [
        "views/fleet_vehicle.xml",
    ],
}
