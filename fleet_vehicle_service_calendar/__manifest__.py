# Copyright 2020-Present Druidoo - Manuel Marquez <manuel.marquez@druidoo.io>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Scheduling Meetings for Vehicle Services",
    "summary": "Add a smart button in services to schedule meetings.",
    "category": "Human Resources/Fleet",
    "author": "Druidoo, Odoo Community Association (OCA)",
    "maintainers": ["mamcode", "ivantodorovich"],
    "development_status": "Production/Stable",
    "website": "https://github.com/OCA/fleet",
    "license": "AGPL-3",
    "version": "12.0.1.0.1",
    "depends": ["calendar", "fleet_vehicle_service_kanban"],
    "data": [
        "views/fleet_vehicle_log_services_views.xml",
        "views/calendar_event_views.xml",
    ],
    "installable": True,
}
