
import base64
import csv
import io
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class InspectionPlanImportExport(models.TransientModel):
    _name = 'inspection.plan.import.export'
    _description = 'Inspection Plan Import/Export Wizard'

    operation = fields.Selection([
        ('import', 'Import'),
        ('export', 'Export')
    ], string='Operation', default='export', required=True)

    file_data = fields.Binary(string='File')
    filename = fields.Char(string='Filename')

    def action_process(self):
        if self.operation == 'export':
            return self._export_plans()
        else:
            return self._import_plans()

    def _export_plans(self):
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        # Headers
        headers = ['Model', 'Brand', 'Inspection Item', 'Interval (KM)', 'Interval (Months)']
        writer.writerow(headers)
        
        plans = self.env['fleet.vehicle.model.inspection.plan'].search([])
        
        for plan in plans:
            writer.writerow([
                plan.model_id.name,
                plan.model_id.brand_id.name if plan.model_id.brand_id else '',
                plan.item_id.name,
                plan.interval_km,
                plan.interval_months
            ])
            
        content = base64.b64encode(output.getvalue().encode('utf-8'))
        self.write({
            'file_data': content,
            'filename': 'inspection_plans.csv'
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'inspection.plan.import.export',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    def _import_plans(self):
        if not self.file_data:
            raise UserError(_("Please upload a file to import."))
            
        try:
            data = base64.b64decode(self.file_data).decode('utf-8')
            csv_data = csv.reader(io.StringIO(data), delimiter=';')
            next(csv_data) # Skip header
        except Exception:
            raise UserError(_("Invalid file format."))
            
        for row in csv_data:
            if len(row) < 5:
                continue
                
            model_name = row[0]
            brand_name = row[1]
            item_name = row[2]
            interval_km = int(row[3])
            interval_months = int(row[4])
            
            brand = False
            # Find or create model
            model_domain = [('name', '=', model_name)]
            if brand_name:
                brand = self.env['fleet.vehicle.model.brand'].search([('name', '=', brand_name)], limit=1)
                if not brand:
                     brand = self.env['fleet.vehicle.model.brand'].create({'name': brand_name})
                model_domain.append(('brand_id', '=', brand.id))
            
            model = self.env['fleet.vehicle.model'].search(model_domain, limit=1)
            if not model:
                # Basic creation if not found. Might need more fields in real scenario
                model_vals = {'name': model_name}
                if brand:
                    model_vals['brand_id'] = brand.id
                model = self.env['fleet.vehicle.model'].create(model_vals)
                
            # Find item
            item = self.env['fleet.vehicle.inspection.item'].search([('name', '=', item_name)], limit=1)
            if not item:
                # Optionally create item or skip
                item = self.env['fleet.vehicle.inspection.item'].create({'name': item_name})

            # Search for existing plan to update or create new
            plan = self.env['fleet.vehicle.model.inspection.plan'].search([
                ('model_id', '=', model.id),
                ('item_id', '=', item.id)
            ], limit=1)
            
            vals = {
                'model_id': model.id,
                'item_id': item.id,
                'interval_km': interval_km,
                'interval_months': interval_months,
            }
            
            if plan:
                plan.write(vals)
            else:
                self.env['fleet.vehicle.model.inspection.plan'].create(vals)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
