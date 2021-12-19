# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.fleet_vehicle_tag_info import FleetVehicleTagInfo
from ..pydantic_models.fleet_vehicle_tag_search_filter import (
    FleetVehicleTagSearchFilter,
)


class FleetVehicleTagService(Component):
    _inherit = "base.fleet.rest.service"
    _name = "fleet.vehicle.tag.rest.service"
    _usage = "vehicle_tag"
    _expose_model = "fleet.vehicle.tag"
    _collection = "fleet.rest.services"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        output_param=PydanticModel(FleetVehicleTagInfo),
        auth="public",
    )
    def get(self, _id: int) -> FleetVehicleTagInfo:
        fleet_vehicle_tag = self._get(_id)
        return FleetVehicleTagInfo.from_orm(fleet_vehicle_tag)

    def _get_search_domain(self, filters):
        domain = []
        if filters.id:
            domain.append(("id", "=", filters.id))
        if filters.name:
            domain.append(("name", "like", filters.name))
        return domain

    @restapi.method(
        routes=[(["/", "/search"], "GET")],
        input_param=PydanticModel(FleetVehicleTagSearchFilter),
        output_param=PydanticModelList(FleetVehicleTagInfo),
        auth="public",
    )
    def search(
        self, fleet_vehicle_tag_search_filter: FleetVehicleTagSearchFilter
    ) -> List[FleetVehicleTagInfo]:
        domain = self._get_search_domain(fleet_vehicle_tag_search_filter)
        res: List[FleetVehicleTagInfo] = []
        for e in self.env["fleet.vehicle.tag"].sudo().search(domain):
            res.append(FleetVehicleTagInfo.from_orm(e))
        return res
