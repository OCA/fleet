# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.pydantic import models


class FleetVehicleLogServicesSearchFilter(models.BaseModel):

    id: int = None
    service_type_id: int = None
    vehicle_id: int = None
    purchaser_id: int = None
    vendor_id: int = None
    state: str = None
