import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-fleet",
    description="Meta package for oca-fleet Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-fleet_vehicle_category',
        'odoo14-addon-fleet_vehicle_history_date_end',
        'odoo14-addon-fleet_vehicle_inspection',
        'odoo14-addon-fleet_vehicle_inspection_template',
        'odoo14-addon-fleet_vehicle_service_kanban',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
