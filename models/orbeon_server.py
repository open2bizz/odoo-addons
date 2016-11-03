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
from odoo import models, fields, api
from odoo.exceptions import ValidationError

from .. import services

import threading
import logging
_logger = logging.getLogger(__name__)

ORBEON_PERSISTENCE_SERVER_PREFIX = 'orbeon.persistence.server'
ORBEON_PERSISTENCE_SERVER_INTERFACE = '127.0.0.1'

PERSISTENCE_SERVER_SINGLE_THREADED = 'SINGLE_THREADED'
PERSISTENCE_SERVER_MULTI_THREADED = 'MULTI_THREADED'
PERSISTENCE_SERVER_FORKING = 'FORKING'

class OrbeonThreadedWSGIServer(threading.Thread):
    
    def __init__(self, name, server, stopper):
        super(OrbeonThreadedWSGIServer, self).__init__(name=name)

        self.local = threading.local()
        self.local.server = server
        self.local.stopper = stopper
        self.server = self.local.server
        self.stopper = self.local.stopper

    def run(self):
        while not self.stopper.is_set():
            try:
                self.server.serve_forever()
            except:
                pass

class OrbeonServer(models.Model):
    _name = "orbeon.server"
    _rec_name = "url"

    name = fields.Char(
        "Name",
        required=True,
    )
    url = fields.Char(
        "URL",
        required=True,
    )
    summary_url = fields.Char(
        "Summary URL",
        compute="_set_summary_url",
        store=True,
    )
    description = fields.Text(
        "Description"
    )

    persistence_server_port = fields.Char(
        "Persistence server port"
    )

    persistence_server_processtype = fields.Selection(
        [
            (PERSISTENCE_SERVER_SINGLE_THREADED, "Single thread"),
            (PERSISTENCE_SERVER_MULTI_THREADED, "Multi thread"),
            (PERSISTENCE_SERVER_FORKING, "Forking (process)"),
        ],
        "Persistence server proces-type",
        default=PERSISTENCE_SERVER_SINGLE_THREADED,
        required=True)

    # todo Still needed (is_active)?
    is_active = fields.Boolean(
        "Is active",
    )

    default_builder_xml = fields.Text(
        "Default Builder XML",
        help="Boilerplate XML (copied from the Orbeon<VERSION> server)",
        required=True
    )

    def __init__(self, pool, cr):
        res = super(OrbeonServer, self).__init__(pool, cr)

        # TODO enable again
        #self._autostart_persistence_servers(pool, cr)
        return res

    @api.one
    @api.depends("url")
    def _set_summary_url(self):
        if self.url:
            url = "%s/fr/orbeon/builder/summary" % self.url
        else:
            url = "Enter URL"
        self.summary_url = url

    @api.constrains("name")
    def constraint_unique_name(self):
        cur_record = self.search([("name","=",self.name)])
        if len(cur_record) > 1:
            raise ValidationError("Server with name '%s' already exists!" % self.name)

    @api.constrains("url")
    def constraint_unique_url(self):
        cur_record = self.search([("url","=",self.url)])
        if len(cur_record) > 1:
            raise ValidationError("Server with URL '%s' already exists!" % self.url)

    @api.multi
    def action_start_persistence_server(self, context=None, *args, **kwargs):
        self._start_persistence_server(self.persistence_server_port, self.persistence_server_processtype)

    @api.multi
    def action_stop_persistence_server(self, context=None, *args, **kwargs):
        self._stop_persistence_server(self.persistence_server_port)

    # def application(self, environment, start_response):
    #     start_response('200 OK', [('Content-Type', 'text/plain')])
    #     return ['Hello World!']

    def _persistence_server_name(self, uuid):
        #TODO
        # uuid_generate_v4() on start/stop!!! Not here
        
        dbuuid = self.env['ir.config_parameter'].get_param('database.uuid')
        return "%s.%s" % (ORBEON_PERSISTENCE_SERVER_PREFIX, uuid)

    def _persistence_wsgi_server(self, server_processtype):
        from werkzeug.serving import BaseWSGIServer, ThreadedWSGIServer, ForkingWSGIServer

        if server_processtype == PERSISTENCE_SERVER_SINGLE_THREADED:
            return BaseWSGIServer
        elif server_processtype == PERSISTENCE_SERVER_MULTI_THREADED:
            return ThreadedWSGIServer
        elif server_processtype == PERSISTENCE_SERVER_FORKING:
            return ForkingWSGIServer

    def _autostart_persistence_servers(self, pool, cr):
        try:
            cr.execute("SELECT persistence_server_port, persistence_server_processtype FROM orbeon_server")
            for (port, server_processtype) in cr.fetchall():
                self._start_persistence_server(port, server_processtype)
        except:
            pass
        
    def _start_persistence_server(self, port, server_processtype):
        dbuuid = self.env['ir.config_parameter'].get_param('database.uuid')

        app = services.wsgi_server.app
        wsgi_server = self._persistence_wsgi_server(server_processtype)
        wsgi_app_server = wsgi_server(ORBEON_PERSISTENCE_SERVER_INTERFACE, port, app)
        
        stopper = threading.Event()

        t = OrbeonThreadedWSGIServer(
            name=self._persistence_server_name(dbuuid),
            server=wsgi_app_server,
            stopper=stopper
        )
        
        t.setDaemon(True)
        _logger.info('Initiating HTTP %s (werkzeug) START on port %s', self._persistence_server_name(dbuuid), port)
        t.start()
        
    def _stop_persistence_server(self, port):
        # TODO uuid_generate and cache/store somehwere?
        dbuuid = self.env['ir.config_parameter'].get_param('database.uuid')
        
        for thread in threading.enumerate():
            if thread.getName() == self.persistence_server_name(dbuuid):
                thread.stopper.set()
                _logger.info("Initiating HTTP %s (werkzeug) SHUTDOWN on port %s", self.persistence_server_name(dbuuid), port)
                thread.server.server_close()
                thread.join()
