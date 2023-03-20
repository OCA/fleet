# Copyright 2020-Present Druidoo - Manuel Marquez <manuel.marquez@druidoo.io>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Kanban Features for Vehicle Services",
    "summary": "Add features of kanban to logs of vehicle services.",
    "category": "Human Resources/Fleet",
    "author": "Druidoo, Odoo Community Association (OCA)",
    "maintainers": ["mamcode", "ivantodorovich"],
    "development_status": "Production/Stable",
    "website": "https://github.com/OCA/fleet",
    "license": "AGPL-3",
    "version": "15.0.1.0.0",
    "depends": ["fleet", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/fleet_vehicle_log_services_stage_data.xml",
        "data/mail_message_subtype_data.xml",
        "views/fleet_vehicle_log_services_views.xml",
        "views/fleet_vehicle_log_services_stage_views.xml",
        "views/fleet_vehicle_log_services_tag_views.xml",
        "views/fleet_service_type_views.xml",
        "views/mail_activity_type_views.xml",
    ],
    "installable": True,
}
