from flask import Flask, render_template, abort
import feedparser
from flask_apscheduler import APScheduler
from database import init_db, get_feeds, get_statuses, add_status
from objects import Status

app = Flask(__name__)

scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)


@scheduler.task("interval", id="fetch_rss", seconds=3600, misfire_grace_time=900)
def rss_fetch():
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
                    gr_date=entry["published_parsed"],
                    gr_title=entry["title"],
                    gr_link=entry["link"],
                    gr_description=entry["summary"],
                )
            )


scheduler.start()
init_db()


@app.route("/")
def index():
    return render_template("contrib_graph.html", data={})


@app.route("/user/<url_name>")
def fetch_user(url_name: str):
    feed_pull = get_feeds(url_name=url_name)
    if len(feed_pull) > 0:
        res = {}
        status = get_statuses(gr_id=feed_pull[0].gr_id)

        for entry in status:
            yday = entry.gr_date.tm_yday
            if yday in res.keys():
                res[yday]["count"] += 1

                if res[yday]["count"] > 4:
                    res[yday]["level"] = 3
                elif res[yday]["count"] > 2:
                    res[yday]["level"] = 2
                else:
                    res[yday]["level"] = 1
            else:
                res[yday] = {"count": 1, "level": 1}

        return render_template("contrib_graph.html", data=res)
    else:
        abort(404)
