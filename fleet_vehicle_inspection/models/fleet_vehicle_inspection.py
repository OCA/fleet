# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo https://www.escodoo.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class FleetVehicleInspection(models.Model):

    _name = 'fleet.vehicle.inspection'
    _description = 'Fleet Vehicle Inspection'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    READONLY_STATES = {
        'confirmed': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    name = fields.Char(
        'Reference',
        required=True,
        index=True,
        copy=False,
        default='New'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled'),
    ], string='Status',
        copy=False, index=True, readonly=True, track_visibility='onchange',
        default='draft',
        help=" * Draft: not confirmed yet.\n"
             " * Confirmed: inspection has been confirmed.\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore.")

    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        'Vehicle',
        help='Fleet Vehicle',
        required=True,
        states=READONLY_STATES
    )

    odometer_id = fields.Many2one(
        'fleet.vehicle.odometer',
        'Odometer',
        help='Odometer measure of the vehicle at the moment of this log'
    )

    odometer = fields.Float(
        compute="_get_odometer",
        inverse='_set_odometer',
        string='Last Odometer',
        help='Odometer measure of the vehicle at the moment of this log',
        stored=True,
        states=READONLY_STATES,
    )

    odometer_unit = fields.Selection([
        ('kilometers', 'Kilometers'),
        ('miles', 'Miles')
    ], 'Odometer Unit', default='kilometers',
        required=True,
        states=READONLY_STATES,
    )

    date_inspected = fields.Datetime(
        'Inspection Date',
        required=True,
        default=fields.Datetime.now,
        help='Date when the vehicle has been inspected',
        copy=False,
        states=READONLY_STATES,
    )

    inspected_by = fields.Many2one(
        'res.partner',
        'Inspected By',
        track_visibility="onchange",
        help='Inspected By',
        states=READONLY_STATES,
    )

    direction = fields.Selection(
        selection=[('in', 'IN'),
                   ('out', 'OUT')],
        default='out',
        states=READONLY_STATES,
    )

    note = fields.Html('Notes', states=READONLY_STATES)

    inspection_line_ids = fields.One2many(
        'fleet.vehicle.inspection.line',
        'inspection_id',
        string='Inspection Lines',
        copy=True,
        auto_join=True,
        states=READONLY_STATES,
    )

    result = fields.Selection([
        ('todo', 'Todo'),
        ('success', 'Success'),
        ('failure', 'Failure')
    ], 'Inspection Result',
        default='todo',
        compute="_compute_inspection_result",
        readonly=True,
        copy=False,
        store=True,
        help='Inspection Result',
    )

    @api.depends('inspection_line_ids', 'state')
    def _compute_inspection_result(self):
        for inspection in self:
            if inspection.inspection_line_ids:
                if (inspection.inspection_line_ids.filtered(
                        lambda x: x.result == 'todo')):
                    inspection.result = 'todo'
                    continue
                elif (inspection.inspection_line_ids.filtered(
                        lambda x: x.result == 'failure')):
                    inspection.result = 'failure'
                else:
                    inspection.result = 'success'
            else:
                inspection.result = 'todo'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            if vals.get('direction') == 'out':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'fleet.vehicle.inspection.out') or '/'
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'fleet.vehicle.inspection.in') or '/'
        return super(FleetVehicleInspection, self).create(vals)

    @api.multi
    def button_cancel(self):
        for inspection in self:
            if inspection.state not in ['draft', 'confirmed']:
                continue
            inspection.write({'state': 'cancel'})
        return True

    @api.multi
    def button_confirm(self):
        for inspection in self:
            if inspection.inspection_line_ids:
                if inspection.state not in ['draft', 'cancel']:
                    continue
                if (inspection.inspection_line_ids.filtered(
                        lambda x: x.result == 'todo')):
                    raise UserError(_(
                        'Inspection cannot be completed. There are uninspected items.'
                    ))
                inspection.write({'state': 'confirmed'})
            else:
                raise UserError(_(
                    'Inspection cannot be completed. There are no inspected items.'
                ))
        return True

    @api.multi
    def button_draft(self):
        for inspection in self:
            inspection.write({'state': 'draft'})
            inspection.write({'result': 'todo'})
        return True

    def _get_odometer(self):
        for record in self:
            if record.odometer_id:
                record.odometer = record.odometer_id.value

    def _set_odometer(self):
        for record in self:
            if not record.odometer:
                raise UserError(_('Emptying the odometer value of a '
                                  'vehicle is not allowed.'))
            odometer = self.env['fleet.vehicle.odometer'].create({
                'value': record.odometer,
                'date': record.date_inspected or fields.Date.context_today(record),
                'vehicle_id': record.vehicle_id.id
            })
            self.odometer_id = odometer
