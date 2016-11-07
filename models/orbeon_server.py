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

    persistence_server_active = fields.Boolean(
        "Active",
        default=False,
    )

    persistence_server_uuid = fields.Char(
        "UUID (thread)",
        compute='_persistence_server_uuid',
        store=True
    )
    
    persistence_server_port = fields.Char(
        "Port"
    )

    persistence_server_processtype = fields.Selection(
        [
            (PERSISTENCE_SERVER_SINGLE_THREADED, "Single threaded"),
            (PERSISTENCE_SERVER_MULTI_THREADED, "Multi threaded"),
            (PERSISTENCE_SERVER_FORKING, "Forking (process)"),
        ],
        "Process-type",
        default=PERSISTENCE_SERVER_SINGLE_THREADED,
        required=True
    )

    persistence_server_configfilename = fields.Char(
        "Config-filename"
    )

    default_builder_xml = fields.Text(
        "Default Builder XML",
        help="Boilerplate XML (copied from the Orbeon<VERSION> server)",
        required=True
    )

    def __init__(self, pool, cr):
        res = super(OrbeonServer, self).__init__(pool, cr)
        self._autostart_persistence_servers(pool, cr)
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
        try:
            uuid = self._persistence_server_uuid()
            
            self._start_persistence_server(
                uuid,
                self.persistence_server_port,
                self.persistence_server_processtype,
                self.persistence_server_configfilename
            )
            self.persistence_server_uuid = uuid
        except Exception, e:
            _logger.error('Exception: %s' % e)

    @api.multi
    def action_stop_persistence_server(self, context=None, *args, **kwargs):
        self._stop_persistence_server(self.persistence_server_uuid, self.persistence_server_port)
        self.persistence_server_uuid = None

    def _persistence_server_uuid(self):
        from uuid import uuid4
        return uuid4()

    def _persistence_wsgi_server(self, processtype):
        from werkzeug.serving import BaseWSGIServer, ThreadedWSGIServer, ForkingWSGIServer

        if processtype == PERSISTENCE_SERVER_SINGLE_THREADED:
            return BaseWSGIServer
        elif processtype == PERSISTENCE_SERVER_MULTI_THREADED:
            return ThreadedWSGIServer
        elif processtype == PERSISTENCE_SERVER_FORKING:
            return ForkingWSGIServer

    def _autostart_persistence_servers(self, pool, cr):
        try:
            cr.execute(
                "SELECT "
                "    id, "
                "    persistence_server_active AS active,"
                "    persistence_server_uuid AS uuid,"
                "    persistence_server_port AS port,"
                "    persistence_server_processtype AS processtype,"
                "    persistence_server_configfilename AS configfilename"
                "  FROM"
                "    orbeon_server"
            )
            
            for (id,active,uuid,port,processtype,configfilename) in cr.fetchall():
                # In case there's already a thread running on the UUID, don't start it again (twice) - Hence the `else` on the `for` loop.
                # This triggers: error(98, 'Address already in use')
                for thread in threading.enumerate():
                    # Don't start if thread/port is already in use.
                    if thread.getName() == uuid:
                        break;
                else:
                    # Force clear (uuid) which ensures a clean start
                    cr.execute("UPDATE orbeon_server SET persistence_server_uuid = NULL WHERE id = '%s'" % (id))
                    
                    if not active:
                        return
                    
                    # Can start (thread isn't in use)
                    new_uuid = self._persistence_server_uuid()
                                     
                    self._start_persistence_server(
                        new_uuid,
                        persistence_server_port,
                        persistence_server_processtype,
                        persistence_server_configfilename
                    )

                    cr.execute("UPDATE orbeon_server SET persistence_server_uuid = %s WHERE id = %s", (str(new_uuid), id))
                
        except Exception, e:
            _logger.error("Exception: %s" % e)

    def _start_persistence_server(self, uuid, port, processtype, configfilename=None):
        app = services.wsgi_server.create_app(configfilename)
        wsgi_server = self._persistence_wsgi_server(processtype)
        wsgi_app_server = wsgi_server(ORBEON_PERSISTENCE_SERVER_INTERFACE, port, app)

        stopper = threading.Event()

        t = OrbeonThreadedWSGIServer(
            name=uuid,
            server=wsgi_app_server,
            stopper=stopper
        )
        
        t.setDaemon(True)
        _logger.info('Starting HTTP (werkzeug) %s (thread: %s) on port %s', ORBEON_PERSISTENCE_SERVER_PREFIX, uuid, port)
        t.start()
        
    def _stop_persistence_server(self, uuid, port):
        for thread in threading.enumerate():
            if thread.getName() == uuid: # TODO uuid
                thread.stopper.set()
                _logger.info("Stopping HTTP (werkzeug) %s (thread: %s) on port %s", ORBEON_PERSISTENCE_SERVER_PREFIX, uuid, port)
                thread.server.server_close()
                thread.join()
