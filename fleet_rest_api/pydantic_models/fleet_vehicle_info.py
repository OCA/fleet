# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, datetime
from typing import List

import pydantic

from odoo.addons.pydantic import models, utils

from .fleet_vehicle_assignation_log_info import FleetVehicleAssignationLogInfo
from .fleet_vehicle_log_contract_info import FleetVehicleLogContractInfo
from .fleet_vehicle_log_services_info import FleetVehicleLogServicesInfo
from .fleet_vehicle_state_info import FleetVehicleStateInfo
from .fleet_vehicle_tag_info import FleetVehicleTagInfo


class FleetVehicleInfo(models.BaseModel):
    id: int
    name: str
    description: str
    active: bool
    company_id: int
    currency_id: int
    license_plate: str
    vin_sn: str
    driver_id: int
    future_driver_id: int
    model_id: int
    manager_id: int
    brand_id: int
    log_drivers: List[FleetVehicleAssignationLogInfo] = pydantic.Field(
        [], alias="log_drivers"
    )
    log_services: List[FleetVehicleLogServicesInfo] = pydantic.Field(
        [], alias="log_services"
    )
    log_contracts: List[FleetVehicleLogContractInfo] = pydantic.Field(
        [], alias="log_contracts"
    )
    contract_count: int
    service_count: int
    odometer_count: int
    history_count: int
    next_assignation_date: date
    acquisition_date: date
    first_contract_date: date
    color: str
    state: FleetVehicleStateInfo = pydantic.Field(None, alias="state_id")
    location: str
    seats: int
    model_year: str
    tag_ids: List[FleetVehicleTagInfo] = pydantic.Field([], alias="tag_ids")
    odometer: float
    odometer_unit: str
    transmission: str
    fuel_type: str
    horsepower: int
    horsepower_tax: float
    power: int
    co2: float
    contract_renewal_due_soon: bool
    contract_renewal_overdue: bool
    contract_renewal_name: str
    contract_renewal_total: str
    car_value: float
    net_car_value: float
    residual_value: float
    plan_to_change_car: bool
    vehicle_type: str
    write_date: datetime

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
