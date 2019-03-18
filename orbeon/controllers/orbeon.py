# -*- coding: utf-8 -*-
##############################################################################
#    Copyright (c) 2016 - Open2bizz
#    Author: Open2bizz
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License is available at:
#    <http://www.gnu.org/licenses/gpl.html>.
#
##############################################################################
import requests
from urlparse import urlparse
from werkzeug.wrappers import Response
from odoo import http
import base64
from odoo.tools import config
import logging
logger = logging.getLogger(__name__)

class Orbeon(http.Controller):
    orbeon_base_route = 'orbeon'
    
    @http.route('/%s/<path:path>' % orbeon_base_route, type='http', auth="user", csrf=False)
    def render_orbeon_page(self, path, redirect=None, **kw):
        orbeon_server = http.request.env["orbeon.server"].search_read([], ['url'])
        if len(orbeon_server) == 0:
            return 'Orbeon server not found'
        else :
            orbeon_server = orbeon_server[0]
        o = urlparse(orbeon_server['url'])
        
        odoo_session = http.request.session

        orbeon_headers = ['cookie']
        in_headers = { name : value for (name, value) in http.request.httprequest.headers.items()
                   if name.lower() in orbeon_headers}
        
        in_headers.update({'Openerp-Server' : 'localhost'})
        in_headers.update({'Openerp-Port' : str(config.get('xmlrpc_port'))})
        in_headers.update({'Openerp-Database' :  odoo_session.get('db') })
        in_headers.update({'Authorization' : 'Basic %s' % base64.b64encode("%s:%s" % (odoo_session.get('login'), odoo_session.get('password')) ) } )
        
        logger.debug('Calling Orbeon on url %s with header %s' % (o.netloc, in_headers))
        curl = urlparse(http.request.httprequest.url)._replace(netloc=o.netloc, scheme='http')
        
        resp = requests.request(
            method=http.request.httprequest.method,
            url=curl.geturl(),
            headers=in_headers,
            data=http.request.httprequest.form if len(http.request.httprequest.form)>0 else http.request.httprequest.get_data(),
            #cookies=http.request.httprequest.cookies,
            allow_redirects=False) 
        
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection'
                            , 'openerp-server', 'openerp-port', 'openerp-database', 'authorization' ]
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        
        response = Response(resp.content, resp.status_code, headers)
        return response    
    