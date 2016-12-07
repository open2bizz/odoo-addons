# -*- coding: utf-8 -*-
import base64
import ConfigParser
import dicttoxml
import logging
import os
from werkzeug.wrappers import Request, Response
from xml.dom.minidom import parseString

from xmlrpc_service import XMLRPCService
from xmlgen import XmlGenerator

FORMAT = "%(asctime)-15s %(log_lvl)-4s: %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(10)

def _log(type, msg):
    if type == "error":
        logger.error(msg, extra={"log_lvl": "Error"})
    elif type == "warning":
        logger.warning(msg, extra={"log_lvl": "Warning"})
    elif type == "debug":
        logger.debug(msg, extra={"log_lvl": "Debug"})
    elif type == "critical":
        logger.critical(msg, extra={"log_lvl": "Critical"})
    elif type == "exception":
        logger.exception(msg, extra={"log_lvl": "Exception"})
    elif type == "info":
        logger.info(msg, extra={"log_lvl": "Info"})

class PersistenceLayer(object):

    def __init__(self, config_filename=None):
        self.config_filename = config_filename
        self.use_config_file = self.assert_config_file()

    def set_config_filename(self, config_filename=None):
        if filename:
            self.config_filename = config_filename

    def get_config(self):
        config = ConfigParser.ConfigParser()
        file_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(file_path, self.config_filename)
        
        config.read(path)
        return config

    def assert_config_file(self):
        config = self.get_config()
        
        if len(config.sections()) > 0:
            return True
        else:
            return False
	
    def dispatch_request(self, request):
        res = Response("") 
        if request.method == "POST":
            _log("info", request)
            return self.post_method(request)
        if request.method == "GET":
            _log("info", request)
            return self.get_method(request)
        if request.method == "PUT":
            _log("info", request)
            return self.put_method(request) 
        return res

    def post_method(self, request):
        """summary"""
        
        res = Response("")
        if request.path == "/search/orbeon/builder":
            xmlrpc = self._get_xmlrpc(request.headers)
            try:
                form = xmlrpc.search_read(
                        "orbeon.builder", 
                        [[("id",">",0)]],
                        ["name","create_date","write_date"]
                        )
                if len(form) > 0:
                    xml = XmlGenerator(form).gen_xml()
                    return Response(xml, mimetype="application/xml") 
            except Exception, e: print "Exception: %s" % e 
        return res

    def get_method(self, request):
        res = Response("")
        try:
            path = request.path.split("/")
            _log('debug', path)

            if path[1] == 'erp':
                return self.get_erp_resource_method(request, path)
            else:
                return self.get_orbeon_method(request, path)
        except:
            return res

    """
    URLs
    ====

    - Builder edit:
    http://localhost:8080/orbeon4.10/fr/orbeon/builder/edit/<ID>

    - Builder view:
    http://localhost:8080/orbeon4.10/fr/orbeon/builder/view/<ID>
    
    - Runner new:
    http://localhost:8080/orbeon4.10/fr/orbeon/runner/new

    - Runner edit:
    http://localhost:8080/orbeon4.10/fr/orbeon/runner/edit/<ID>
    """
    def get_orbeon_method(self, request, path):
        # import pdb
        # pdb.set_trace()
        try:
            xmlrpc = self._get_xmlrpc(request.headers)
        except Exception, e:
            _log('error', "Exception: %s" % e)
            
        form_mode = path[3]

        if form_mode == 'builder':
            form_id = path[5]
            record = xmlrpc.builder_search_read_data(
                    [[("id","=",form_id)]],
                    ["xml"],
                    )
            xml = record.get("xml")
            return Response(xml, mimetype="application/xml")

        elif form_mode == 'runner':
            runner_action = path[4]

            if runner_action == 'form':
                form_id = request.args.get('document')
                record = xmlrpc.runner_search_read_builder(
                    [[("id","=",form_id)]],
                    ["xml"],
                    )
            elif runner_action == 'data':
                form_id = path[5]
                record = xmlrpc.runner_search_read_data(
                    [[("id","=",form_id)]],
                    ["xml"],
                    )

            xml = record.get("xml")
            return Response(xml, mimetype="application/xml")

    """
    URLs
    ====
    - Get a list of res.partner (name, id) where health_partner_type = physician and gender = female
    http://localhost:5000/erp?model=res.partner&domain_fields=health_partner_type&health_partner_type=physician&domain_fields=gender&gender=female&label=name

    queryparams:
    1. model=res.partner (required)
    
    2.1 domain_fields=health_partner_type
    2.2 health_partner_type=physician
    
    3.1 domain_fields=gender
    3.2 gender=female

    4. label=name
    """
    def get_erp_resource_method(self, request, path):
        _log('debug', request.args)

        model = request.args.get('model')

        if model is None:
            _log('error', '[get_erp_resource_method] model: is missing in URL query-param !')

        label = request.args.get('label')

        if label is None:
            _log('error', '[get_erp_resource_method] label: is missing in URL query-param !')                    

        domain = []
        domain_fields = request.args.getlist('domain_fields')

        for domain_field in domain_fields: 
            value = request.args.get(domain_field)

            if value is not None:
                filter = (domain_field,'=',value)
                domain.append(filter)

        _log('debug', "[get_erp_resource_method] domain: %s" % domain)

        try:
            xmlrpc = self._get_xmlrpc(request.headers)
            records = xmlrpc.search_read(model, [domain], [label])
            xml = dicttoxml.dicttoxml(records)
            dom = parseString(xml)

            _log('debug', dom.toprettyxml())

            return Response(xml, mimetype="application/xml")
        except Exception, e:
            _log('error', "Exception: %s" % e)

    def put_method(self, request):
        """create / write"""
        res = Response("")
        path = self._get_path_data(request)

        if path['form_type'] == "builder":
            self._put_builder(request, path)
        elif path['form_type'] == "runner":
            self._put_runner(request, path)

    def _put_builder(self, request, path_info):
        record = []
        form_id = path_info['form_id']

        # Assumption of a database Pk/sequenced integer.
        # Orbeon sends a alnum string/hash, which is here handeld by _put_builder_create().
        if form_id.isdigit():
            self.put_builder_write(request, path_info)
        else:
            self.put_builder_create(request, path_info)

    def _put_builder_write(self, request, path_info):
        xmlrpc = self._get_xmlrpc(request.headers)
        record = []
        form_id = path_info['form_id']
        form_payload_type = path_info['form_payload_type']
        form_payload_id = path_info['form_payload_id']
        
        record = xmlrpc.search(
            "orbeon.builder",
            [[("id","=",form_id)]],
                    )
        if len(record) == 0:
            return

        if form_payload_type != 'data':
            data = {
                "xml": str(request.data),
            }
            xmlrpc.write(
                "orbeon.builder",
                int(form_id),
                data
            )

        self._handle_binary_data(request, path_info)

    """
    TODO
    - Really test thoroughly (create from Orbeon app, and save multiple times.. what about the from_id??)
    - Check _handle_binary_data() e.g. images.
    """
    def _put_builder_create(self, request, path_info):
        xmlrpc = self._get_xmlrpc(request.headers)
        
        data = {
            "name": 'TODO',
            "xml": request.data,
            "version": 1,
            "version_comment": "1",
            "server_id": 5,
        }
        xmlrpc.create(
            "orbeon.builder",
            [data]
        )

        self._handle_binary_data(request, path_info)

    # TODO: impement _put_runner_create(), _put_runner_write()
    def _put_runner(self, request, path_info):
        record = xmlrpc.search(
            "orbeon.runner",
            [[("id","=",form_id)]],
        )
        
        if len(record) == 1:
            data = {
                "xml": str(request.data),
            }
            
            xmlrpc.write(
                "orbeon.runner",
                int(form_id),
                data,
            )
        elif len(record) == 0:
            data = {
                "name": str(form_id),
                "xml": str(request.data),
            }
            xmlrpc.create(
                    "orbeon.runner",
                    [data]
            )
    
    def _handle_binary_data(self, request, path_info):
        form_payload_type = path_info['form_payload_type']
        form_payload_id = path_info['form_payload_id']
        
        if form_payload_type == 'data' and form_payload_id != 'data.xml':
            ira_data = {
                "res_id": form_id,
                "res_model": "orbeon.builder",
                'name': form_payload_id,
                'stored_fname': form_payload_id,
                'datas_fname': form_payload_id,
                "datas": request.data.encode('base64')
            }
            xmlrpc.create(
                'ir.attachment',
                [ira_data],
            )

    def _get_path_data(self, request):
        path = request.path.split("/")

        return {
            'form_type': path[3],
            'form_payload_type': path[4],
            'form_id': path[5] if len(path) > 5 else None,
            'form_payload_id': path[6] if len(path) > 6 else None
        }

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def _get_xmlrpc(self, header):
        """ use config file if exists, otherwise get header data """
        if not self.use_config_file:
            url = "http://%s:%s" % (
                    header.get("Openerp-Server"),
                    header.get("Openerp-Port"),
                    )
            db = header.get("Openerp-Database")

            # get authorization parameters
            b64str = header.get("Authorization").replace("Basic ","")
            auth_str = base64.b64decode(b64str)
            auth = auth_str.split(":")
            usr, pwd = (auth[0], auth[1])	
        else:
            config = self.get_config()
            
            url = "%s:%s" % (
                    config.get("odoo config", "server_url"),
                    config.get("odoo config", "port"),
                    )
            db = config.get("odoo config", "database_name")
            usr = config.get("odoo config", "username")
            pwd = config.get("odoo config", "password")

        return XMLRPCService(db, usr, pwd, url)

def create_app(config_filename=None):
    app = PersistenceLayer(config_filename)
    return app
