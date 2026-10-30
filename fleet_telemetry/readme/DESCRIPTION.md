This module is an add-on for the Fleet application in Odoo. It provides a
generic, provider-agnostic storage for vehicle telemetry (GPS positions
and tracker data), so that integration modules for specific tracking
platforms can feed positions into Odoo using a common data model.

It adds:

- **Telemetry Devices**: the trackers installed in the vehicles,
  identified by their provider and external reference, and linked to a
  fleet vehicle.
- **Telemetry**: the positions received from the devices, with GPS and
  server dates, latitude, longitude, speed, course, altitude, address
  and a JSON field to keep any extra attribute sent by the provider. The
  route day is computed from the GPS date to ease filtering and grouping
  of the vehicle routes.

The uniqueness of devices and positions is enforced per company and
provider, and a helper method allows merging duplicated positions
received for the same device, date and coordinates.

This module intentionally does not depend on any map rendering addon.
