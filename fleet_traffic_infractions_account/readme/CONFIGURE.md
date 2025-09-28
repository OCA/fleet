This module extends the configuration of `fleet_traffic_infractions`.

1.  **Configure Infraction Types for Accounting:**
    *   Navigate to `Fleet > Configuration > Infraction Types`.
    *   For each type, select a **Fine Product**. This service product is essential for creating invoices and bills.
    *   Ensure the selected product has an **Expense Account** defined on its product form or category, as this will be used when creating journal entries.

2.  **Set the Company-Wide Billing Method:**
    *   Navigate to `Fleet > Configuration > Settings`.
    *   Under the **Traffic Infractions** section, you will find the **Infraction Agency Billing Method**.
    *   Choose one of two options:
        *   **Create Vendor Bill:** This is the default. It will create a standard supplier bill, which is useful for tracking procurement.
        *   **Create Miscellaneous Journal Entry:** This option creates a direct journal entry, debiting the expense account from the fine product and crediting the agency's payable account. This is useful for treating fines as taxes and keeping them out of procurement reports.