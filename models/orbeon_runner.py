# -*- encoding: utf-8 -*-
##############################################################################
#
#    open2bizz
#    Copyright (C) 2016 open2bizz (open2bizz.nl).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, fields, models
from odoo.exceptions import ValidationError

import copy
import logging
import re

from lxml import etree

_logger = logging.getLogger(__name__)

from orbeon_builder import STATE_NEW as BUILDER_STATE_NEW
from orbeon_builder import STATE_CURRENT as BUILDER_STATE_CURRENT

STATE_NEW = 'new'
STATE_PROGRESS = 'progress'
STATE_COMPLETE = 'complete'
STATE_CANCELED = 'canceled'

class OrbeonRunner(models.Model):
    _name = "orbeon.runner"
    _rec_name = "builder_name"

    _orbeon_res_id_field = None
    
    builder_id = fields.Many2one(
        "orbeon.builder",
        string="Form builder",
        ondelete='restrict')

    builder_name = fields.Char(
        "Builder name",
        compute="_get_builder_name",
        readonly=True)

    builder_version = fields.Integer(
        "Builder version",
        compute="_get_builder_version",
        readonly=True)
    
    state = fields.Selection(
        [
            (STATE_NEW, "New"),
            (STATE_PROGRESS, "In Progress"),
            (STATE_COMPLETE, "Complete"),
            (STATE_CANCELED, "Canceled"),
        ],
        string="State",
        default=STATE_NEW)

    """Lets us know if this filed is merged with latest builder fields."""
    is_merged = fields.Boolean(
        'Is Merged',
        default=False)

    xml = fields.Text(
        'XML',
        default=False)

    url = fields.Text(
        'URL',
        compute="_get_url",
        readonly=True)

    @api.model
    def _get_orbeon_res_id_field(self):
        return self._orbeon_res_id_field

    @api.one
    def _get_builder_name(self, id=None):
        self.builder_name = "%s (%s)" % (self.builder_id.name, self.builder_id.version)

    @api.one
    def _get_builder_version(self, id=None):
        self.builder_version = self.builder_id.version

    @api.multi
    @api.onchange('builder_id')
    def _get_url(self):
        for rec in self:
            
            if isinstance(rec.id, models.NewId) and not rec.builder_id.id:
                return rec.url

            server_url = rec.builder_id.server_id.url
            base_path = 'fr/orbeon/runner'
            base_url = "%s/%s" % (server_url, base_path)

            if isinstance(rec.id, models.NewId):
                url = "%s/new" % base_url
            else:
                #runner_id = rec.id
                get_mode = {STATE_NEW: 'edit', STATE_PROGRESS: 'edit'}
                path_mode = get_mode.get(rec.state ,'view')
                url = "%s/%s/%i" % (base_url, path_mode, rec.id)

            rec.url = url

    @api.multi
    def action_open_orbeon_runner(self):
        self.ensure_one()
        return {
            'name': 'Orbeon',
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': self.url
        }

    # def orbeon_runner_form(self, cr, uid, ids, context=None):
    #     _logger.error('open orbeon_runner_form')
    #     # TODO From here open wizard (action window: to coppy or create/new

    @api.multi
    def write(self, vals):
        if self.is_merged == False:
            vals['is_merged'] = True

        if vals.get('builder_id', False) and vals['builder_id'] != self.builder_id:
            raise ValidationError("Changing the builder is not allowed.")
        
        res = super(OrbeonRunner, self).write(vals)
        return res
    
    @api.multi
    def duplicate_runner_form(self):
        alter = {}
        alter["state"] = STATE_NEW
        alter["is_merged"] = False

        # XXX maybe useless if merge_xml_current_builder() returns None?
        alter["xml"] = self.merge_xml_current_builder()

        res = super(OrbeonRunner, self).copy(alter)        
        
    # TODO: check whether and which @api decorator is needed here
    def merge_xml_current_builder(self):
        # No merge required if the runner's builder already is currrent
        if (self.builder_id.state == BUILDER_STATE_CURRENT):
            return self.xml

        orbeon_server = self.env['orbeon.builder']
        current_builder = orbeon_builder.search(
            [('name', '=', self.builder_id.name),
             ('state', '=', BUILDER_STATE_CURRENT)],
            limit=1,
            order='version DESC')

        return self.merge_xml_builder(current_builder.id)

    # TODO: check whether and which @api decorator is needed here
    def merge_xml_builder(self, builder_id):
        builder_name = self.builder_id.name
        builder = self.browse(builder_id)

        # TODO implement
        return self.xml

    @api.model
    def orbeon_search_read_builder(self, domain=None, fields=None):
        runner = self.search(domain or [], limit=1)
        builder = runner.builder_id

        res = {'id': builder['id']}

        if 'xml' in fields:
            res['xml'] = builder.xml

        return res

    @api.model
    def orbeon_search_read_data(self, domain=None, fields=None):
        runner = self.search(domain or [], limit=1)

        res = {'id': runner['id']}

        if 'xml' in fields:
            if runner.xml is None or runner.xml is False:
                # TODO
                # preprend the <xml> tag from elsewhere? Via builder-API to get right version?
                # code: runner.builder_id.get_xml_form_node(with_xml_tag)
                runner_xml = '<?xml version="1.0" encoding="utf-8"?>%s' % \
                             runner.builder_id.get_xml_form_node()[0]
            else:
                runner_xml = runner.xml

            res['xml'] = self.parse_runner_xml(runner_xml, runner)

        return res

    def parse_runner_xml(self, xml, runner):
        parser = RunnerXmlParser(xml, runner)
        parser.parse()
        return parser.xml

class RunnerXmlParser(object):

    def __init__(self, xml, runner):
        self.xml = xml
        self.runner = runner

        # XXX to prevent modification of the runner object?
        # self.runner = copy.deepcopy(runner)

        self.xml_root = self.xml_root()
        self.parsers = self.parsers()

    def parsers(self):
        return ('XmlParserERPFields',)

    def xml_root(self):
        try:
            xml = self.xml.encode('utf-8')
            parser = etree.XMLParser(ns_clean=True, recover=False, encoding='utf-8')
            xml_root = etree.XML(xml, parser)
        except etree.XMLSyntaxError:
            parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
            xml_root = etree.XML(xml, parser)
            _logger.debug("Bad XML: %s, Id: %d" % ('orbeon.runner', self.runner.id))
        return xml_root

    def parse(self):
        """Call each parser and update the xml (self.xml)"""

        for parser_class in self.parsers:
            parser = globals()[parser_class](self.runner, self.xml_root)
            parser.parse()
            self.xml_root = parser.xml_root

        self.xml = etree.tostring(self.xml_root)

ERP_FIELD_PREFIX = 'ERP'

class XmlParserERPFields(object):

    def __init__(self, runner, xml_root):
        self.runner = runner
        self.xml_root = xml_root

        self.erp_fields = None
        self.res_model = self.runner.builder_id.res_model_id.model
        self.res_object = None

        self.init()

    def init(self):
        self.load_erp_fields()

        if not self.has_erp_fields():
            return

        self.load_res_object()

    def has_erp_fields(self):
        return self.erp_fields is not None

    def load_erp_fields(self):
        """Load ERP fields"""

        """
        (xpath) find all ERP-fields in XML and store these in a dictionary key'd
        by the tagname.
        """
        query = "//*[starts-with(local-name(), '%s.')]" % ERP_FIELD_PREFIX
        res = self.xml_root.xpath(query)

        if len(res) == 0:
            return

        # Re-initialize from None to dict
        self.erp_fields = {}

        for element in res:
            self.erp_fields[element.tag] = ERPField(element.tag, element)

        _logger.debug('Read fields: %s\n From model: %s' % (fields, self.res_model))

    def load_res_object(self):
        if not self.has_erp_fields():
            return

        res_id_field = self.runner._get_orbeon_res_id_field()
        self.res_object = self.runner.env[self.res_model].browse(self.runner[res_id_field].id)

    def parse(self):
        if not self.has_erp_fields():
            return

        for tagname, erp_field_obj in self.erp_fields.iteritems():
            target_object = self.res_object

            # copy model_fields because of alternations in the while-loop reducer below.
            model_fields = copy.copy(erp_field_obj.model_fields)

            """
            model_fields with a length greater then 1 presumes a relational read
            For example:
            - ['company_id', 'name']
            - ['company_id', 'currency_id', 'name']
            """

            while len(model_fields) > 1:
                field = model_fields.pop(0)
                target_object = target_object[field]

            # The last/solely item in model_fields should be the value
            erp_field_obj.set_element_text(target_object[model_fields[0]])
        return self.xml_root

class ERPField(object):

    def __init__(self, tagname, element):
        self.tagname = tagname
        self.element = element

        re_pattern = r'^%s\.' % ERP_FIELD_PREFIX
        # erp_field_token is self.tagname without the ERP_FIELD_PREFIX
        erp_field_token = re.sub(re_pattern, '', self.tagname)
        self.model_fields = erp_field_token.split('.')

    def set_element_text(self, value):
        self.element.text = value
