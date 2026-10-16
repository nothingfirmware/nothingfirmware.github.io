import json, os, re, urllib.request
from datetime import datetime, timezone
from html import escape

URL = "https://nothingtools.github.io/update.json"
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
items = json.load(urllib.request.urlopen(req, timeout=30))
notes = {}
if os.path.exists("notes.json"):
    notes = json.load(open("notes.json", encoding="utf-8"))


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def paras(text):
    return "".join(f"<p>{escape(p.strip())}</p>" for p in text.split("\n\n") if p.strip())


cards = []
for it in items:
    title = re.sub(r"new update available for ", "", it["title"], flags=re.I).strip()
    version = it.get("version", "Unknown")
    date = it.get("date", "")
    image = it.get("image", "")
    slug = slugify(f"{title}-{version}")

    phone = re.search(r"OS|Phone", title, re.I)
    acc = re.search(r"Ear|Buds|Watch", title, re.I)
    if phone:
        path = "On your device: Settings &rarr; System &rarr; System Updates &rarr; Check for Update"
        fb = "On your device: Settings &rarr; System &rarr; Feedback"
        note = "For reference only, firmware rollouts are often staggered."
    elif acc:
        path = "Open the <strong style='display:inline'>Nothing X</strong> app, connect your Buds or Watch &rarr; About &rarr; Firmware Update"
        fb = "Submit feedback through the Nothing X or CMF Watch app"
        note = "Accessory firmware updates may take time to reach all regions."
    else:
        path = "App updates roll out automatically or via your app manager"
        fb = "Leave feedback on the community forums"
        note = "App updates roll out in phases."

    my_notes = paras(notes[slug]) if slug in notes else ""
    notes_html = (
        f'<div class="detail-box"><strong>Our notes:</strong>{my_notes}</div>' if my_notes else ""
    )

    cards.append(f"""
<article class="feed-card" id="{slug}">
  <img src="{escape(image)}" loading="lazy" class="feed-img" alt="{escape(title)} {escape(version)}" style="object-fit:cover;">
  <div class="feed-info">
    <div class="feed-date"><i class="fa-regular fa-clock"></i> {escape(date)}</div>
    <h3>{escape(title)}</h3>
    <p style="font-weight:600;color:#000;">Version: {escape(version)}</p>
    <details>
      <summary>View details</summary>
      <div class="detail-box"><strong>Update path:</strong>{path}</div>
      <div class="detail-box"><strong>Feedback:</strong>{fb}</div>
      {notes_html}
      <div class="detail-note"><span><strong>Note:</strong> {note}</span></div>
    </details>
  </div>
</article>""")

html = open("index.html", encoding="utf-8").read()
html = re.sub(
    r"<!-- FEED_START -->.*?<!-- FEED_END -->",
    lambda m: "<!-- FEED_START -->" + "".join(cards) + "\n<!-- FEED_END -->",
    html,
    flags=re.S,
)
html = re.sub(r'(<span id="logs-count">)[^<]*(</span>)', rf"\g<1>{len(items)}\2", html)
now = datetime.now(timezone.utc).strftime("%d %b %Y")
html = re.sub(r'(<span id="last-sync">)[^<]*(</span>)', rf"\g<1>{now}\2", html)
open("index.html", "w", encoding="utf-8").write(html)
print(len(items), "updates written")
