# Copyright 2026 Fleet e-Frotas Contributors
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Fleet SENATRAN e-Frotas Connector",
    "summary": """
        Módulo conector e integração com os webservices do e-Frotas SENATRAN / SERPRO:
        Consultas de veículos, CRLV-e digital, infrações, restrições RENAJUD,
        roubo/furto, recall, webhooks e transações (indicação de condutor, boletos).
    """,
    "version": "13.0.1.1.4",
    "category": "Human Resources/Fleet",
    "author": "Fleet Contributors, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/fleet",
    "license": "AGPL-3",
    "development_status": "Beta",
    "depends": [
        "fleet",
        "mail",
    ],
    "external_dependencies": {
        "python": [
            "requests",
            "cryptography",
        ],
    },
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/efrotas_config_views.xml",
        "views/fleet_vehicle_views.xml",
        "views/efrotas_log_views.xml",
        "views/efrotas_query_wizard_views.xml",
        "views/efrotas_menus.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
