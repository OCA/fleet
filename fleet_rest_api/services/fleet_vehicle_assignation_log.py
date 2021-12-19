# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.fleet_vehicle_assignation_log_info import FleetVehicleAssignationLogInfo
from ..pydantic_models.fleet_vehicle_assignation_log_search_filter import (
    FleetVehicleAssignationLogSearchFilter,
)


class FleetVehicleAssignationLogService(Component):
    _inherit = "base.fleet.rest.service"
    _name = "fleet.vehicle.assignation.log.rest.service"
    _usage = "vehicle_assignation_log"
    _expose_model = "fleet.vehicle.assignation.log"
    _collection = "fleet.rest.services"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        output_param=PydanticModel(FleetVehicleAssignationLogInfo),
        auth="public",
    )
    def get(self, _id: int) -> FleetVehicleAssignationLogInfo:
        fleet_vehicle_assignation_log = self._get(_id)
        return FleetVehicleAssignationLogInfo.from_orm(fleet_vehicle_assignation_log)

    def _get_search_domain(self, filters):
        domain = []
        if filters.id:
            domain.append(("id", "=", filters.id))
        if filters.vehicle_id:
            domain.append(("vehicle_id", "=", filters.vehicle_id))
        if filters.driver_id:
            domain.append(("driver_id", "=", filters.driver_id))
        return domain

    @restapi.method(
        routes=[(["/", "/search"], "GET")],
        input_param=PydanticModel(FleetVehicleAssignationLogSearchFilter),
        output_param=PydanticModelList(FleetVehicleAssignationLogInfo),
        auth="public",
    )
    def search(
        self, fleet_vehicle_assignation_log_search_filter: FleetVehicleAssignationLogSearchFilter
    ) -> List[FleetVehicleAssignationLogInfo]:
        domain = self._get_search_domain(fleet_vehicle_assignation_log_search_filter)
        res: List[FleetVehicleAssignationLogInfo] = []
        for e in self.env["fleet.vehicle.assignation.log"].sudo().search(domain):
            res.append(FleetVehicleAssignationLogInfo.from_orm(e))
        return res
