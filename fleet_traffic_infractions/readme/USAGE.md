This module is designed to be straightforward. The main workflow is creating and confirming an infraction.

**1. Registering a New Traffic Infraction:**

*   Navigate to `Fleet > Infractions > Traffic Infractions` and click "New".
*   The form is designed for a logical workflow. For the best experience, follow these steps:
    1.  Select the **Vehicle** that received the fine.
    2.  Set the **Infraction Datetime** to the exact date and time the incident occurred.
*   **Automatic Driver Suggestion:** After setting the vehicle and datetime, the **Driver** field will be automatically populated based on the vehicle's assignment logs.
*   Fill in the remaining details of the ticket:
    *   **Infraction Type:** Select the category you configured.
    *   **Infraction Auto Number:** Enter the official ticket or reference number.
    *   **Issuing Agency:** Select the agency that issued the fine.
    *   **Fine Amount** and **Due Date**.
*   You can click **Save** at any time to keep the infraction in a `Draft` state.

**2. Confirming and Managing the Infraction:**

*   Once all details are complete, click the **Confirm** button. The system will verify that all mandatory fields are filled before changing the state to `Confirmed`.
*   **Driver Change Logging:** If the automatically suggested driver is incorrect and you manually change it, a detailed note will be automatically posted in the chatter. This note includes the old and new driver, the infraction time (with the user's timezone), and a comparison against the assignment log, ensuring full traceability.

**3. Accessing Infractions from Other Views:**

*   On a **Vehicle** form, you can use the **"Traffic Infractions"** smart button to see all fines associated with that vehicle.
*   On a **Partner** form, you will see a **"Driver Infractions"** smart button to view all infractions where that partner was the driver.