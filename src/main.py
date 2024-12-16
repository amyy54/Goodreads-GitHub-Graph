from flask import Flask, render_template, abort
import feedparser
from flask_apscheduler import APScheduler
from database import init_db, get_feeds, get_statuses, add_status
from objects import Status
from utils import offset_datetime, generate_contribution_chart, print_log_with_timestamp

app = Flask(__name__)

scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)


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


init_db()
scheduler.start()


@app.route("/")
def index():
    return "Hello World!"


@app.route("/user/<url_name>")
def fetch_user(url_name: str):
    feed_pull = get_feeds(url_name=url_name)
    if len(feed_pull) > 0:
        return render_template(
            "contrib_graph.html",
            data=generate_contribution_chart(get_statuses(gr_id=feed_pull[0].gr_id)),
        )
    else:
        abort(404)
