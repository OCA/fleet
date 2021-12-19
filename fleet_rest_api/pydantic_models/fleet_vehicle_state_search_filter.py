# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.pydantic import models


class FleetVehicleStateSearchFilter(models.BaseModel):

    id: int = None
    name: str = None
