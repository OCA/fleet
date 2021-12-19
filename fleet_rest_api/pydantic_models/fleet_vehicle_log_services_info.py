# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, datetime
from typing import List

from odoo.addons.pydantic import models, utils


class FleetVehicleLogServicesInfo(models.BaseModel):
    id: int
    active: bool
    vehicle_id: int
    amount: float
    description: str
    odometer_id: int
    odometer: float
    odometer_unit: str
    date: date
    company_id: int
    currency_id: int
    purchaser_id: int
    inv_ref: str
    vendor_id: int
    notes: str
    service_type_id: int
    state: str
    write_date: datetime

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
