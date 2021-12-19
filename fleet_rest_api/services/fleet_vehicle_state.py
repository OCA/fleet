# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.fleet_vehicle_state_info import FleetVehicleStateInfo
from ..pydantic_models.fleet_vehicle_state_search_filter import (
    FleetVehicleStateSearchFilter,
)


class FleetVehicleStateService(Component):
    _inherit = "base.fleet.rest.service"
    _name = "fleet.vehicle.state.rest.service"
    _usage = "vehicle_state"
    _expose_model = "fleet.vehicle.state"
    _collection = "fleet.rest.services"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        output_param=PydanticModel(FleetVehicleStateInfo),
        auth="public",
    )
    def get(self, _id: int) -> FleetVehicleStateInfo:
        fleet_vehicle_state = self._get(_id)
        return FleetVehicleStateInfo.from_orm(fleet_vehicle_state)

    def _get_search_domain(self, filters):
        domain = []
        if filters.id:
            domain.append(("id", "=", filters.id))
        if filters.name:
            domain.append(("name", "like", filters.name))
        return domain

    @restapi.method(
        routes=[(["/", "/search"], "GET")],
        input_param=PydanticModel(FleetVehicleStateSearchFilter),
        output_param=PydanticModelList(FleetVehicleStateInfo),
        auth="public",
    )
    def search(
        self, fleet_vehicle_state_search_filter: FleetVehicleStateSearchFilter
    ) -> List[FleetVehicleStateInfo]:
        domain = self._get_search_domain(fleet_vehicle_state_search_filter)
        res: List[FleetVehicleStateInfo] = []
        for e in self.env["fleet.vehicle.state"].sudo().search(domain):
            res.append(FleetVehicleStateInfo.from_orm(e))
        return res
