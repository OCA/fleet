# Copyright 2021 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Fleet Vehicle Agreement",
    "summary": """
        This is a bridge module between Fleet Vehicle and Agreement
        allows you to link a fleet vehicle to an agreement and adds a smart
        button on the agreement to look at the list of related fleet vehicles.""",
    "version": "14.0.1.0.0",
    "category": "Human Resources/Fleet",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "maintainers": ["marcelsavegnago"],
    "website": "https://github.com/OCA/fleet",
    "images": ["static/description/banner.png"],
    "depends": [
        "fleet",
        "agreement",
    ],
    "data": [
        "views/agreement.xml",
        "views/fleet_vehicle.xml",
    ],
    "demo": [],
}
