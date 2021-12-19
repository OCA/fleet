# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.fleet_vehicle_log_services_info import FleetVehicleLogServicesInfo
from ..pydantic_models.fleet_vehicle_log_services_search_filter import (
    FleetVehicleLogServicesSearchFilter,
)


class FleetVehicleLogServicesService(Component):
    _inherit = "base.fleet.rest.service"
    _name = "fleet.vehicle.log.services.rest.service"
    _usage = "vehicle_log_services"
    _expose_model = "fleet.vehicle.log.services"
    _collection = "fleet.rest.services"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        output_param=PydanticModel(FleetVehicleLogServicesInfo),
        auth="public",
    )
    def get(self, _id: int) -> FleetVehicleLogServicesInfo:
        fleet_vehicle_log_services = self._get(_id)
        return FleetVehicleLogServicesInfo.from_orm(fleet_vehicle_log_services)

    def _get_search_domain(self, filters):
        domain = []
        if filters.id:
            domain.append(("id", "=", filters.id))
        if filters.service_type_id:
            domain.append(("service_type_id", "=", filters.service_type_id))
        if filters.vehicle_id:
            domain.append(("vehicle_id", "=", filters.vehicle_id))
        if filters.purchaser_id:
            domain.append(("purchaser_id", "=", filters.purchaser_id))
        if filters.vendor_id:
            domain.append(("vendor_id", "=", filters.vendor_id))
        if filters.state:
            domain.append(("state", "=", filters.state))
        return domain

    @restapi.method(
        routes=[(["/", "/search"], "GET")],
        input_param=PydanticModel(FleetVehicleLogServicesSearchFilter),
        output_param=PydanticModelList(FleetVehicleLogServicesInfo),
        auth="public",
    )
    def search(
        self, fleet_vehicle_log_services_search_filter: FleetVehicleLogServicesSearchFilter
    ) -> List[FleetVehicleLogServicesInfo]:
        domain = self._get_search_domain(fleet_vehicle_log_services_search_filter)
        res: List[FleetVehicleLogServicesInfo] = []
        for e in self.env["fleet.vehicle.log.services"].sudo().search(domain):
            res.append(FleetVehicleLogServicesInfo.from_orm(e))
        return res
