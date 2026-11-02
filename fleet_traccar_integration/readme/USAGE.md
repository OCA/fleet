Once configured and enabled, the cron job synchronizes devices and
telemetry automatically. It can also be triggered manually:

- From *Fleet > Configuration > Traccar > Devices*, with the *Update
  Status* and *Import History* buttons.
- From a vehicle form, in the *Traccar* page, with the *Update
  Locations* and *Import History* buttons.

*Import History* asks for the period to download (today, yesterday, last
7 or 30 days, since the last stored point or a custom period) and runs
in background, one day per device at a time:

- Follow the imports in *Fleet > Configuration > Traccar > History
  Imports*, or with the smart button of the device. Each import shows
  its progress, the points created and updated and the last processed
  date.
- The user is notified when the import finishes or fails. A failed or
  cancelled import can be resumed from the last processed day.
- Only one import per device runs at a time: asking for a new one opens
  the import in progress.

*Update Locations* and the cron job download the positions received
since the last stored point. When this gap is longer than the
*Immediate Sync Limit*, a history import is created instead, so the
synchronization never blocks the user.

Received positions are stored in *Fleet > Configuration > Traccar >
Telemetry*.
