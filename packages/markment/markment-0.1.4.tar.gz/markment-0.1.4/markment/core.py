# -*- coding: utf-8 -*-
# <markment - markdown-based documentation generator for python>
# Copyright (C) <2013>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import unicode_literals

import json
import yaml
from os.path import basename
from functools import partial
from collections import OrderedDict

from .fs import Node, TreeMaker
from .engine import Markment
from .views import TemplateContext


class Project(object):
    metadata_filename = '.markment.yml'

    def __init__(self, path):
        self.path = path

        self.node = Node(path)
        self.tree = TreeMaker(path)
        self.name = basename(path)
        self.version = ''
        self.description = ''

        documentation_index_fallback = 'README.md'

        found = self.node.grep(r'\.(md|markdown)')

        if found:
            documentation_index_fallback = found[0].basename

        self.meta = {
            'project': {
                'name': self.name,
            },
            'documentation': {
                'index': documentation_index_fallback
            }
        }
        self._found_files = OrderedDict()
        self.load(path)

    def load(self, path):
        metadata = self.parse_metadata(path)

        self.meta.update(metadata)

        p = self.meta['project']
        self.name = p.get('name', self.name)
        self.version = p.get('version', self.version)
        self.description = p.get('description', self.description)
        self.github_url = p.get('github_url', '')

        tarball_fallback = zipball_fallback = ''

        if self.github_url:
            tarball_fallback = '{0}/archive/master.tar.gz'.format(self.github_url)
            zipball_fallback = '{0}/archive/master.zip'.format(self.github_url)

        self.zipball_download_url = p.get('zipball_download_url', zipball_fallback)
        self.tarball_download_url = p.get('tarball_download_url', tarball_fallback)

    def parse_metadata(self, path):
        if not self.node.contains(self.metadata_filename):
            return {}

        with self.node.open(self.metadata_filename) as f:
            data = f.read()

        return yaml.load(data.decode('utf-8'))

    def find_markdown_files(self):
        if self._found_files:
            return self._found_files

        for_blobs = lambda info: info['type'] == 'blob'
        blobs = filter(for_blobs, self.tree.find_all_markdown_files())

        for info in blobs:
            name = info['relative_path']
            self._found_files[name] = info

        return self._found_files

    def generate(self, theme, static_url_cb=None, link_cb=None, **kw):
        master_index = self.find_markdown_files().values()

        for info in master_index:
            yield self.render_html_from_markdown_info(
                info, theme, static_url_cb, link_cb, master_index, **kw)

    def render_html_from_markdown_info(
            self, info, theme, static_url_cb, link_cb, master_index, **kw):

        if static_url_cb:
            static_url_cb = partial(static_url_cb, current_document_info=info)

        if link_cb:
            link_cb = partial(link_cb, current_document_info=info)

        with self.node.open(info['path']) as f:
            data = f.read()

        decoded = data.decode('utf-8')

        md = Markment(decoded, url_prefix=link_cb)

        info['markdown'] = md.raw
        info['indexes'] = md.index()
        info['documentation'] = md.rendered

        Context = TemplateContext(
            project=self.meta['project'],
            documentation=md.rendered,
            index=md.index(),
            master_index=list(master_index),
            json=json,
            static_url_cb=static_url_cb,
            link_cb=link_cb,
            **kw)

        ctx = Context.ready_to_render()
        info['html'] = theme.render(**ctx).encode('utf-8')
        info['references'] = md.url_references
        return info

    @classmethod
    def discover(cls, path, *args, **kw):
        return cls(path, *args, **kw)

    def __repr__(self):
        return '<Project({0})>'.format(repr(self.path))
