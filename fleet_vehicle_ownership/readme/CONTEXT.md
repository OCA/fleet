This is an extension of the 'fleet.vehicle' model in the Odoo framework.
It introduces a new field, 'owner_id', to track and associate the owner of a
vehicle.

Fields:
- owner_id: Many2one field linking to the 'res.partner' model. It represents
  the owner of the vehicle.

Usage:
- This extension is particularly useful in scenarios where it's essential to
associate each fleet vehicle with a specific owner.
- The 'owner_id' field can be utilized to establish relationships with
partners in the 'res.partner' model, facilitating clear ownership tracking.
