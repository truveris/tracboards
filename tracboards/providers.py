# Copyright (c) 2016 Truveris, Inc. All Rights Reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from pkg_resources import resource_filename

from trac.core import Component, implements
from trac.web.chrome import ITemplateProvider


class TemplateProvider(Component):

    implements(ITemplateProvider)

    abstract = True

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        """Return the absolute path of a directory containing additional
        static resources (such as images, style sheets, etc).
        """
        return [('tracboards', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        """Return the absolute path of the directory containing the provided
        Genshi templates.
        """
        return [resource_filename(__name__, 'templates')]
