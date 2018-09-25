import ConfigParser
import dicttoxml

from xml.dom.minidom import parseString

from xmlrpc_service import XMLRPCService
from xmlgen import XmlGenerator
from .. import utils

_log = utils._log


class OrbeonHandlerBase(object):
    def __init__(self, app, form, data_type, path=(), args={}, data=None):
        self.model = None

        self.app = app
        self.form = form
        self.data_type = data_type
        self.path = path
        self.args = args
        self.data = data

        self.config = None
        self.xmlrpc = None

    def set_config_by_file_path(self, configfile_path):
        """Set config object by config_filename"""
        config = ConfigParser.ConfigParser()
        config.read(configfile_path)

        if len(config.sections()) > 0:
            self.config = config

    def set_xmlrpc(self, db, usr, passwd, url):
        """Set XML-RPC service connection object"""
        self.xmlrpc = XMLRPCService(db, usr, passwd, url)

    def set_xmlrpc_by_config(self):
        """Set XML-RPC by config (e.g. config-file)"""
        url = "%s:%s" % (
            self.config.get("odoo config", "server_url"),
            self.config.get("odoo config", "port"),
        )
        db = self.config.get("odoo config", "database_name")
        usr = self.config.get("odoo config", "username")
        pwd = self.config.get("odoo config", "password")

        self.xmlrpc = XMLRPCService(db, usr, pwd, url)

    def get_binary_data(self):
        "Get binary data"

        """Currently get data from 'ir_attachment' (model)"""
        domain = [
            ('res_id', '=', self.form_doc_id),
            ('res_model', '=', self.model),
            ('datas_fname', '=', self.form_data_id)
        ]

        res = self.xmlrpc.search_read(
            'ir.attachment',
            [domain],
            ['datas'],
        )

        if len(res) > 0:
            return res[0]['datas'].decode('base64')

    def handle_binary_data(self):
        """Handle binray data"""

        """Currently data is stored in 'ir_attachment' (model)"""
        ira_data = {
            "res_id": self.form_doc_id,
            "res_model": self.model,
            'name': self.form_data_id,
            'store_fname': self.form_data_id,
            'datas_fname': self.form_data_id,
            "datas": self.data.encode('base64')
        }
        self.xmlrpc.create(
            'ir.attachment',
            [ira_data],
        )


class BuilderHandler(OrbeonHandlerBase):
    """Orbeon-Builder (data) Handler"""

    def __init__(self, app, form, data_type, path=(), args={}, data=None):
        super(BuilderHandler, self).__init__(app, form, data_type, path, args, data)

        self.model = 'orbeon.builder'
        self.form_doc_id = path[5] if len(path) > 5 else None
        self.form_data_id = path[6] if len(path) > 6 else None

    def read(self):
        """Get Orbeon-Builder data by read (i.e. HTTP GET)"""
        if self.data_type == 'data' and self.form_data_id == 'data.xml':
            record = self.xmlrpc.builder_search_read_data(
                [[("id", "=", self.form_doc_id)]],
                ["xml"],
            )
            return record.get("xml")
        else:
            return self.get_binary_data()

    def save(self):
        """Save Orbeon-Builder data by save (i.e. HTTP PUT)"""

        """Assumption of a database Pk/sequenced integer.
        Orbeon sends a alnum string/hash, which is here handeld by create().
        """
        if self.form_doc_id.isdigit():
            self.write()
        else:
            self.create()

    def write(self):
        """Write Orbeon-Builder data by save on edit (i.e. HTTP PUT)"""
        record = self.xmlrpc.search(
            "orbeon.builder",
            [[("id", "=", self.form_doc_id)]],
        )
        if len(record) == 0:
            return

        if self.data_type == 'data' and self.form_data_id == 'data.xml':
            data = {"xml": str(self.data)}

            self.xmlrpc.write(
                "orbeon.builder",
                int(self.form_doc_id),
                data
            )
        elif self.data_type == 'data':
            self.handle_binary_data()

    """
    TODO: create() called by the Orbeon request.
    Really test thoroughly (create from Orbeon app, and save multiple times.
    - What about the from_id
    - Check handle_binary_data() e.g. images.
    """
    def create(self):
        """Create Orbeon-Builder data by save on create/new (i.e. HTTP PUT)"""
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

    def search(self):
        """Search Orbeon-Builder data by search (i.e. HTTP POST on /search)"""
        try:
            form = self.xmlrpc.search_read(
                    "orbeon.builder",
                    [[("id", ">", 0)]],
                    ["name", "create_date", "write_date"]
            )
            if len(form) > 0:
                xml = XmlGenerator(form).gen_xml()
                return xml
        except Exception, e:
            print "Exception: %s" % e


class RunnerHandler(OrbeonHandlerBase):
    """Orbeon-Runner (data) Handler"""

    def __init__(self, app, form, data_type, path=(), args={}, data=None):
        super(RunnerHandler, self).__init__(app, form, data_type, path, args, data)

        self.model = 'orbeon.runner'
        self.form_doc_id = path[2].split('!')[2]
        self.form_data_id = path[6] if len(path) > 6 else None

    def read(self):
        """Get Orbeon-Runner data by read (i.e. HTTP GET)"""
        if self.data_type == 'form':
            record = self.xmlrpc.runner_search_read_builder(
                [[("id", "=", self.form_doc_id)]],
                ["xml"],
            )
            return record.get("xml")
        elif self.data_type == 'data' and self.form_data_id == 'data.xml':
            # Runner form data
            record = self.xmlrpc.runner_search_read_data(
                [[("id", "=", self.form_doc_id)]],
                ["xml"],
            )
            return record.get("xml")
        else:
            return self.get_binary_data()

    def save(self):
        """Save Orbeon-Runner data by save (i.e. HTTP PUT)"""

        """Assumption of a database Pk/sequenced integer.
        Orbeon sends a alnum string/hash, which is here handeld by create().
        """
        if self.form_doc_id.isdigit():
            self.write()
        else:
            self.create()

    def write(self):
        """Write Orbeon-Runner data by save on edit (i.e. HTTP PUT)"""

        if self.data_type == 'data' and self.form_data_id == 'data.xml':
            data = {"xml": str(self.data)}

            self.xmlrpc.write(
                "orbeon.runner",
                int(self.form_doc_id),
                data,
            )
        elif self.data_type == 'data':
            self.handle_binary_data()

    """
    TODO: create() called by the Orbeon request.
    Really test thoroughly (create from Orbeon app, and save multiple times.
    - What about the from_id
    - Check handle_binary_data() e.g. images.
    """
    def create(self):
        """Create Orbeon-Runner data by save on create/new (i.e. HTTP PUT)"""
        raise NotImplementedError("'create' not implemented on RunnerHandler")
        #     data = {
        #         "name": str(self.form_doc_id),
        #         "xml": str(self.data),
        #     }


class OdooServiceHandler(OrbeonHandlerBase):
    def __init__(self, app, form, data_type, path=(), args={}, data=None):
        super(OdooServiceHandler, self).__init__(app, form, data_type, path, args, data)

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
                filter = (domain_field, '=', value)
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
