import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-fleet",
    description="Meta package for oca-fleet Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-fleet_vehicle_calendar_year>=16.0dev,<16.1dev',
        'odoo-addon-fleet_vehicle_configuration>=16.0dev,<16.1dev',
        'odoo-addon-fleet_vehicle_fuel_capacity>=16.0dev,<16.1dev',
        'odoo-addon-fleet_vehicle_fuel_type_ethanol>=16.0dev,<16.1dev',
        'odoo-addon-fleet_vehicle_inspection>=16.0dev,<16.1dev',
        'odoo-addon-fleet_vehicle_log_fuel>=16.0dev,<16.1dev',
        'odoo-addon-fleet_vehicle_service_calendar>=16.0dev,<16.1dev',
        'odoo-addon-fleet_vehicle_service_kanban>=16.0dev,<16.1dev',
        'odoo-addon-fleet_vehicle_service_services>=16.0dev,<16.1dev',
        'odoo-addon-fleet_vehicle_stock>=16.0dev,<16.1dev',
        'odoo-addon-fleet_vehicle_usage>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
