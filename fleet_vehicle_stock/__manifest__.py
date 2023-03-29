# Copyright 2021 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Fleet Vehicle Stock",
    "summary": """
        This module is an add-on for the Fleet application in Odoo. It allows
        you to track your Fleet Vehicles in stock moves.""",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/fleet",
    "category": "Human Resources/Fleet",
    "images": ["static/description/banner.png"],
    "maintainers": ["marcelsavegnago"],
    "depends": ["stock", "fleet"],
    "data": [
        "views/stock_production_lot.xml",
        "views/stock_picking_type.xml",
        "views/product_template.xml",
        "views/product_product.xml",
        "views/fleet_vehicle.xml",
        "views/fleet_vehicle_model.xml",
    ],
    "demo": [],
}
