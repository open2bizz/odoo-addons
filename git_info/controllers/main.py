# -*- coding: utf-8 -*-
##############################################################################
#
#    open2bizz
#    Copyright (C) 2017 open2bizz (open2bizz.nl).
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

import subprocess

from datetime import datetime
from pytz import timezone
from functools32 import lru_cache

from odoo import http
from odoo.http import request
from odoo.tools import config
from odoo.addons.web_settings_dashboard.controllers.main import WebSettingsDashboard


class GitInfoWebSettingsDashboard(WebSettingsDashboard):

    @http.route()
    def web_settings_dashboard_data(self, **kw):
        res = super(GitInfoWebSettingsDashboard, self).web_settings_dashboard_data()
        res['share']['git_info'] = "%s" % self.get_git_info()

        return res

    @lru_cache()
    def get_git_info(self):
        """Returns a numeric identifier of the latest git changeset.
        The result is the timestamp of the changeset, in timezone of current user,
        in YYYYMMDDHHMMSS format.
        This value isn't guaranteed to be unique, but collisions are very unlikely,
        so it's sufficient for generating the development version numbers.
        """

        repo_dir = config['root_path']
        git_log = subprocess.Popen(
            'git log --pretty=format:%ct --quiet -1 HEAD',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=True, cwd=repo_dir, universal_newlines=True,
        )

        timestamp = git_log.communicate()[0]

        if not timestamp:
            return "Not a git repository"

        try:
            timestamp_utc = datetime.utcfromtimestamp(int(timestamp)).replace(tzinfo=timezone('UTC'))
            user_tz = timezone(request.context.get('tz') or request.env.user.tz or 'UTC')
            timestamp = timestamp_utc.astimezone(user_tz)
        except ValueError:
            return None
        return timestamp.strftime('%Y%m%d%H%M%S')
