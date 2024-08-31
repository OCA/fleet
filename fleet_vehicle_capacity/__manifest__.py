# Copyright 2024 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Fleet Vehicle Capacity",
    "summary": """
        Add capacity fields to vehicles""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "maintainers": ["marcelsavegnago"],
    "website": "https://github.com/OCA/fleet",
    "depends": [
        "fleet",
        "uom",
    ],
    "data": [
        "views/res_config_settings.xml",
        "views/fleet_vehicle_model.xml",
        "views/fleet_vehicle.xml",
    ],
    "demo": [],
}
