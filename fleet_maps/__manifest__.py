{
    "name": "Fleet Maps",
    "summary": "Generic map view for fleet vehicles",
    "version": "18.0.1.0.0",
    "category": "Fleet",
    "author": "Ragna, douglascstd@yahoo.com, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/fleet",
    "maintainers": ["douglascstd"],
    "license": "AGPL-3",
    "depends": ["fleet", "web_view_leaflet_map"],
    "data": [
        "views/fleet_vehicle_views.xml",
        "views/fleet_maps_menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "fleet_maps/static/src/views/leaflet_map/fleet_leaflet_map_patch.esm.js",
            "fleet_maps/static/src/views/leaflet_map/fleet_leaflet_map_controller.xml",
        ],
    },
    "application": False,
    "installable": True,
}
