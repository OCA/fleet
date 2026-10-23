This module is an add-on for the Fleet application in Odoo. It adds map
views for the telemetry data provided by `fleet_telemetry`, based on
`fleet_maps` and `web_view_leaflet_map`.

It provides:

- A map view for telemetry records, showing the position of each received
  point.
- Route drawing: telemetry points are grouped by vehicle and route day and
  displayed as colored polylines, with a legend that allows filtering the
  routes by vehicle and by day.
- A **Telemetry Map** menu entry under *Fleet > Configuration > Telemetry*,
  and the leaflet map view added to the telemetry action.
- A default OpenStreetMap tile server URL in the `leaflet.tile_url` system
  parameter, so maps work out of the box.
