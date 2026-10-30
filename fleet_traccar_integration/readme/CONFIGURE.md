To configure the integration:

1.  Go to *Fleet > Configuration > Settings*.
2.  In the *Traccar* section, set the Traccar server URL (without `/api`
    at the end), the authentication mode and the credentials.
3.  Use *Test Connection* and *Test API Access* to validate the setup.
4.  Enable the integration and set the synchronization intervals.
5.  Optionally adjust the history limits:
    - *Initial History (days)*: period downloaded for a device without
      telemetry.
    - *Immediate Sync Limit (hours)*: longer gaps are imported in
      background.
    - *Maximum Import Period (days)*: longest period of a manual import.
