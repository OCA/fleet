# Copyright 2022 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def fill_fleet_vehicle_log_fuel_fields(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE
            fleet_vehicle_log_fuel as fvlf
        SET
            vehicle_id = fvc.vehicle_id,
            amount = fvc.amount,
            company_id = fvc.company_id,
            odometer_id = fvc.odometer_id,
            description = fvc.description,
            date = fvc.date,
            service_type_id = fvc.cost_subtype_id
        FROM
            fleet_vehicle_cost as fvc
        WHERE
            fvc.id =  fvlf.cost_id
        """,
    )


def set_fleet_vehicle_log_fuel_state(env):
    """Set all records to 'done', as it was the supposed option in v13"""
    openupgrade.logged_query(env.cr, "UPDATE fleet_vehicle_log_fuel SET state = 'done'")


@openupgrade.migrate()
def migrate(env, version):
    fill_fleet_vehicle_log_fuel_fields(env)
    set_fleet_vehicle_log_fuel_state(env)
