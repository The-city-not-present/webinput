# Dates & time

- **Store in UTC.** Dates and timestamps produced or stored by the backend are
  in UTC. Full timestamps are ISO-8601 with an explicit UTC designator
  (`2025-07-15T10:00:00Z`); calendar dates with no time are `YYYY-MM-DD`.
- **Show in local time.** The frontend displays dates in the browser's local
  timezone. `new Date(isoString)` and the date formatting APIs already do the
  conversion — no manual timezone math.
- **User-entered dates are local.** A date entered by the user in the web UI is
  interpreted in the browser's local timezone (the same timezone used for
  display). Interpret it in a specific timezone only when the UI/requirements
  explicitly capture that timezone.
- **No hardcoded dates.** Don't put dates in implementation code. Dates come
  from the backend/database, or are generated when an object is created (e.g.
  `datetime.now(timezone.utc)`, as `src/input.py` already does).
- **Webinput renders datetimes through the native `<input type="datetime-local">`
  control** (`widgets/widget_datetime.py`). A raw date/datetime string is only
  allowed at that DOM boundary; convert to/from the model value there.
