# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest.controllers import main


class BaseFleetPublicApiController(main.RestController):
    _root_path = "/fleet_rest_api/"
    _collection_name = "fleet.rest.services"
    _default_auth = "public"


# class BaseRestDemoPrivateApiController(main.RestController):
#     _root_path = "/base_rest_demo_api/private/"
#     _collection_name = "base.rest.demo.private.services"
#     _default_auth = "user"
#
#
# class BaseRestDemoNewApiController(main.RestController):
#     _root_path = "/base_rest_demo_api/new_api/"
#     _collection_name = "base.rest.demo.new_api.services"
#     _default_auth = "public"


# class BaseRestDemoJwtApiController(main.RestController):
#     # JWT Demo Controller, to be used with auth_jwt_demo
#     # https://github.com/OCA/server-auth/tree/14.0/auth_jwt_demo
#     _root_path = "/base_rest_demo_api/jwt/"
#     _collection_name = "base.rest.demo.jwt.services"
#     _default_auth = "jwt_demo_keycloak"
#     _component_context_provider = "auth_jwt_component_context_provider"
#     _default_cors = "*"
