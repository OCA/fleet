# Copyright 2026 Fleet e-Frotas Contributors
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from . import efrotas_client

try:
    import odoo
    from . import efrotas_config
    from . import efrotas_log
    from . import fleet_vehicle
except ImportError:
    pass

