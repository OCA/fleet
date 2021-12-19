# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.fleet_vehicle_odometer_info import FleetVehicleOdometerInfo
from ..pydantic_models.fleet_vehicle_odometer_search_filter import (
    FleetVehicleOdometerSearchFilter,
)


class FleetVehicleOdometerService(Component):
    _inherit = "base.fleet.rest.service"
    _name = "fleet.vehicle.odometer.rest.service"
    _usage = "vehicle_odometer"
    _expose_model = "fleet.vehicle.odometer"
    _collection = "fleet.rest.services"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        output_param=PydanticModel(FleetVehicleOdometerInfo),
        auth="public",
    )
    def get(self, _id: int) -> FleetVehicleOdometerInfo:
        fleet_vehicle_odometer = self._get(_id)
        return FleetVehicleOdometerInfo.from_orm(fleet_vehicle_odometer)

    def _get_search_domain(self, filters):
        domain = []
        if filters.id:
            domain.append(("id", "=", filters.id))
        if filters.name:
            domain.append(("name", "like", filters.name))
        if filters.vehicle_id:
            domain.append(("vehicle_id", "=", filters.vehicle_id))
        if filters.driver_id:
            domain.append(("driver_id", "=", filters.driver_id))
        return domain

    @restapi.method(
        routes=[(["/", "/search"], "GET")],
        input_param=PydanticModel(FleetVehicleOdometerSearchFilter),
        output_param=PydanticModelList(FleetVehicleOdometerInfo),
        auth="public",
    )
    def search(
        self, fleet_vehicle_odometer_search_filter: FleetVehicleOdometerSearchFilter
    ) -> List[FleetVehicleOdometerInfo]:
        domain = self._get_search_domain(fleet_vehicle_odometer_search_filter)
        res: List[FleetVehicleOdometerInfo] = []
        for e in self.env["fleet.vehicle.odometer"].sudo().search(domain):
            res.append(FleetVehicleOdometerInfo.from_orm(e))
        return res
