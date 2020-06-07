import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-fleet",
    description="Meta package for oca-fleet Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-fleet_vehicle_category',
        'odoo13-addon-fleet_vehicle_history_date_end',
        'odoo13-addon-fleet_vehicle_license_plate_alt',
        'odoo13-addon-fleet_vehicle_service_calendar',
        'odoo13-addon-fleet_vehicle_service_kanban',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
