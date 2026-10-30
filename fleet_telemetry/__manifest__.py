{
    "name": "Fleet Telemetry",
    "summary": "Generic telemetry storage for fleet vehicles",
    "version": "18.0.1.0.0",
    "category": "Fleet",
    "author": "Ragna, douglascstd@yahoo.com,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/fleet",
    "maintainers": ["douglascstd"],
    "license": "AGPL-3",
    "depends": ["fleet", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/fleet_telemetry_device_views.xml",
        "views/fleet_telemetry_views.xml",
        "views/fleet_telemetry_menu.xml",
    ],
    "application": False,
    "installable": True,
}
