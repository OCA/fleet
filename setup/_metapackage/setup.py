import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-fleet",
    description="Meta package for oca-fleet Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-fleet_vehicle_calendar_year',
        'odoo13-addon-fleet_vehicle_category',
        'odoo13-addon-fleet_vehicle_fuel_capacity',
        'odoo13-addon-fleet_vehicle_fuel_type_ethanol',
        'odoo13-addon-fleet_vehicle_history_date_end',
        'odoo13-addon-fleet_vehicle_inspection',
        'odoo13-addon-fleet_vehicle_inspection_template',
        'odoo13-addon-fleet_vehicle_license_plate_alt',
        'odoo13-addon-fleet_vehicle_notebook',
        'odoo13-addon-fleet_vehicle_pivot_graph',
        'odoo13-addon-fleet_vehicle_service_calendar',
        'odoo13-addon-fleet_vehicle_service_kanban',
        'odoo13-addon-fleet_vehicle_stock',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 13.0',
    ]
)
