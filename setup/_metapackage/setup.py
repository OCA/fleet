import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-fleet",
    description="Meta package for oca-fleet Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-fleet_vehicle_calendar_year>=16.0dev,<16.1dev',
        'odoo-addon-fleet_vehicle_fuel_capacity>=16.0dev,<16.1dev',
        'odoo-addon-fleet_vehicle_fuel_type_ethanol>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
