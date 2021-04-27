# Copyright 2021 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Fleet Vehicle Maintenance',
    'summary': """
        Integrate Fleet Vehicle with maintenance requests""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Escodoo,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/fleet',
    'depends': [
        'fleet_vehicle_stock',
        'maintenance',
    ],
    'data': [
        'views/maintenance_equipment.xml',
        'views/fleet_vehicle.xml',
    ],
    'demo': [
    ],
}
