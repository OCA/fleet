This module provides the core operational foundation for managing traffic infractions. The roadmap includes creating a separate companion module for financial integration.

**Future Module: `fleet_traffic_infractions_account`**

This planned module will extend the functionality of this one to handle all accounting aspects:

*   Create a Vendor Bill from a confirmed infraction, with the "Issuing Agency" as the vendor.
*   Create a Customer Invoice to charge the fine and any administrative fees to the responsible driver.
*   Track the payment status of both the bill and the invoice.
*   Provide a clear link between the infraction record and its corresponding journal entries.