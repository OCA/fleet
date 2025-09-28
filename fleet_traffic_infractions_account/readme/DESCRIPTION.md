This module bridges `fleet_traffic_infractions` with Odoo's accounting features.

**Key Features:**

*   Extends the infraction workflow with states for invoicing and billing.
*   Enables the creation of a customer invoice to charge the responsible driver for the fine, plus any additional fees defined in Invoicing Terms.
*   Allows configurable handling of payments to the issuing agency:
    *   Create a standard **Vendor Bill**.
    *   Create a **Miscellaneous Journal Entry** to treat the fine as a direct expense or tax.
*   Adds all necessary fields and views to manage the financial aspects of traffic infractions.