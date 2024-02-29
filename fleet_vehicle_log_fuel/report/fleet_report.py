# Copyright 2022 ForgeFlow S.L.  <https://www.forgeflow.com>
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from psycopg2 import sql

from odoo import fields, models, tools


class FleetReport(models.Model):
    _inherit = "fleet.vehicle.cost.report"

    cost_type = fields.Selection(selection_add=[("fuel", "Fuel")])

    def init(self):
        """Inject parts in the query with this hack, fetching the query and
        recreating it. Query is returned all in upper case and with final ';'.
        """
        super().init()
        self.env.cr.execute(f"SELECT pg_get_viewdef('{self._table}', true)")
        view_def = self.env.cr.fetchone()[0]
        if view_def[-1] == ";":  # Remove trailing semicolon
            view_def = view_def[:-1]
        # Subquery
        view_def = view_def.replace(
            "contract_costs AS (",
            """
            fuel_costs AS (
                SELECT
                    ve.id AS vehicle_id,
                    ve.company_id AS company_id,
                    ve.name AS name,
                    ve.driver_id AS driver_id,
                    ve.fuel_type AS fuel_type,
                    date(date_trunc('month', d)) AS date_start,
                    vem.vehicle_type as vehicle_type,
                    COALESCE(sum(fvlf.amount), 0) AS cost,
                    'fuel' AS cost_type
                FROM
                    fleet_vehicle ve
                JOIN
                    fleet_vehicle_model vem ON vem.id = ve.model_id
                CROSS JOIN generate_series(
                    (
                        SELECT min(date)
                        FROM fleet_vehicle_log_fuel),
                    CURRENT_DATE + '1 month'::interval, '1 month') d
                LEFT JOIN fleet_vehicle_log_fuel fvlf ON fvlf.vehicle_id = ve.id
                    AND date_trunc('month', fvlf.date) = date_trunc('month', d)
                WHERE
                    ve.active AND fvlf.active AND fvlf.state <> 'cancelled'
                GROUP BY ve.id, ve.company_id, ve.name, vem.vehicle_type, date_start, d
                ORDER BY ve.id, date_start
            ),
            contract_costs AS (""",
        )
        # Union
        view_def = view_def.replace(
            "UNION ALL",
            """
            UNION ALL
                SELECT
                    fc.company_id,
                    fc.vehicle_id,
                    fc.name,
                    fc.driver_id,
                    fc.fuel_type,
                    fc.date_start,
                    fc.vehicle_type,
                    fc.cost,
                    'fuel' as cost_type
                FROM
                    fuel_costs fc
            UNION ALL""",
        )
        # Re-create view
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            sql.SQL("""CREATE or REPLACE VIEW {} as ({})""").format(
                sql.Identifier(self._table), sql.SQL(view_def)
            )
        )
        return True
