#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008-2012 Zuza Software Foundation
#
# This file is part of Pootle.
#
# Pootle is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pootle is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pootle; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('pootle_translationproject.views',
    # Admin views
    (r'^(?P<language_code>[^/]*)/(?P<project_code>[^/]*)/((.*/)*)admin_permissions.html$',
        'admin_permissions'),

    # Management actions
    url(r'^(?P<language_code>[^/]*)/(?P<project_code>[^/]*)/rescan/?$',
        'rescan_files',
        name='tp.rescan'),
    url(r'^(?P<language_code>[^/]*)/(?P<project_code>[^/]*)/update/?$',
        'update_against_templates',
        name='tp.update_against_templates'),
    url(r'^(?P<language_code>[^/]*)/(?P<project_code>[^/]*)/delete/(?P<dir_path>(.*/)*)(?P<filename>.*\.*)?$',
        'delete_path_obj',
        name='tp.delete_path_obj'),

    # XHR views
    (r'^(?P<language_code>[^/]*)/(?P<project_code>[^/]*)/((.*/)*)edit_settings.html$',
        'edit_settings'),
    url(r'^(?P<language_code>[^/]*)/(?P<project_code>[^/]*)/summary/(?P<dir_path>(.*/)*)(?P<filename>.*\.*)?$',
        'path_summary_more',
        name='tp.path_summary_more'),

    # Exporting files
    (r'^(?P<language_code>[^/]*)/(?P<project_code>[^/]*)/(?P<file_path>.*)export/zip$',
        'export_zip'),

    # Overview
    url(r'^(?P<language_code>[^/]*)/(?P<project_code>[^/]*)/(?P<dir_path>(.*/)*)(?P<filename>.*\.*)?$',
        'overview',
        name='tp.overview'),
)
