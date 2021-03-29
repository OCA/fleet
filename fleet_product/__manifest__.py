# Copyright 2021 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Fleet Product",
    "summary": """
        This module is a bridge between Fleet and Product.""",
    "version": "12.0.1.0.0",
    "category": "Human Resources/Fleet",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "maintainers": ["marcelsavegnago"],
    "images": ["static/description/banner.png"],
    "website": "https://github.com/OCA/fleet",
    "depends": [
        "fleet",
        "product",
    ],
    "data": [
        "views/product_template.xml",
        "views/product_product.xml",
    ],
    "demo": [],
}
