"""Build feed.xml (Apple Podcasts RSS) from episodes.json.
episodes.json: list of {id, title, lead, date, duration, points[], actions[]}; audio at episodes/<id>.mp3.
Usage: python3 build_feed.py https://ianquanu-web.github.io/podcast
"""
import json, os, sys, email.utils, datetime
from xml.sax.saxutils import escape

base = sys.argv[1].rstrip("/")
here = os.path.dirname(os.path.abspath(__file__))
eps = json.load(open(os.path.join(here, "episodes.json"), encoding="utf-8"))
eps.sort(key=lambda e: e["date"], reverse=True)

def notes(e):
    s = e.get("lead", "") + "\n\n要点：\n" + "\n".join(f"{i+1}. {p}" for i, p in enumerate(e.get("points", [])))
    s += "\n\n行动建议：\n" + "\n".join(f"- {a}" for a in e.get("actions", []))
    return s

items = []
for e in eps:
    path = os.path.join(here, "episodes", e["id"] + ".mp3")
    size = os.path.getsize(path)
    d = datetime.datetime.fromisoformat(e["date"] + "T15:00:00-04:00")
    dur = int(e.get("duration", 0))
    items.append(f"""    <item>
      <title>{escape(e['title'])}</title>
      <description>{escape(notes(e))}</description>
      <itunes:summary>{escape(notes(e))}</itunes:summary>
      <enclosure url="{base}/episodes/{e['id']}.mp3" length="{size}" type="audio/mpeg"/>
      <guid isPermaLink="false">video-digest-{e['id']}</guid>
      <pubDate>{email.utils.format_datetime(d)}</pubDate>
      <itunes:duration>{dur//60:02d}:{dur%60:02d}</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
    </item>""")

feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>视频速听</title>
    <link>{base}/</link>
    <atom:link href="{base}/feed.xml" rel="self" type="application/rss+xml"/>
    <language>zh-cn</language>
    <description>把长视频听成几分钟：要点 + 可执行的行动建议。私人订阅。</description>
    <itunes:author>David Han</itunes:author>
    <itunes:image href="{base}/cover.jpg"/>
    <itunes:category text="Technology"/>
    <itunes:explicit>false</itunes:explicit>
    <itunes:block>Yes</itunes:block>
{chr(10).join(items)}
  </channel>
</rss>
"""
open(os.path.join(here, "feed.xml"), "w", encoding="utf-8").write(feed)
print("feed.xml", len(eps), "episodes")
