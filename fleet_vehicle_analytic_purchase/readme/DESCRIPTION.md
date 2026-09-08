This module extends the functionality of fleet management to link each vehicle
to one or more analytic accounts (cost centers), using the same analytic
distribution field used everywhere else in Odoo accounting. It also gives
direct access, from the vehicle form, to every purchase order that shares an
analytic account with the vehicle.

It also makes the analytic accounts of a purchase order searchable from the
user interface, reusing the `analytic_distribution` field that the OCA
`purchase_analytic` module already adds on the purchase order header. In Odoo
that field is stored as JSON, which is not searchable from a regular search
view out of the box; the `analytic.mixin` it relies on already solves that by
exposing a computed and searchable `distribution_analytic_account_ids` field,
which this module simply adds to the Requests for Quotation and Purchase
Orders search views.
