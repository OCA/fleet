# Copyright 2025 Raimundo Pereira da Silva Junior, Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Fleet Traffic Infractions",
    "version": "18.0.1.0.0",
    "category": "Fleet",
    "summary": "Manage and track traffic infractions for your fleet vehicles.",
    "author": "Raimundo Pereira da Silva Junior, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/fleet",
    "license": "AGPL-3",
    "depends": [
        "fleet",
        "fleet_vehicle_assignation_log_datetime",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/fleet_traffic_infraction_type_views.xml",
        "views/fleet_traffic_infraction_views.xml",
        "views/fleet_vehicle_views.xml",
        "views/res_partner_views.xml",
        "data/ir_sequence_data.xml",
        "views/fleet_traffic_infraction_menus.xml",
    ],
    "demo": [
        "demo/fleet_traffic_infractions_demo.xml",
    ],
    "installable": True,
}
