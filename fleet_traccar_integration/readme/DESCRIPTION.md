This module is an add-on for the Fleet application in Odoo. It connects
fleet vehicles with a Traccar server to synchronize tracking devices and
their telemetry:

- Per-company Traccar configuration: server URL, authentication (basic,
  session or token), synchronization intervals and initial history days.
- Devices: `traccar.device` model linked to a `fleet.vehicle` and to a
  `fleet.telemetry.device`, created remotely on Traccar when needed.
- Telemetry: positions are synchronized into `fleet.telemetry` records
  (provider `traccar`), keeping GPS date, coordinates, speed, course,
  altitude, address and the provider attributes.
- Synchronization can run from a cron job or on demand from the vehicle
  form, the device form or the settings.
- History imports: long periods are downloaded in background, one day
  per device at a time, with progress, notification, cancel and resume.
- Smart button on the vehicle form to browse its telemetry points, using
  the map view when `fleet_telemetry_maps` is installed.
