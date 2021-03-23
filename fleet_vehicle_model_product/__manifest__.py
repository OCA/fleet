# Copyright 2021 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Fleet Vehicle Model Product",
    "summary": """
        Extends the Fleet Module to allow creating relationship products
        and models of vehicles.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "maintainers": ["marcelsavegnago"],
    "website": "https://github.com/OCA/fleet",
    "images": ["static/description/banner.png"],
    "category": "Human Resources/Fleet",
    "depends": ["fleet_product"],
    "data": [
        "views/product_product.xml",
        "views/fleet_vehicle_model.xml",
    ],
}
