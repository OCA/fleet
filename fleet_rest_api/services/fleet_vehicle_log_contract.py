# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.fleet_vehicle_log_contract_info import (
    FleetVehicleLogContractInfo,
)
from ..pydantic_models.fleet_vehicle_log_contract_search_filter import (
    FleetVehicleLogContractSearchFilter,
)


class FleetVehicleLogContractService(Component):
    _inherit = "base.fleet.rest.service"
    _name = "fleet.vehicle.log.contract.rest.service"
    _usage = "vehicle_log_contract"
    _expose_model = "fleet.vehicle.log.contract"
    _collection = "fleet.rest.services"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        output_param=PydanticModel(FleetVehicleLogContractInfo),
        auth="public",
    )
    def get(self, _id: int) -> FleetVehicleLogContractInfo:
        fleet_vehicle_log_contract = self._get(_id)
        return FleetVehicleLogContractInfo.from_orm(fleet_vehicle_log_contract)

    def _get_search_domain(self, filters):
        domain = []
        if filters.id:
            domain.append(("id", "=", filters.id))
        if filters.name:
            domain.append(("name", "like", filters.name))
        if filters.vehicle_id:
            domain.append(("vehicle_id", "=", filters.vehicle_id))
        if filters.user_id:
            domain.append(("user_id", "=", filters.user_id))
        return domain

    @restapi.method(
        routes=[(["/", "/search"], "GET")],
        input_param=PydanticModel(FleetVehicleLogContractSearchFilter),
        output_param=PydanticModelList(FleetVehicleLogContractInfo),
        auth="public",
    )
    def search(
        self,
        fleet_vehicle_log_contract_search_filter: FleetVehicleLogContractSearchFilter,
    ) -> List[FleetVehicleLogContractInfo]:
        domain = self._get_search_domain(fleet_vehicle_log_contract_search_filter)
        res: List[FleetVehicleLogContractInfo] = []
        for e in self.env["fleet.vehicle.log.contract"].sudo().search(domain):
            res.append(FleetVehicleLogContractInfo.from_orm(e))
        return res
