# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.addons.pydantic import models, utils


class FleetVehicleOdometerInfo(models.BaseModel):
    id: int
    name: str
    value: float
    vehicle_id: int
    unit: str
    driver_id: int
    sequence: int = None
    write_date: datetime

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
