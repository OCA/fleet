import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-fleet",
    description="Meta package for oca-fleet Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-fleet_config',
        'odoo12-addon-fleet_vehicle_calendar_year',
        'odoo12-addon-fleet_vehicle_category',
        'odoo12-addon-fleet_vehicle_fuel_capacity',
        'odoo12-addon-fleet_vehicle_fuel_type_ethanol',
        'odoo12-addon-fleet_vehicle_history_date_end',
        'odoo12-addon-fleet_vehicle_inspection',
        'odoo12-addon-fleet_vehicle_inspection_item_compatible_product',
        'odoo12-addon-fleet_vehicle_inspection_template',
        'odoo12-addon-fleet_vehicle_license_plate_alt',
        'odoo12-addon-fleet_vehicle_model_compatible_product',
        'odoo12-addon-fleet_vehicle_notebook',
        'odoo12-addon-fleet_vehicle_pivot_graph',
        'odoo12-addon-fleet_vehicle_service_calendar',
        'odoo12-addon-fleet_vehicle_service_kanban',
        'odoo12-addon-fleet_vehicle_stock',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 12.0',
    ]
)
