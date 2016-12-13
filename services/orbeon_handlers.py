import ConfigParser
import os
import dicttoxml

from xmlrpc_service import XMLRPCService
from xmlgen import XmlGenerator

class OrbeonHandlerBase(object):
    def __init__(self, app, form, data_type, path=(), args={}, data=None):
        self.app = app
        self.form = form
        self.data_type = data_type
        self.path = path
        self.args = args
        self.data = data

        self.config = None
        self.xmlrpc = None

    def set_config_by_filename(self, config_filename):
        config = ConfigParser.ConfigParser()
        file_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(file_path, config_filename)

        config.read(path)
        
        if len(config.sections()) > 0:
            self.config = config

    def set_xmlrpc(self, db, usr, passwd, url):
        self.xmlrpc = XMLRPCService(db, usr, passwd, url)
    
    def set_xmlrpc_by_config(self):
        url = "%s:%s" % (
            self.config.get("odoo config", "server_url"),
            self.config.get("odoo config", "port"),
        )
        db = self.config.get("odoo config", "database_name")
        usr = self.config.get("odoo config", "username")
        pwd = self.config.get("odoo config", "password")

        self.xmlrpc = XMLRPCService(db, usr, pwd, url)

    def assert_config_file(self):
        config = self.get_config()
        
        if len(config.sections()) > 0:
            return True
        else:
            return False

class BuilderHandler(OrbeonHandlerBase):
    """Orbeon Builder (data) Handler"""
    
    def __init__(self, app, form, data_type, path=(), args={}, data=None):
        super(BuilderHandler, self).__init__(app, form, data_type, path, args, data)
        
        self.form_doc_id = path[5] if len(path) > 5 else None
        self.form_data_id = path[6] if len(path) > 6 else None

    def read(self):
        if self.data_type == 'data':
            if self.form_data_id == 'data.xml':
                record = self.xmlrpc.builder_search_read_data(
                    [[("id","=",self.form_doc_id)]],
                    ["xml"],
                )
                xml = record.get("xml")

                return xml
            else:
                return self.get_binary_data()

    def save(self):
        # Assumption of a database Pk/sequenced integer.
        # Orbeon sends a alnum string/hash, which is here handeld by _create().
        if self.form_doc_id.isdigit():
            self.write()
        else:
            self.create()
        
    """
    TODO
    Really test thoroughly (create from Orbeon app, and save multiple times.
    - What about the from_id
    - Check handle_binary_data() e.g. images.
    """
    def create(self):
        raise NotImplementedError("'create' not implemented on BuilderHandler")
        # data = {
        #     "name": 'TODO',
        #     "xml": self.data,
        #     "version": 1,
        #     "version_comment": "1",
        #     "server_id": 5,
        # }
        # self.xmlrpc.create(
        #     "orbeon.builder",
        #     [data]
        # )

        # self.handle_binary_data()

    def write(self):
        record = []

        record = self.xmlrpc.search(
            "orbeon.builder",
            [[("id","=",self.form_doc_id)]],
                    )
        if len(record) == 0:
            return

        if self.data_type == 'data':
            if self.form_data_id == 'data.xml':
                data = {"xml": str(self.data)}

                self.xmlrpc.write(
                    "orbeon.builder",
                    int(self.form_doc_id),
                    data
                )

                # TODO ? self.delete_all_binary_data()
            else:
                self.handle_binary_data()

    def search(self):
        try:
            form = self.xmlrpc.search_read(
                    "orbeon.builder", 
                    [[("id",">",0)]],
                    ["name","create_date","write_date"]
                    )
            if len(form) > 0:
                xml = XmlGenerator(form).gen_xml()
                return xml
        except Exception, e: print "Exception: %s" % e
        
        return res

    # TODO Can this be moved/refactored into parent-class?
    def get_binary_data(self):
        if self.data_type == 'data' and self.form_data_id != 'data.xml':
            domain = [
                ('res_id', '=', self.form_doc_id),
                ('res_model', '=', "orbeon.builder"),
                ('datas_fname', '=', self.form_data_id)
            ]

            res = self.xmlrpc.search_read(
                'ir.attachment',
                [domain],
                ['datas'],
            )

            if len(res) > 0:
                return res[0]['datas'].decode('base64')

    # TODO Can this be moved/refactored into parent-class?
    def handle_binary_data(self):
        if self.data_type == 'data' and self.form_data_id != 'data.xml':
            ira_data = {
                "res_id": self.form_doc_id,
                "res_model": "orbeon.builder",
                'name': self.form_data_id,
                'stored_fname': self.form_data_id,
                'datas_fname': self.form_data_id,
                "datas": self.data.encode('base64')
            }
            self.xmlrpc.create(
                'ir.attachment',
                [ira_data],
            )

    def delete_all_binary_data(self):
        pass

class RunnerHandler(OrbeonHandlerBase):
    """Orbeon Runner (data) Handler"""
    
    def __init__(self, app, form, data_type, path=(), args={}, data=None):
        super(Builder, self).__init__(app, form, data_type, path, args, data)

        self.form_doc_id = path[5] if len(path) > 5 else None

    def read(self):
        if self.data_type == 'form':
            # TODO form_id document not in path?
            form_doc_id = self.args.get('document')
            record = self.xmlrpc.runner_search_read_builder(
                [[("id","=",form_doc_id)]],
                ["xml"],
            )
        elif self.data_type == 'data':
            record = self.xmlrpc.runner_search_read_data(
                [[("id","=",self.form_doc_id)]],
                ["xml"],
            )

        xml = record.get("xml")
        return xml

    # TODO: impement create(), write() - like the BuilderHandler
    def save(self):
        record = self.xmlrpc.search(
            "orbeon.runner",
            [[("id","=",self.form_doc_id)]],
        )
        
        if len(record) == 1:
            data = {"xml": str(self.data)}
            
            self.xmlrpc.write(
                "orbeon.runner",
                int(self.form_doc_id),
                data,
            )
        elif len(record) == 0:
            data = {
                "name": str(self.form_doc_id),
                "xml": str(self.data),
            }
            self.xmlrpc.create(
                    "orbeon.runner",
                    [data]
            )

class OdooServiceHandler(OrbeonHandlerBase):
    def __init__(self, app, form, data_type, path=(), args={}, data=None):
        super(OdooServiceHandler, self).__init__(app, form, data_type, path, args, data)

        self.form_doc_id = path[5]

    """
    Orbeon Service URL support
    ==========================
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
    def read(self):
        model = self.args.get('model')

        if model is None:
            _log('error', 'model is missing in args (dict)')

        label = self.args.get('label')

        if label is None:
            _log('error', 'label is missing in args (dict)')                    

        domain = []
        domain_fields = self.args.getlist('domain_fields')

        for domain_field in domain_fields: 
            value = self.args.get(domain_field)

            if value is not None:
                filter = (domain_field,'=',value)
                domain.append(filter)

        _log('debug', "domain: %s" % domain)

        try:
            records = self.xmlrpc.search_read(model, [domain], [label])
            xml = dicttoxml.dicttoxml(records)
            dom = parseString(xml)

            _log('debug', dom.toprettyxml())
            return xml
        except Exception, e:
            _log('error', "Exception: %s" % e)
