# Copyright 2021 César Fernández Domínguez
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Fleet Vehicle Usage",
    "version": "17.0.1.0.0",
    "category": "Human Resources/Fleet",
    "website": "https://github.com/OCA/fleet",
    "author": "César Fernández, Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["fleet"],
    "installable": True,
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence_data.xml",
        "views/fleet_vehicle_usage_view.xml",
        "views/fleet_vehicle_view.xml",
    ],
    "maintainers": ["victoralmau"],
}
