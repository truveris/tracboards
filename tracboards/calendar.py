# Copyright (c) 2016 Truveris, Inc. All Rights Reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import re
import json
from datetime import timedelta, datetime

from trac.wiki.api import WikiSystem
from trac.wiki.model import WikiPage
from trac.core import Component, implements
from trac.web import IRequestHandler
from trac.ticket import model
from trac.util.datefmt import parse_date

from providers import TemplateProvider


re_date = re.compile(r".*Date: ([-/\d]+)$")
re_icon = re.compile(r".*Icon: ([-\w]+)$")
re_color = re.compile(r".*Color: ([#\w]+)$")
re_title = re.compile(r"^= ([\w\s()]+) =$")
re_name = re.compile(r".*Name: ([-:()\s\w]+)$")


class CalendarDashboardJSON(Component):

    implements(IRequestHandler)

    def get_events(self):
        events = {}

        for key, value in self.env.config.options("tracboards"):
            if not key.startswith("calendar."):
                continue

            tokens = key.split(".", 2)
            if len(tokens) != 3:
                self.env.log.warn("invalid calendar key: {}".format(key))
                continue

            _, event_name, key = tokens
            event = events.setdefault(event_name, {})
            if key == "delta":
                value = int(value)
            event[key] = value

        return events

    def get_milestone_event_dates(self):
        dates = []

        events = self.get_events()

        for milestone in self.get_milestones():
            for event_key, event in events.items():
                delta = timedelta(days=event.get("delta", 0))
                event_date = milestone.due + delta

                if event_date.date() < datetime.now().date():
                    continue

                dates.append({
                    "name": event.get("name", "Unnamed event"),
                    "icon": event.get("icon", "flag"),
                    "class": event_key,
                    "color": event.get("color", "white"),
                    "milestone": milestone.name,
                    "date": event_date,
                })

        return dates

    def get_wiki_event_dates(self):
        """Try to fetch events from the wiki as well."""
        dates = []

        for page in WikiSystem(self.env).get_pages("Events/"):
            page = WikiPage(self.env, page)
            if not page.exists:
                continue

            date = {
                "name": page.name.split("/", 1).pop(),
                "icon": "flag",
                "color": "white",
                "milestone": "",
                "class": page.name.split("/").pop().lower(),
            }

            for line in page.text.splitlines():
                m = re_date.match(line)
                if m:
                    date["date"] = parse_date(m.group(1))
                m = re_icon.match(line)
                if m:
                    date["icon"] = m.group(1)
                m = re_color.match(line)
                if m:
                    date["color"] = m.group(1)
                m = re_name.match(line)
                if m:
                    date["name"] = m.group(1)
                m = re_title.match(line)
                if m:
                    date["name"] = m.group(1)

            if date["date"] is not None and date["date"] >= parse_date("now"):
                dates.append(date)

        return dates

    def get_event_dates(self):
        event_dates = sorted(
            self.get_milestone_event_dates() + self.get_wiki_event_dates(),
            key=lambda ed: ed["date"]
        )

        for ed in event_dates:
            ed["date"] = self.format_date(ed["date"])

        return event_dates

    def format_date(self, d):
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        if d.date() == today:
            return "Today"
        if d.date() == tomorrow:
            return "Tomorrow"
        if d.date() - today < timedelta(days=6):
            return d.strftime("%A")
        return d.strftime("%a %m/%e")

    def get_milestones(self):
        milestones = model.Milestone.select(self.env, include_completed=False)
        return [m for m in milestones if m.due is not None]

    # IRequestHandler methods
    def match_request(self, req):
        return req.path_info == "/dashboard/calendar.json"

    def process_request(self, req):
        content = {
            "event_dates": self.get_event_dates(),
        }

        req.send(json.dumps(content), "application/json")


class CalendarDashboard(TemplateProvider):

    implements(IRequestHandler)

    # IRequestHandler methods
    def match_request(self, req):
        return req.path_info == "/dashboard/calendar"

    def process_request(self, req):
        return ("calendar.html", {}, None)
