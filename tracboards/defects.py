# Copyright (c) 2016 Truveris, Inc. All Rights Reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import json

from trac.core import Component, implements
from trac.web import IRequestHandler
from trac.config import Option

from providers import TemplateProvider


class DefectDashboardJSON(Component):

    ticket_type = Option("tracboards", "defects.ticket_type", default="defect",
                         doc="Type of your defect tickets")

    implements(IRequestHandler)

    # IRequestHandler methods
    def match_request(self, req):
        return req.path_info == "/dashboard/defects.json"

    def process_request(self, req):
        # All the opened defects by component, in current releases.
        with self.env.db_query as db:
            cursor = db.cursor()
            cursor.execute("""
                SELECT coalesce(component, '?!?'), count(*)
                FROM ticket t
                    LEFT JOIN milestone m ON t.milestone = m.name
                WHERE type = %s
                    AND m.due != 0
                    AND m.completed = 0
                    AND status = 'new'
                GROUP BY 1
            """, (self.ticket_type,))
            new_opened_by_component = dict(cursor)

        # All the opened defects by component, in current releases.
        with self.env.db_query as db:
            cursor = db.cursor()
            cursor.execute("""
                SELECT coalesce(component, '?!?'), count(*)
                FROM ticket t
                    LEFT JOIN milestone m ON t.milestone = m.name
                WHERE type = %s
                    AND m.due != 0
                    AND m.completed = 0
                    AND status NOT IN ('new', 'closed')
                GROUP BY 1
            """, (self.ticket_type,))
            triaged_opened_by_component = dict(cursor)

        # All high priority defects.
        with self.env.db_query as db:
            cursor = db.cursor()
            cursor.execute("""
                SELECT count(*)
                FROM ticket t
                    LEFT JOIN enum p ON p.name = t.priority AND p.type = 'priority'
                    LEFT JOIN milestone m ON t.milestone = m.name
                WHERE t.type = %s
                    AND m.due != 0
                    AND m.completed = 0
                    AND status != 'closed'
                    AND cast(p.value as int) < 4
            """, (self.ticket_type,))
            blocker_count = list(cursor)[0][0]

        # All the closed defect by owner, in current releases.
        with self.env.db_query as db:
            cursor = db.cursor()
            cursor.execute(r"""
                SELECT coalesce(owner, '?!?'), count(*)
                FROM ticket t
                    LEFT JOIN milestone m ON t.milestone = m.name
                WHERE type = %s
                    AND m.due != 0
                    AND m.completed = 0
                    AND status = 'closed'
                    AND resolution = 'fixed'
                GROUP BY 1
            """, (self.ticket_type,))
            closed_by_owner = dict(cursor)

        content = {
            "new_opened_by_component": new_opened_by_component,
            "triaged_opened_by_component": triaged_opened_by_component,
            "closed_by_owner": closed_by_owner,
            "blocker_count": blocker_count,
        }
        req.send(json.dumps(content), "application/json")


class DefectDashboard(TemplateProvider):

    implements(IRequestHandler)

    # IRequestHandler methods
    def match_request(self, req):
        return req.path_info == "/dashboard/defects"

    def process_request(self, req):
        return ("defects.html", {}, None)
