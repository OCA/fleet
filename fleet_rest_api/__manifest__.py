# Copyright 2021 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Fleet Rest Api",
    "summary": """Add a REST API to manage events""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "maintainers": ["marcelsavegnago"],
    "website": "https://github.com/OCA/fleet",
    "depends": ["base_rest", "base_rest_pydantic", "fleet"],
    "data": [],
    "demo": [],
    "external_dependencies": {
        "python": [
            "pydantic",
        ]
    },
}
