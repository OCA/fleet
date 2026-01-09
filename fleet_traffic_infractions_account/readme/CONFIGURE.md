This module extends the configuration of `fleet_traffic_infractions`.

1.  **Configure Infraction Types for Accounting:**
    *   Navigate to `Fleet > Configuration > Infraction Types`.
    *   For each type, select a **Fine Product**. This service product is essential for creating invoices and bills and determining the correct expense account.

2.  **Set the Company-Wide Agency Billing Method:**
    *   Navigate to `Fleet > Configuration > Settings`.
    *   Under the **Traffic Infractions** section, choose the default **Infraction Agency Billing Method** (Vendor Bill or Journal Entry).

3.  **Define Driver Invoicing Rules:**
    *   Navigate to `Fleet > Configuration > Invoicing Rules`.
    *   Click "New" to create a rule. Each rule defines a financial policy for a specific group of drivers.
    *   **Name:** Give the rule a clear name (e.g., "Contractor Surcharge," "Employee Default Policy").
    *   **Sequence:** Set the priority. Rules with lower numbers are checked first.
    *   **Applies To Drivers:** Use the domain builder to define which drivers this rule applies to.
        *   *Example: To apply a rule to all drivers in a specific department, you could use a domain like `[('department_id', '=', 'Logistics')]`.*
        *   *Leave the domain empty (`[]`) to create a "catch-all" rule for any driver not matched by a higher-priority rule. This should have the highest sequence number.*
    *   **Action:** Decide whether to invoice the driver or have the company pay.
    *   **Invoice Lines:** If invoicing the driver, you can add extra lines for administrative fees or apply discounts.