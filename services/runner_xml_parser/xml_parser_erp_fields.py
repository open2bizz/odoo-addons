import copy
import logging
import re

_logger = logging.getLogger(__name__)

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

        _logger.debug('Read ERP-fields: %s\n For model: %s' % (self.erp_fields.keys(), self.res_model))

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

                try:
                    target_object = target_object[field]
                except KeyError:
                    _logger.error('ERP-field %s not in model %s' % (field, self.res_model))

            # The last/solely item in model_fields should be the value
            try:
                field = model_fields[0]
                field_val = target_object[field]
            except KeyError:
                _logger.error('ERP-field %s not in model %s' % (field, self.res_model))

            erp_field_obj.set_element_text(field_val)

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
