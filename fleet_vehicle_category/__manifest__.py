# Copyright 2020 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Fleet Vehicle Category",
    "summary": "Add category definition for vehicles.",
    "version": "14.0.1.1.1",
    "category": "Human Resources",
    "author": "Stefano Consolaro, Associazione PNLUG - Gruppo Odoo, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/fleet",
    "license": "AGPL-3",
    "depends": ["fleet"],
    "data": ["security/ir.model.access.csv", "views/fleet_vehicle_views.xml"],
    "installable": True,
    "auto_install": False,
}
