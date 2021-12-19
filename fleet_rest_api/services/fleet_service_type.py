# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.fleet_service_type_info import FleetServiceTypeInfo
from ..pydantic_models.fleet_service_type_search_filter import (
    FleetServiceTypeSearchFilter,
)


class FleetServiceTypeService(Component):
    _inherit = "base.fleet.rest.service"
    _name = "fleet.service.type.rest.service"
    _usage = "service_type"
    _expose_model = "fleet.service.type"
    _collection = "fleet.rest.services"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        output_param=PydanticModel(FleetServiceTypeInfo),
        auth="public",
    )
    def get(self, _id: int) -> FleetServiceTypeInfo:
        fleet_tag = self._get(_id)
        return FleetServiceTypeInfo.from_orm(fleet_tag)

    def _get_search_domain(self, filters):
        domain = []
        if filters.id:
            domain.append(("id", "=", filters.id))
        if filters.name:
            domain.append(("name", "like", filters.name))
        return domain

    @restapi.method(
        routes=[(["/", "/search"], "GET")],
        input_param=PydanticModel(FleetServiceTypeSearchFilter),
        output_param=PydanticModelList(FleetServiceTypeInfo),
        auth="public",
    )
    def search(
        self, fleet_service_type_search_filter: FleetServiceTypeSearchFilter
    ) -> List[FleetServiceTypeInfo]:
        domain = self._get_search_domain(fleet_service_type_search_filter)
        res: List[FleetServiceTypeInfo] = []
        for e in self.env["fleet.service.type"].sudo().search(domain):
            res.append(FleetServiceTypeInfo.from_orm(e))
        return res
