# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, datetime

from odoo.addons.pydantic import models, utils


class FleetVehicleAssignationLogInfo(models.BaseModel):
    id: int
    vehicle_id: int
    driver_id: int
    date_start: date
    date_end: date
    write_date: datetime

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
