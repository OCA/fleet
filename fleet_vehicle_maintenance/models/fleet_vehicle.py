# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class FleetVehicle(models.Model):

    _inherit = 'fleet.vehicle'

    maintenance_equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='Related Maintenance Equipment',
    )

    maintenance_count = fields.Integer(
        string='aintenance Count',
        related='maintenance_equipment_id.maintenance_count',
    )

    @api.multi
    def action_view_maintenance(self):
        for vehicle in self:
            maintenance_request_ids = self.env['maintenance.request'].search(
                [('equipment_id', '=', vehicle.maintenance_equipment_id.id)])
            action = self.env.ref(
                'maintenance.hr_equipment_request_action_from_equipment').read()[0]
            action['context'] = {}
            if len(maintenance_request_ids) == 1:
                action['views'] = [(
                    self.env.ref('maintenance.hr_equipment_request_view_form').id,
                    'form')]
                action['res_id'] = maintenance_request_ids.ids[0]
                action['context'].update({'default_equipment_id': self.maintenance_equipment_id.id})
            else:
                action['domain'] = [('id', 'in', maintenance_request_ids.ids)]
                action['context'].update({'search_default_is_open': 1,
                                          'default_equipment_id': self.maintenance_equipment_id.id})
            return action



    @api.model
    def create(self, vals):
        model_id = vals.get('model_id', False)
        vehicle_model = self.env['fleet.vehicle.model'].browse(model_id),
        vehicle_name = vehicle_model[0].brand_id.name + '/' + vehicle_model[0].name + '/' + (
                vals.get('license_plate', False) or _('No Plate'))
        lot_id = vals.get('lot_id', False)
        maintenance_equipment_id = self.env['maintenance.equipment'].create({
            'name': vehicle_name or 'New Vehicle',
            'is_fleet_vehicle': True,
            'note': vals.get('notes', False),
            'serial_no':
                lot_id and
                self.env['stock.production.lot'].browse(lot_id).name,
            'maintenance_team_id':
                vals.get('maintenance_team_id', False) or
                self.env.ref('maintenance.equipment_team_maintenance').id})
        if maintenance_equipment_id:
            vals.update({
                'maintenance_equipment_id': maintenance_equipment_id.id})
        return super().create(vals)

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if 'model_id' or 'license_plate' in vals:
            self.maintenance_equipment_id.write({'name': self.name})
        return res

    @api.multi
    def unlink(self):
        equipments = self.mapped('maintenance_equipment_id')
        res = super(FleetVehicle, self).unlink()
        for equipment in equipments:
            other = self.env['fleet.vehicle'].search(
                [('maintenance_equipment_id', '=', equipment.id)])
            if not other:
                equipment.is_fleet_vehicle = False
        return res
