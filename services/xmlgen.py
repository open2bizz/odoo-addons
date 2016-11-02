# (document)
main_template = '<?xml version="1.0" encoding="utf-8"?><documents xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:f="http//www.orbeon.com/function" xmlns:frf="java:org.orbeon.oxf.fr.FormRunner" xmlns:odt="http://orbeon.org/oxf/xml/datatypes" xmlns:oxf="http://www.orbeon.com/oxf/processors" xmlns:p="http://www.orbeon.com/oxf/pipeline" xmlns:saxon="http://saxon.sf.net/" xmlns:sql="http://orbeon.org/oxf/xml/sql" xmlns:xf="http://www.w3.org/2002/xforms" xmlns:xi="http://www.w3.org/2001/XInclude" xmlns:xpl="java:org.orbeon.oxf.pipeline.api.FunctionLibrary" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xxf="http://orbeon.org/oxf/xml/xforms" search-total="9" total="9">%s</documents>'

# dates in format Y-M-DTh:m:s.msZ
# (created, modified, name, details)
document_template = '<document created="%s" draft="N" last-modified="%s" name="%s" operations="*">%s</document>'

# (application name, form name, form title)
detail_template = '<details><detail>%s</detail><detail>%s</detail><detail>%s</detail><detail/></details>'


class XmlGenerator(object):
	
    def __init__(self, records):
        self.records = records	

    def _get_xml(self):
        documents = ""
        for record in self.records:
            app_name = record.get("name")
            form_name = record.get("name")
            form_title = record.get("name")
            # time format dateTtimeZ
            cr_date = record.get("create_date").split(" ")
            create_date = "%sT%sZ" % (cr_date[0], cr_date[1])
            wr_date = record.get("write_date").split(" ")
            write_date = "%sT%sZ" % (wr_date[0], wr_date[1])
            # details template
            details = detail_template % (
                        app_name, 
                        form_name, 
                        form_title
                        )
            # document template
            document = document_template % (
                            create_date,
                            write_date,
                            app_name,
                            details,
                            )
            documents += document
        return documents

    def gen_xml(self):
        documents = self._get_xml()
        xml = main_template % documents
        return xml
