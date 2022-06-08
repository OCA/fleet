# Copyright 2022 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def fill_fleet_vehicle_log_service_service_ids(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO fleet_service_type_fleet_vehicle_log_services_rel
        (fleet_vehicle_log_services_id, fleet_service_type_id)
        SELECT fvls.id, fvc2.cost_subtype_id
        FROM fleet_vehicle_log_services fvls
        JOIN fleet_vehicle_cost fvc ON fvls.cost_id = fvc.id
        JOIN fleet_vehicle_cost fvc2 ON fvc2.parent_id = fvc.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_fleet_vehicle_log_service_service_ids(env)
