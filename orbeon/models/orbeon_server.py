# -*- coding: utf-8 -*-
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

import threading
import urllib2
import logging

from lxml import etree
from .. import services
_logger = logging.getLogger(__name__)

ORBEON_PERSISTENCE_SERVER_PREFIX = 'orbeon.persistence.server'
ORBEON_PERSISTENCE_SERVER_INTERFACE = '0.0.0.0'

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
    _name = 'orbeon.server'
    _inherit = ['mail.thread']
    _description = 'Orbeon Server'

    _rec_name = "url"

    name = fields.Char(
        "Name",
        required=True,
    )
    url = fields.Char(
        "URL",
        help='URL relative to Odoo server, the Odoo server will open the URL and proxy the response',
        required=True,
    )
    description = fields.Text(
        "Description"
    )

    persistence_server_port = fields.Char(
        "Port",
        required=True,
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

    persistence_server_configfile_path = fields.Char(
        "Config-file path",
        help="If specified, the Odoo connection is setup with its config, "
        "from file in given path. "
        "If blank, the Orbeon HTTP-Headers will be used."
    )

    persistence_server_active = fields.Boolean(
        "Active",
        default=False,
        help="Provisioning the persistence-server is enabled if active is checked (True).",
    )

    persistence_server_autostart = fields.Boolean(
        "Autostart",
        default=False,
        help="Ensures the persistence-server will be started right after Odoo starts"
    )

    persistence_server_uuid = fields.Char(
        "UUID (thread)",
        compute='_persistence_server_uuid',
        store=True
    )

    builder_template_ids = fields.One2many(
        "orbeon.builder.template",
        "server_id",
        string="Builder Form templates"
    )

    builder_templates_created = fields.Boolean(
        "Builder Form Templates Created",
        default=False,
        help="Whether Builder Form Templates had been created. Unset to delete and re-create Builder Template Forms."
    )

    def __init__(self, pool, cr):
        res = super(OrbeonServer, self).__init__(pool, cr)
        self._autostart_persistence_servers(pool, cr)
        return res

    @api.constrains("name")
    def constraint_unique_name(self):
        cur_record = self.search([("name", "=", self.name)])
        if len(cur_record) > 1:
            raise ValidationError("Server with name '%s' already exists!" % self.name)

    @api.constrains("url")
    def constraint_unique_url(self):
        cur_record = self.search([("url", "=", self.url)])
        if len(cur_record) > 1:
            raise ValidationError("Server with URL '%s' already exists!" % self.url)

    @api.multi
    def start_persistence_server(self, context=None, *args, **kwargs):
        if not self.persistence_server_active:
            raise ValidationError("Server with name %s can't start, because marked inactive." % self.name)

        try:
            uuid = self._persistence_server_uuid()

            self._start_persistence_server(
                uuid,
                self.persistence_server_port,
                self.persistence_server_processtype,
                self.persistence_server_configfile_path or ''
            )
            self.persistence_server_uuid = uuid

            self.create_orbeon_builder_templates()

            return True
        except Exception, e:
            _logger.error('Exception: %s' % e)

    @api.multi
    def stop_persistence_server(self, context=None, *args, **kwargs):
        self._stop_persistence_server(self.persistence_server_uuid, self.persistence_server_port)
        self.persistence_server_uuid = None
        return True

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

    def _is_installed(self, pool, cr):
        cr.execute(
                "SELECT "
                "    1 "
                "  FROM"
                "    ir_module_module "
                "  WHERE "
                "    name = 'orbeon' "
                "    AND state = 'installed' "
            )

        return cr.fetchone() is not None

    def _autostart_persistence_servers(self, pool, cr):
        """These (last resort) SQL could led to API-change breakage.  However,
        currently funky errors with ORM search/reads on
        odoo.api.Environment.
        """
        if not self._is_installed(pool, cr):
            return

        try:
            cr.execute(
                "SELECT "
                "    id, "
                "    persistence_server_active AS active,"
                "    persistence_server_autostart AS autostart,"
                "    persistence_server_uuid AS uuid,"
                "    persistence_server_port AS port,"
                "    persistence_server_processtype AS processtype,"
                "    persistence_server_configfile_path AS configfile_path"
                "  FROM"
                "    orbeon_server "
                "  WHERE "
                "    persistence_server_active = True "
            )

            for (id, active, autostart, uuid, port, processtype, configfile_path) in cr.fetchall():
                # Stop
                self._stop_persistence_server(uuid, port)
                cr.execute("UPDATE orbeon_server SET persistence_server_uuid = NULL WHERE id = %s", (id,))

                # Start
                if autostart:
                    new_uuid = self._persistence_server_uuid()
                    self._start_persistence_server(
                        new_uuid,
                        port,
                        processtype,
                        configfile_path
                    )
                    cr.execute("UPDATE orbeon_server SET persistence_server_uuid = %s WHERE id = %s", (str(new_uuid), id))

        except Exception, e:
            _logger.error("Exception: %s" % e)

    def _start_persistence_server(self, uuid, port, processtype, configfile_path=None):
        app = services.persistence_server.wsgi_server.create_app(configfile_path)
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
            if thread.getName() == uuid:
                thread.stopper.set()
                _logger.info("Stopping HTTP (werkzeug) %s (thread: %s) on port %s", ORBEON_PERSISTENCE_SERVER_PREFIX, uuid, port)
                thread.server.server_close()
                thread.join()

    @api.multi
    def create_orbeon_builder_templates(self):
        if self.builder_templates_created:
            return

        # XXX Once the listing (HTTP) request doesn't fail (HTTP 500),
        # this can be changed to a loop through all Orbeon example forms.
        #
        # Accorrding to https://doc.orbeon.com/form-runner/api/persistence/forms-metadata.html
        # HTTP GET on: /fr/service/persistence/form
        form_names = ['contact', 'controls']

        for form_name in form_names:
            try:
                url = "%s/fr/service/persistence/crud/orbeon/%s/form/form.xhtml" % (self.url, form_name)
                request = urllib2.Request(url)
                result = urllib2.urlopen(request)
                data = result.read()

                parser = etree.XMLParser(recover=True, encoding='utf-8')
                xml_root = etree.XML(data, parser)

                # TODO FIXME: multiple titles nodes (by language)
                form_name = xml_root.xpath('//metadata/form-name')[0].text

                xml = etree.tostring(xml_root)

                # First delete all related builder templates
                self.builder_template_ids.filtered(
                    lambda r: r.fetched_from_orbeon and r.form_name == form_name
                ).unlink()

                self.env['orbeon.builder.template'].create({
                    'server_id': self.id,
                    'module_id': self.env['ir.model.data'].xmlid_to_res_id('base.module_orbeon'),
                    'form_name': form_name,
                    'xml': xml,
                    'fetched_from_orbeon': True
                })

                self.builder_templates_created = True
            except Exception, e:
                _logger.error(
                    "%s - Orbeon request: %s" % (e, url)
                )
