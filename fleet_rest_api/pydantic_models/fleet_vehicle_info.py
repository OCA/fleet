# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

import pydantic

from odoo.addons.pydantic import models, utils

from .fleet_vehicle_state_info import FleetVehicleStateInfo


class FleetVehicleInfo(models.BaseModel):
    id: int
    name: str
    odometer: float
    odometer_unit: str
    vehicle_type: str
    state: FleetVehicleStateInfo = pydantic.Field(None, alias="state_id")
    write_date: datetime

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
