# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo.addons.pydantic import models


class FleetVehicleSearchFilter(models.BaseModel):

    id: int = None
    name: str = None
    stage_ids: List[int] = None
