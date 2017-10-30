import copy
import logging
import re

_logger = logging.getLogger(__name__)

ERP_FIELD_PREFIX = 'ERP'
UNKNOWN_ERP_FIELD = 'UNKNOWN ERP-FIELD'


class XMLParserERPFieldsException(Exception):
    def __init__(self, msg):
        self.message = "[ERROR: ERP-Field] %s" % msg


class XmlParserBase(object):

    def __init__(self, runner, xml_root):
        self.runner = runner
        self.xml_root = xml_root

        self.erp_fields = None
        self.res_object = None
        self.res_model = self.runner.builder_id.res_model_id.model

        self.errors = []


class XmlParserERPFields(XmlParserBase):

    def __init__(self, runner, xml_root):
        super(XmlParserERPFields, self).__init__(runner, xml_root)

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

        self.res_object = self.runner.env[self.runner.builder_id.res_model_id.model].browse(self.runner.res_id)

    def parse(self):
        # TODO Refactor this beast into smaller functions
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

            # All handled (seen) fields
            all_fields = []
            # All traversed (parent) fields
            traversed_fields = []
            relational_field_error = False

            while len(model_fields) > 1:
                field = model_fields.pop(0)
                all_fields.append(field)

                try:
                    target_object = target_object[field]
                    traversed_fields.append(field)
                except KeyError as relational_field_error:
                    msg = "NOT IN MODEL %s" % self.res_model
                    error = self._exception_erpfield(erp_field_obj.tagname, all_fields, msg)
                except Exception as relational_field_error:
                    msg = "ERROR with model %s" % self.res_model
                    error = self._exception_erpfield(erp_field_obj.tagname, all_fields, msg)

                if relational_field_error:
                    self.errors.append(error)
                    _logger.info('[orbeon] %s' % error.message)

            # Add last model_field
            all_fields.append(model_fields[0])

            if not relational_field_error:
                try:
                    # The last/solely item in model_fields should be the value
                    field = model_fields[0]
                    field_val = target_object[field]

                except KeyError:
                    msg = "NOT IN MODEL %s" % self.res_model
                    error = self._exception_erpfield(erp_field_obj.tagname, all_fields, msg)

                    if self.runner.builder_id.debug_mode:
                        field_val = error.message
                    else:
                        field_val = UNKNOWN_ERP_FIELD

                    _logger.info('[orbeon] %s' % error.message)
                    self.errors.append(error)

                except Exception as e:
                    error = self._exception_erpfield(erp_field_obj.tagname, all_fields, e.message)

                    if self.runner.builder_id.debug_mode:
                        field_val = error.message
                    else:
                        field_val = UNKNOWN_ERP_FIELD

                    _logger.info('[orbeon] %s' % error.message)
                    self.errors.append(error)
            else:
                # elif isinstance(relational_field_error, KeyError):
                # Brought here by the `while (loop)` above.
                # where relational_field_error was set True.
                if self.runner.builder_id.debug_mode:
                    field_val = error.message
                else:
                    field_val = UNKNOWN_ERP_FIELD

            erp_field_obj.set_element_text(field_val)

    def _exception_erpfield(self, tagname, fields_chain, msg):
        msg_exception = "%s (ERP.%s %s)" % (tagname, (".".join(fields_chain)), msg)
        return XMLParserERPFieldsException(msg_exception)


class ERPField(object):

    def __init__(self, tagname, element):
        self.tagname = tagname
        self.element = element

        re_pattern = r'^%s\.' % ERP_FIELD_PREFIX
        # erp_field_token is self.tagname without the ERP_FIELD_PREFIX
        erp_field_token = re.sub(re_pattern, '', self.tagname)
        self.model_fields = erp_field_token.split('.')

    def set_element_text(self, value):
        try:
            self.element.text = value
        except:
            pass
