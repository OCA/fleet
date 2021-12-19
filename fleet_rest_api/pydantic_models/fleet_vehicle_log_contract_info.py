# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pydantic

from datetime import date, datetime
from typing import List

from odoo.addons.pydantic import models, utils
from .fleet_service_type_info import FleetServiceTypeInfo


class FleetVehicleLogContractInfo(models.BaseModel):
    id: int
    name: str
    active: bool
    vehicle_id: int
    cost_subtype_id: int
    amount: float
    date: date
    company_id: int
    currency_id: int
    user_id: int
    start_date: date
    expiration_date: date
    days_left: int
    insurer_id: int
    purchaser_id: int
    ins_ref: str
    state: str
    notes: str
    cost_generated: float
    cost_frequency: str
    services_ids: List[FleetServiceTypeInfo] = pydantic.Field(alias="service_ids")
    write_date: datetime

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
