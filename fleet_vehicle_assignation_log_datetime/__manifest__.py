# Copyright 2025 Raimundo Pereira da Silva Junior, Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Fleet Vehicle Assignation Log Datetime",
    "version": "18.0.1.0.0",
    "category": "Fleet",
    "summary": "Adds datetime precision to driver assignation logs.",
    "author": "Raimundo Pereira da Silva Junior, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/fleet",
    "license": "AGPL-3",
    "depends": [
        "fleet",
        "fleet_vehicle_history_date_end",
    ],
    "data": [
        "views/fleet_vehicle_assignation_log_views.xml",
    ],
    "installable": True,
}
