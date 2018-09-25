import logging

from lxml import etree

from xml_parser_erp_fields import XmlParserERPFields

_logger = logging.getLogger(__name__)

class RunnerXmlParser(object):

    def __init__(self, xml, runner):
        self.xml = xml
        self.runner = runner

        # XXX to prevent modification of the runner object?
        # self.runner = copy.deepcopy(runner)

        self.xml_root = self.xml_root()
        self.parsers = self.parsers()
        self.errors = []

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

            # Append any errors
            self.xml_root = parser.xml_root
            self.errors += parser.errors

        self.xml = etree.tostring(self.xml_root, encoding='unicode')
