# Copyright 2025 Raimundo Pereira da Silva Junior, Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Fleet Traffic Infractions - Accounting",
    "version": "18.0.1.0.0",
    "category": "Fleet",
    "summary": "Handle invoicing and billing for fleet traffic infractions.",
    "author": "Raimundo Pereira da Silva Junior, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/fleet",
    "license": "AGPL-3",
    "depends": [
        "fleet_traffic_infractions",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/fleet_traffic_infraction_views.xml",
        "views/fleet_traffic_infraction_type_views.xml",
        "views/fleet_traffic_infraction_invoicing_term_views.xml",
    ],
    "installable": True,
}