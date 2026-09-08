This module extends the functionality of fleet management to link each vehicle
to one or more analytic accounts (cost centers), using the same analytic
distribution field used everywhere else in Odoo accounting. It also gives
direct access, from the vehicle form, to every purchase order that shares an
analytic account with the vehicle.

It also makes the analytic accounts of a purchase order, and of its lines,
searchable from the user interface, reusing the `analytic_distribution` field
that `purchase.order` (via the OCA `purchase_analytic` module) and
`purchase.order.line` (natively) already carry. In Odoo that field is stored
as JSON, which is not searchable from a regular search view out of the box.
The `analytic.mixin` it relies on already exposes a computed and searchable
`distribution_analytic_account_ids` Many2many field, which solves the
searchability problem, but not the usability one: Odoo's web client only
shows the "type and pick a suggested record" dropdown (the same one used to
search by Vendor or Product) for fields whose Python type is Many2one; this
is hardcoded in the search bar component and does not depend on the widget
used in the view. Neither a Json field (`analytic_distribution`) nor a
Many2many field (`distribution_analytic_account_ids`) gets that behavior, so
searching by them only supports typing a full or partial name, with no
suggestions to pick from.

To get the same search experience as Vendor or Product, this module adds a
small, non-stored, search-only `analytic_account_id` Many2one field on
`purchase.order` and `purchase.order.line`. It exists only to redirect its
search to `distribution_analytic_account_ids`; it is never stored, read, or
displayed. This field is what gets exposed in the Requests for Quotation,
Purchase Orders, and Purchase Order Lines search views.
