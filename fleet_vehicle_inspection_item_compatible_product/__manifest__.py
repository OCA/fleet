# Copyright 2021 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Fleet Vehicle Inspection Item Compatible Product',
    'summary': """
        This module extends the fleet management functionality. Allows you to define
        which products are compatible with inspection itens.""",
    'version': '12.0.1.0.0',
    'category': 'Human Resources/Fleet',
    'license': 'AGPL-3',
    'author': 'Escodoo,Odoo Community Association (OCA)',
    'maintainers': ['marcelsavegnago'],
    'images': ['static/description/banner.png'],
    'website': 'https://github.com/OCA/fleet',
    'depends': [
        'fleet_vehicle_model_compatible_product',
        'fleet_vehicle_inspection',
    ],
    'data': [
        'views/fleet_vehicle_inspection_item.xml',
        'views/product_product.xml',
    ],
    'demo': [
    ],
}
