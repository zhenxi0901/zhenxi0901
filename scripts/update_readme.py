#!/usr/bin/env python3
"""Rewrite the auto-updated sections of README.md from the GitHub API.

Sections sit between <!-- name:start --> and <!-- name:end --> markers. If a call fails, that
section keeps its previous content, so a bad API day never blanks the profile.
"""

import datetime as dt
import html
import json
import math
import os
import re
import sys
import urllib.parse
import urllib.request

USER = "zhenxi0901"
PORTFOLIO = f"{USER}/portfolio"
FIRST = ["hyscale-lab/ARIES"]  # repositories listed first in the merged pull requests
README = os.path.join(os.path.dirname(__file__), "..", "README.md")
SITE = "https://portfolio-emsghin2iq-as.a.run.app"
# The typing line's first sentences, which don't change; the live ones follow.
TYPING_FIXED = ["I run Kubernetes in production on Google Cloud", "I benchmark LLM agents on A100 GPUs"]
TYPING_URL = re.compile(r"(https://readme-typing-svg\.demolab\.com\?[^\"]*?lines=)([^\"&]*)")
TYPING_ALT = re.compile(r'(<img alt=")([^"]*)(" src="https://readme-typing-svg\.demolab\.com)')


def api(path: str):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": f"{USER}-readme"}
    if token := os.environ.get("GH_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"https://api.github.com{path}", headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def cell(text: str) -> str:
    """Make text safe inside a Markdown table cell."""
    return text.replace("|", "\\|").replace("\n", " ")


def plain(text: str) -> str:
    """Words from someone else's repository (a pull request title, which its maintainers can edit),
    shown as words: no HTML, links, images or emphasis can come through."""
    return re.sub(r"([\\`*_\[\]])", r"\\\1", html.escape(text, quote=False))


def merged_prs(per_repo: int = 3) -> str:
    """My merged pull requests to other people's public repositories, grouped by repository.

    Repositories in FIRST lead, in that order; the rest follow by their most recent merge.
    """
    query = f"author:{USER} is:pr is:merged is:public -user:{USER}"
    items = api(f"/search/issues?q={urllib.parse.quote(query)}&sort=updated&order=desc&per_page=100")["items"]
    by_repo: dict[str, list[tuple[str, str]]] = {}
    for it in items:
        repo = it["repository_url"].split("/repos/", 1)[1]
        merged = (it.get("pull_request") or {}).get("merged_at") or it["closed_at"]
        line = f"  - [#{it['number']}]({it['html_url']}) {plain(it['title'])} <sub>merged {merged[:10]}</sub>"
        by_repo.setdefault(repo, []).append((merged, line))
    for prs in by_repo.values():
        prs.sort(reverse=True)
    # Other repositories only while they are current: something merged in the last year.
    cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=365)).isoformat()
    pinned = [r for r in FIRST if r in by_repo]
    rest = sorted(
        (r for r in by_repo if r not in FIRST and by_repo[r][0][0] >= cutoff),
        key=lambda r: by_repo[r][0][0],
        reverse=True,
    )
    out = []
    for repo in pinned + rest:
        prs = by_repo[repo]
        out.append(f"- **[{repo}](https://github.com/{repo})**: {len(prs)} merged")
        out.extend(line for _, line in prs[: per_repo if repo in FIRST else 2])
    return "\n".join(out) or "_Nothing merged yet._"


def open_prs(limit: int = 6) -> str:
    """My open pull requests to other people's public repositories, newest first."""
    query = f"author:{USER} is:pr is:open is:public -user:{USER}"
    items = api(f"/search/issues?q={urllib.parse.quote(query)}&sort=created&order=desc&per_page={limit}")["items"]
    lines = []
    for it in items:
        repo = it["repository_url"].split("/repos/", 1)[1]
        draft = " (draft)" if it.get("draft") else ""
        lines.append(f"- **[{repo}#{it['number']}]({it['html_url']})** {plain(it['title'])}{draft} <sub>opened {it['created_at'][:10]}</sub>")
    return "\n".join(lines) or "_Nothing open right now._"


def deploys(limit: int = 5) -> str:
    """The portfolio's latest finished deploys: commit, result, date and duration."""
    runs = api(f"/repos/{PORTFOLIO}/actions/workflows/deploy.yml/runs?per_page=30")["workflow_runs"]
    done = [r for r in runs if r["status"] == "completed" and r["conclusion"] in ("success", "failure")][:limit]
    parse = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    lines = ["| Commit | Result | Started (UTC) | Took |", "|---|---|---|---|"]
    for r in done:
        took = int((parse(r["updated_at"]) - parse(r["run_started_at"])).total_seconds())
        msg = cell(plain(r["head_commit"]["message"].splitlines()[0]))[:80]
        sha = r["head_sha"]
        result = "passed" if r["conclusion"] == "success" else "failed"
        started = r["run_started_at"][:16].replace("T", " ")
        lines.append(f"| [`{sha[:7]}`](https://github.com/{PORTFOLIO}/commit/{sha}) {msg} | [{result}]({r['html_url']}) | {started} | {took // 60}m {took % 60:02d}s |")
    return "\n".join(lines) if done else "_No deploys yet._"


def site(path: str):
    """JSON from my portfolio."""
    req = urllib.request.Request(SITE + path, headers={"User-Agent": f"{USER}-readme"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def typing_lines() -> list[str]:
    """What the typing line cycles through: the fixed sentences with the live ones between them, so a
    live one shows early. No commit and no relative time: the line is only redrawn a few times a day,
    and the live-commit badge right below it says which commit is running."""
    slo, delivery = site("/api/slo"), site("/delivery.json")
    live = []
    if slo.get("available"):
        av = slo["availability"]
        # The site's own rule: two decimals rounded down, and a plain 100% when nothing failed.
        up = "100%" if av >= 1 else f"{math.floor(av * 1e4 + 1e-6) / 100:.2f}%"
        days = slo.get("window_days", 30)
        since = dt.datetime.fromisoformat(slo["since"].replace("Z", "+00:00")) if slo.get("since") else None
        if since and (dt.datetime.now(dt.timezone.utc) - since).days < days:
            window = f"since {since.day} {since:%b}"
        else:
            window = f"over {days} days"
        line = f"Portfolio: {up} up {window}"
        if delivery.get("deploys"):
            line += f", {delivery['deploys']} deploys in {delivery['windowDays']} days"
        live.append(line)
    query = f"author:{USER} is:pr is:merged is:public -user:{USER}"
    items = api(f"/search/issues?q={urllib.parse.quote(query)}&sort=updated&order=desc&per_page=20")["items"]
    if items:
        it = max(items, key=lambda i: (i.get("pull_request") or {}).get("merged_at") or i["closed_at"])
        live.append(f"Just merged: {it['repository_url'].split('/repos/', 1)[1]}#{it['number']}")
    lines = [TYPING_FIXED[0], *live[:1], TYPING_FIXED[1], *live[1:], "Open an issue titled ask: … and my site replies"]
    # A semicolon would end a line early in the service's URL.
    return [line.replace(";", ",") for line in lines]


def set_typing(text: str, lines: list[str]) -> str:
    """Write the sentences into every readme-typing-svg URL, and the image's alt text."""
    encoded = ";".join(urllib.parse.quote_plus(line) for line in lines)
    if not TYPING_URL.search(text):
        raise ValueError("typing line not found")
    text = TYPING_URL.sub(lambda m: m.group(1) + encoded, text)
    alt = html.escape(" ".join(line if line.endswith(("…", ".")) else line + "." for line in lines), quote=True)
    return TYPING_ALT.sub(lambda m: m.group(1) + alt + m.group(3), text)


def replace(text: str, name: str, body: str) -> str:
    pattern = re.compile(rf"(<!-- {name}:start -->\n).*?(\n<!-- {name}:end -->)", re.S)
    if not pattern.search(text):
        raise ValueError(f"markers for {name} not found")
    return pattern.sub(lambda m: m.group(1) + body + m.group(2), text)


def main() -> int:
    with open(README, encoding="utf-8") as f:
        text = f.read()
    updated = text
    for name, build in (("open-prs", open_prs), ("merged-prs", merged_prs), ("deploys", deploys)):
        try:
            updated = replace(updated, name, build())
        except Exception as e:  # keep the old section; say why in the job log
            print(f"warning: {name} not updated: {e}", file=sys.stderr)
    try:
        updated = set_typing(updated, typing_lines())
    except Exception as e:  # keep the old line
        print(f"warning: typing line not updated: {e}", file=sys.stderr)
    if updated != text:
        with open(README, "w", encoding="utf-8", newline="\n") as f:
            f.write(updated)
        print("README updated")
    else:
        print("README unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
