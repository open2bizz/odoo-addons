# -*- coding: utf-8 -*-
import base64
from werkzeug.wrappers import Request, Response

from orbeon_handlers import BuilderHandler, RunnerHandler, OdooServiceHandler
from .. import utils
from xml.etree import ElementTree as ET

_log = utils._log

BUILDER_HANDLER = 'builder_handler'
RUNNER_HANDLER = 'runner_handler'
ODOO_SERVICE_HANDLER = 'odoo_service_handler'


class OrbeonRequestHandler(object):
    """Orbeon (HTTP) request handler"""

    def __init__(self, request, configfile_path=None, wsgi_input=None):
        _log("debug", "request => %s" % request)
        _log("debug", "configfile_path => %s" % configfile_path)

        self.request = request
        self.path = request.path.split("/")
        self.args = request.args

        # Correct for chunked encoding in Orbeon > 2016
        if request.headers.get('Transfer-Encoding', '') == 'chunked' and request.headers.get('Content-Length', ' ') != ' ':
            body = ''
            if wsgi_input is not None:
                size = int(wsgi_input.readline(),16)
                while size > 0:
                    body += wsgi_input.read(size+2)[:-2]
                    size = int(wsgi_input.readline(),16)
                self.data = body
        else:
            self.data = request.data

        _log("debug", "path => %s" % self.path)

        """Attrs extracted from the request its path"""
        self.namespace = None
        self.app = None
        self.form = None
        self.data_type = None
        self.set_path_attrs()

        self.handler_type = None
        self.set_handler_type()

        self.handler = None
        self.set_handler()

        if configfile_path is not None:
            self.handler.set_config_by_file_path(configfile_path)

        if self.handler.config is not None and len(self.handler.config.sections()) > 0:
            self.handler.set_xmlrpc_by_config()
        else:
            url = "http://%s:%s" % (
                request.headers.get("Openerp-Server"),
                request.headers.get("Openerp-Port"),
            )
            db = request.headers.get("Openerp-Database")

            # get authorization parameters
            b64str = request.headers.get("Authorization").replace("Basic ", "")
            auth_str = base64.b64decode(b64str)
            auth = auth_str.split(":")
            usr, passwd = (auth[0], auth[1])

            self.handler.set_xmlrpc(db, usr, passwd, url)

    def set_path_attrs(self):
        """Set Request path-components to object attributes"""

        """Follows the spec of:
        https://doc.orbeon.com/form-runner/api/persistence
        """
        self.namespace = self.path[1]

        if len(self.path) > 2:
            self.app = self.path[2]
            self.form = self.path[3]
            self.data_type = self.path[4]

    def set_handler_type(self):
        """Get Orbeon handler type (class)"""
        if self.namespace == 'crud' and self.app == 'orbeon' and self.form == 'builder':
            self.handler_type = BUILDER_HANDLER
        elif self.namespace == 'crud' and self.form == 'runner':
            self.handler_type = RUNNER_HANDLER
        elif self.namespace == 'erp':
            self.handler_type = ODOO_SERVICE_HANDLER
        elif self.namespace == 'search' and self.app == 'orbeon' and self.form == 'builder':
            self.handler_type = BUILDER_HANDLER

        _log('debug', "handler_type => %s" % self.handler_type)

    def set_handler(self):
        """Set the Orbeon handler, determined by (path-)attrs (i.e. URL path-components)"""

        if self.handler_type == BUILDER_HANDLER:
            self.handler = BuilderHandler(self.app, self.form, self.data_type, self.path, self.args, self.data)
        elif self.handler_type == RUNNER_HANDLER:
            self.handler = RunnerHandler(self.app, self.form, self.data_type, self.path, self.args, self.data)
        elif self.handler_type == ODOO_SERVICE_HANDLER:
            self.handler = OdooServiceHandler(self.app, self.form, self.data_type, self.path, self.args, self.data)
        else:
            raise Exception("No OrbeonResource handler found for namespace %s and app %s."
                            % (self.namespace, self.app))

    def process(self):
        """Call the handler its HTTP-method equivalent function"""
        if self.request.method == "PUT":
            # create or update
            self.handler.save()
            return Response("")

        if self.request.method == "GET":
            res = self.handler.read()

            if self.handler.data_type == 'data' and self.handler.form_data_id == 'data.xml':
                return Response(res, mimetype="application/xml")
            elif self.handler_type == ODOO_SERVICE_HANDLER:
                return Response(res, mimetype="application/xml")
            else:
                return Response(res)

        if self.request.method == "POST":
            return self.handler.search()

        # if self.method == "DELETE":
        #     return self.handler.delete()


class OrbeonPersistenceApp(object):
    def __init__(self, configfile_path=None):
        self.configfile_path = configfile_path

    def dispatch_request(self, request, wsgi_input=None):
        orbeon_request = OrbeonRequestHandler(request, self.configfile_path, wsgi_input)
        return orbeon_request.process()

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request, wsgi_input=environ.get('wsgi.input'))
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def create_app(configfile_path=None):
    app = OrbeonPersistenceApp(configfile_path)
    return app
