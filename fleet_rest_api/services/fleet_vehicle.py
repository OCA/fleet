# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.fleet_vehicle_info import FleetVehicleInfo

# from ..pydantic_models.fleet_vehicle_registration_info import FleetVehicleRegistrationInfo
# from ..pydantic_models.fleet_vehicle_registration_request import (
#     FleetVehicleRegistrationRequest,
#     FleetVehicleRegistrationRequestList,
# )
from ..pydantic_models.fleet_vehicle_search_filter import FleetVehicleSearchFilter


class FleetVehicleService(Component):
    _inherit = "base.fleet.rest.service"
    _name = "fleet.vehicle.rest.service"
    _usage = "vehicle"
    _expose_model = "fleet.vehicle"
    _collection = "fleet.rest.services"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        output_param=PydanticModel(FleetVehicleInfo),
        auth="public",
    )
    def get(self, _id: int) -> FleetVehicleInfo:
        fleet_vehicle = self._get(_id)
        return FleetVehicleInfo.from_orm(fleet_vehicle)

    def _get_search_domain(self, filters):
        domain = []
        if filters.id:
            domain.append(("id", "=", filters.id))
        if filters.name:
            domain.append(("name", "like", filters.name))
        return domain

    @restapi.method(
        routes=[(["/", "/search"], "GET")],
        input_param=PydanticModel(FleetVehicleSearchFilter),
        output_param=PydanticModelList(FleetVehicleInfo),
        auth="public",
    )
    def search(
        self, fleet_vehicle_search_filter: FleetVehicleSearchFilter
    ) -> List[FleetVehicleInfo]:
        domain = self._get_search_domain(fleet_vehicle_search_filter)
        res: List[FleetVehicleInfo] = []
        for e in self.env["fleet.vehicle"].sudo().search(domain):
            res.append(FleetVehicleInfo.from_orm(e))
        return res
