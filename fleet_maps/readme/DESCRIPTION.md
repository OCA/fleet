This module is an add-on for the Fleet application in Odoo. It adds a
generic map view for fleet vehicles, based on the OCA `web_view_leaflet_map`
module.

It provides:

- A `leaflet_map` view for vehicles, using stored map fields: latitude,
  longitude, marker title, marker address and last update.
- A **Fleet Map** action and menu entry under *Fleet > Vehicles*, showing
  only the vehicles that have a position.
- A smart button and a *Map* page in the vehicle form, with an embedded
  OpenStreetMap preview.

This module does not compute positions by itself: position data is provided
by modules overriding `_get_map_position_values()`, for example telemetry
integrations.
