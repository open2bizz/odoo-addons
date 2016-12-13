# -*- coding: utf-8 -*-
import base64
import dicttoxml
from werkzeug.wrappers import Request, Response
from xml.dom.minidom import parseString

from orbeon_handlers import BuilderHandler, RunnerHandler, OdooServiceHandler
from utils import _log

BUILDER_HANDLER = 'builder_handler'
RUNNER_HANDLER = 'runner_handler'
ODOO_SERVICE_HANDLER = 'odoo_service_handler'

class OrbeonRequestHandler(object):
    """Orbeon (HTTP) request handler"""
    
    def __init__(self, request, config_filename=None):
        _log("debug", "request => %s" % request)
        _log("debug", "config_filename => %s" % config_filename)

        self.request = request
        self.path = request.path.split("/")
        self.args = request.args
        self.data = request.data

        """Attrs extracted from the request its path"""
        self.namespace = None
        self.app = None
        self.form = None
        self.data_type = None
        self.set_path_attrs()

        self.handler = self.set_handler()
        self.handler.set_config_by_filename(config_filename)

        if len(self.handler.config.sections()) > 0:
            self.handler.set_xmlrpc_by_config()
        else:
            url = "http://%s:%s" % (
                request_headers.get("Openerp-Server"),
                request_headers.get("Openerp-Port"),
            )
            db = request_headers.get("Openerp-Database")

            # get authorization parameters
            b64str = request_headers.get("Authorization").replace("Basic ","")
            auth_str = base64.b64decode(b64str)
            auth = auth_str.split(":")
            usr, pwd = (auth[0], auth[1])
            
            self.handler.set_xmlrpc(db, usr, passwd, url)

    def set_path_attrs(self):
        """Follows the specs of:
        https://doc.orbeon.com/form-runner/api/persistence
        """
        self.namespace = self.path[1]
        self.app = self.path[2]
        self.form = self.path[3]
        self.data_type = self.path[4]

    def set_handler(self):
        """Set the Orbeon handler, determined by (URL)path-components"""
        handler_type = self.get_handler_type()

        if handler_type == BUILDER_HANDLER:
            return BuilderHandler(self.app, self.form, self.data_type, self.path, self.args, self.data)
        elif handler_type == RUNNER_HANDLER:
            return RunnerHandler(self.app, self.form, self.data_type, self.path, self.args, self.data)
        elif handler_type == ODOO_SERVICE_HANDLER:
            return OdooServiceHandler(self.app, self.form, self.data_type, self.path, self.args, self.data)
        else:
            raise Exception("No OrbeonResource handler found for namespace %s and app %s."
                            % (self.namespace, self.app))

    def get_handler_type(self):
        if self.namespace == 'crud' and self.app == 'orbeon':
            return BUILDER_HANDLER
        
        elif self.namespace == 'search' and self.app == 'orbeon' and self.form == 'builder':
            return BUILDER_HANDLER
        
        elif self.namespace == 'crud' and self.app != 'orbeon':
            return RUNNER_HANDLER
        
        elif self.namespace == 'erp':
            return ODOO_SERVICE_HANDLER

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
            else:
                return Response(res)

        if self.request.method == "POST":
            return self.handler.search()

        # if self.method == "DELETE":
        #     return self.handler.delete()

class OrbeonPersistenceApp(object):
    def __init__(self, config_filename=None):
        self.config_filename = config_filename
	
    def dispatch_request(self, request):
        orbeon_request = OrbeonRequestHandler(request, self.config_filename)
        return orbeon_request.process()

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

def create_app(config_filename=None):
    app = OrbeonPersistenceApp(config_filename)
    return app
