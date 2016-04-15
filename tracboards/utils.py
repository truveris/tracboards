# Copyright (c) 2016 Truveris, Inc. All Rights Reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from datetime import timedelta, datetime


def safe_date_replace(date, **kw):
    """Replace a date with extra diaper."""
    while True:
        try:
            new_date = date.replace(**kw)
            return new_date
        except ValueError:
            date = date.replace(day=date.day - 1)
            continue


def format_date(d):
    today = datetime.now().date()
    if d.date() == today:
        return "Today"
    elif d.strftime("%U") == today.strftime("%U") and d.year == today.year:
        return d.strftime("%A")
    return d.strftime("%a %e %b")
