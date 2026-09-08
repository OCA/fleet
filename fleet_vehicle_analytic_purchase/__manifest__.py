# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Fleet Vehicle Analytic Purchase",
    "summary": """
        Link vehicles to analytic accounts (cost centers) and browse the
        purchase orders of those cost centers from the vehicle form.""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "category": "Human Resources/Fleet",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "maintainers": ["marcelsavegnago"],
    "website": "https://github.com/OCA/fleet",
    "depends": [
        "analytic",
        "fleet",
        "purchase",
        "purchase_analytic",
    ],
    "data": [
        "views/fleet_vehicle.xml",
        "views/purchase_order.xml",
    ],
    "installable": True,
    "auto_install": False,
}
