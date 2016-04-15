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
from utils import safe_date_replace, format_date


re_date = re.compile(r".*Date: ([-/\d]+)$")
re_icon = re.compile(r".*Icon: ([-\w]+)$")
re_color = re.compile(r".*Color: ([#\w]+)$")
re_frequency = re.compile(r".*Frequency: (\w+)$")
re_title = re.compile(r"^= ([\w\s()]+) =$")
re_name = re.compile(r".*Name: ([-:()\s\w]+)$")


class CalendarDashboardJSON(Component):

    implements(IRequestHandler)

    # Milestone event methods

    def get_event_templates(self):
        """Fetch the event templates from the configuration file."""

        templates = {}

        for key, value in self.env.config.options("tracboards"):
            if not key.startswith("calendar."):
                continue

            tokens = key.split(".", 2)
            if len(tokens) != 3:
                self.env.log.warn("invalid calendar key: {}".format(key))
                continue

            _, name, key = tokens
            t = templates.setdefault(name, {})
            if key == "delta":
                value = int(value)
            t[key] = value

        return templates

    def get_milestones(self):
        milestones = model.Milestone.select(self.env, include_completed=False)
        return [m for m in milestones if m.due is not None]

    def get_milestone_events(self):
        events = []

        templates = self.get_event_templates()

        for milestone in self.get_milestones():
            for key, template in templates.items():
                delta = timedelta(days=template.get("delta", 0))
                date = milestone.due + delta

                if date.date() < datetime.now().date():
                    continue
                events.append({
                    "name": template.get("name", "Unnamed event"),
                    "icon": template.get("icon", "flag"),
                    "class": key,
                    "color": template.get("color", "white"),
                    "milestone": milestone.name,
                    "date": date,
                })

        return events

    # Wiki event methods

    def get_raw_event_from_page(self, page):
        """Return an event as defined in the page.

        This function does not expand an event into multiple based on
        frequency, it only returns the values as-is.

        """
        event = {
            "name": page.name.split("/", 1).pop(),
            "icon": "flag",
            "color": "white",
            "milestone": "",
            "class": page.name.split("/").pop().lower(),
        }

        for line in page.text.splitlines():
            m = re_date.match(line)
            if m:
                event["date"] = parse_date(m.group(1))

            m = re_icon.match(line)
            if m:
                event["icon"] = m.group(1)

            m = re_color.match(line)
            if m:
                event["color"] = m.group(1)

            m = re_name.match(line)
            if m:
                event["name"] = m.group(1)

            m = re_title.match(line)
            if m:
                event["name"] = m.group(1)

            m = re_frequency.match(line)
            if m:
                frequency = m.group(1)
                if frequency in ("yearly", "monthly"):
                    event["frequency"] = frequency

        return event

    def expand_event(self, event, frequency):
        events = []

        today = parse_date("now").date()
        start_year = max(today.year, event["date"].year)
        end_year = today.year + 1

        if frequency == "yearly":
            for year in range(start_year, end_year):
                new_event = event.copy()
                new_event["date"] = safe_date_replace(
                        event["date"], year=year)
                events.append(new_event)
        elif frequency == "monthly":
            for year in range(start_year, end_year):
                for month in range(1, 13):
                    new_event = event.copy()
                    new_event["date"] = safe_date_replace(
                            event["date"], year=year)
                    events.append(new_event)

        events = [e for e in events if e["date"].date() > today]

        return events

    def get_events_from_page(self, page):
        event = self.get_raw_event_from_page(page)
        if event["date"] is None:
            return []

        frequency = event.get("frequency")
        if frequency:
            return self.expand_event(event, frequency)

        if event["date"].date() < parse_date("now").date():
            return []

        return [event]

    def get_wiki_pages(self):
        """Return all the wiki page instances in the Events/ namespace."""
        wiki_pages = []
        for page in WikiSystem(self.env).get_pages("Events/"):
            page = WikiPage(self.env, page)
            if not page.exists:
                continue
            wiki_pages.append(page)
        return wiki_pages

    def get_wiki_events(self):
        """Try to fetch events from the wiki as well."""
        pages = self.get_wiki_pages()
        return sum([self.get_events_from_page(p) for p in pages], [])

    def get_events(self):
        events = sorted(self.get_milestone_events() + self.get_wiki_events(),
                        key=lambda e: e["date"])

        for event in events:
            today = datetime.now().date()

            if event["date"].date() == today:
                group = None
            elif event["date"].date() == today + timedelta(days=1):
                group = "Tomorrow"
            elif (event["date"].isocalendar()[1] == today.isocalendar()[1] and
                  event["date"].year == today.year):
                group = "This Week"
            elif (event["date"].isocalendar()[1] == today.isocalendar()[1] + 1 and
                  event["date"].year == today.year):
                group = "Next Week"
            elif event["date"].month == today.month:
                group = "Later This Month"
            else:
                group = "Future"

            event.update({
                "date": format_date(event["date"]),
                "group": group,
            })

        return events

    # IRequestHandler methods

    def match_request(self, req):
        return req.path_info == "/dashboard/calendar.json"

    def process_request(self, req):
        content = {
            "events": self.get_events(),
        }
        req.send(json.dumps(content), "application/json")


class CalendarDashboard(TemplateProvider):

    implements(IRequestHandler)

    # IRequestHandler methods

    def match_request(self, req):
        return req.path_info == "/dashboard/calendar"

    def process_request(self, req):
        return ("calendar.html", {}, None)
