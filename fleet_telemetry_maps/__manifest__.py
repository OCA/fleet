{
    "name": "Fleet Telemetry Maps",
    "summary": "Map views for generic fleet telemetry",
    "version": "18.0.1.1.0",
    "category": "Fleet",
    "author": "Ragna, douglascstd@yahoo.com, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/fleet",
    "maintainers": ["douglascstd"],
    "license": "AGPL-3",
    "depends": ["fleet_telemetry", "fleet_maps", "web_view_leaflet_map"],
    "data": [
        "data/ir_config_parameter.xml",
        "views/fleet_telemetry_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "fleet_telemetry_maps/static/src/views/leaflet_map/fleet_telemetry_route_map_patch.esm.js",
            "fleet_telemetry_maps/static/src/views/leaflet_map/leaflet_map_search_bar_patch.esm.js",
            "fleet_telemetry_maps/static/src/views/leaflet_map/leaflet_map_controller.xml",
            "fleet_telemetry_maps/static/src/search/telemetry_period_filter_patch.esm.js",
        ],
    },
    "application": False,
    "installable": True,
}
