import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-fleet",
    description="Meta package for oca-fleet Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-fleet_vehicle_calendar_year',
        'odoo14-addon-fleet_vehicle_category',
        'odoo14-addon-fleet_vehicle_fuel_capacity',
        'odoo14-addon-fleet_vehicle_fuel_type_ethanol',
        'odoo14-addon-fleet_vehicle_history_date_end',
        'odoo14-addon-fleet_vehicle_inspection',
        'odoo14-addon-fleet_vehicle_inspection_template',
        'odoo14-addon-fleet_vehicle_license_plate_alt',
        'odoo14-addon-fleet_vehicle_log_fuel',
        'odoo14-addon-fleet_vehicle_notebook',
        'odoo14-addon-fleet_vehicle_pivot_graph',
        'odoo14-addon-fleet_vehicle_service_calendar',
        'odoo14-addon-fleet_vehicle_service_kanban',
        'odoo14-addon-fleet_vehicle_service_services',
        'odoo14-addon-fleet_vehicle_stock',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
