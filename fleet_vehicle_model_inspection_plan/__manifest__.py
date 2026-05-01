# inspection_plan/__manifest__.py
{
    "name": "Fleet Vehicle Model Inspection Plan",
    "summary": "Define inspection plans per vehicle model (intervals in Odoometer and Months)",
    "version": "13.0.1.0.0",
    "category": "Human Resources/Fleet",
    "website": "https://github.com/OCA/fleet",
    "author": "RPSJR, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["fleet", "fleet_vehicle_inspection"],  # Dependência crucial da OCA
    "data": [
        "security/ir.model.access.csv",
        "wizards/inspection_plan_import_export_views.xml",
        "views/fleet_vehicle_model_views.xml",
        "views/fleet_vehicle_model_inspection_plan_menus.xml",
    ],
    "demo": [
        "demo/fleet_vehicle_model_inspection_plan_demo.xml",
    ],
}
