from os import getenv
import os
from flask import Flask, render_template, abort, request
from flask_babel import Babel
import feedparser
from flask_apscheduler import APScheduler
from database import init_db, get_feeds, get_statuses, add_status
from objects import Status
from utils import (
    offset_datetime,
    generate_contribution_chart,
    print_log_with_timestamp,
    generate_data_list,
)

META_CONTACT_ADDR = getenv("META_CONTACT_ADDR", "contact@example.com")
ADMIN_URL_NAME = getenv("ADMIN_URL_NAME", "root")

app = Flask(__name__)

scheduler = APScheduler()
if app.debug:
    scheduler.api_enabled = True
scheduler.init_app(app)


def get_locale():
    # Gets the date the right way around
    return request.accept_languages.best_match(["en_US", "en_GB", "en"])


babel = Babel(app, locale_selector=get_locale)


@scheduler.task("interval", id="fetch_rss", seconds=3600, misfire_grace_time=900)
def rss_fetch():
    print_log_with_timestamp("Scheduler", "Fetching RSS feeds")
    for feed in get_feeds():
        rss = feedparser.parse(
            f"https://www.goodreads.com/user/updates_rss/{feed.gr_id}"
        )
        for entry in rss["entries"]:
            add_status(
                Status(
                    id=-1,
                    gr_id=feed.gr_id,
                    gr_guid=entry["id"],
                    gr_date=offset_datetime(entry["published"], feed.timezone),
                    gr_title=" ".join(entry["title"].split()),
                    gr_link=entry["link"],
                    gr_description=entry["summary"],
                )
            )


if not os.path.exists("lockfile.lock"):
    open("lockfile.lock", "a").close()
    init_db()

    scheduler.start()
    scheduler.run_job("fetch_rss")

    os.remove("lockfile.lock")


@app.route("/")
def index():
    return render_template(
        "home.html",
        chart_data=generate_contribution_chart([], random=True),
        contact_addr=META_CONTACT_ADDR,
        admin_url_name=ADMIN_URL_NAME,  # Otherwise the link could 404 due to the profile missing.
    )


@app.route("/user/<url_name>")
def fetch_user(url_name: str):
    feed_pull = get_feeds(url_name=url_name)
    if len(feed_pull) > 0:
        statuses = get_statuses(gr_id=feed_pull[0].gr_id)
        return render_template(
            "contrib_graph.html",
            chart_data=generate_contribution_chart(
                statuses, timezone=feed_pull[0].timezone
            ),
            url_name=feed_pull[0].url_name.title(),
            gr_id=feed_pull[0].gr_id,
            statuses=generate_data_list(statuses, timezone=feed_pull[0].timezone),
        )
    else:
        abort(404)
