# Copyright 2021 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Fleet Vehicle Pivot and Graph View',
    'summary': """
        This module extends the fleet management functionality. Adds the pivot
        table and graph view to the fleet vehicles.""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Human Resources/Fleet',
    'author': 'Escodoo,Odoo Community Association (OCA)',
    'maintainers': ['marcelsavegnago'],
    'images': ['static/description/banner.png'],
    'website': 'https://github.com/OCA/fleet',
    'depends': [
        'fleet',
    ],
    'data': [
        'views/fleet_vehicle.xml',
    ],
}
