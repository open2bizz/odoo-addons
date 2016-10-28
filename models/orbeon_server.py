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

class OrbeonServer(models.Model):
    _name = "orbeon.server"
    _rec_name = "base_url"

    name = fields.Char(
        "Name",
        required=True,
    )
    base_url = fields.Char(
        "Base URL",
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
    
    # TODO Still needed (is_active)?
    is_active = fields.Boolean(
        "Is active",
    )

    default_builder_xml = fields.Text(
        "Default Builder XML",
        help="Boilerplate XML (copied from the Orbeon<VERSION> server)",
        required=True
    )

    @api.one
    @api.depends("base_url")
    def _set_summary_url(self):
        if self.base_url:
            url = "%s/fr/orbeon/builder/summary" % self.base_url
        else:
            url = "Enter base url"
        self.summary_url = url

    @api.constrains("name")
    def constraint_unique_name(self):
        cur_record = self.search([("name","=",self.name)])
        if len(cur_record) > 1:
            raise ValidationError("Server with name '%s' already exists!" % self.name)
