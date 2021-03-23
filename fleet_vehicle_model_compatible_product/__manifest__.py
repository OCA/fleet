# Copyright 2021 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Fleet Vehicle Model Compatible Product",
    "summary": """
        This module extends the fleet management functionality. Allows you to define
        which products are compatible with the vehicle model.""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "category": "Human Resources/Fleet",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "maintainers": ["marcelsavegnago"],
    "website": "https://github.com/OCA/fleet",
    "images": ["static/description/banner.png"],
    "depends": [
        "fleet",
        "product",
    ],
    "data": [
        'views/product_template.xml',
        "views/product_product.xml",
        "views/fleet_vehicle_model.xml",
    ],
}
