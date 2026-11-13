#!/usr/bin/env python3
"""Answer an issue titled "ask: <question>" from my portfolio's own Ask API, then close it.

The API is retrieval over the site's own facts (BM25, no LLM), the same one behind the site's Ask
console and its MCP server. The reply is built only from what the API returns: nothing the asker
wrote is repeated back, so the bot can't be used to post someone else's links or mentions.

Environment: GH_TOKEN, REPO (owner/name), NUMBER (the issue), TITLE (the issue's title).
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request

SITE = "https://portfolio-emsghin2iq-as.a.run.app"
AGENT = "zhenxi0901-ask-bot"
LABEL = {"name": "ask", "color": "c2f75c", "description": "Answered by my portfolio's Ask API"}


def call(method: str, url: str, body=None, headers=None, timeout=20):
    """One HTTP request; returns (status, parsed JSON or None)."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={"User-Agent": AGENT, **(headers or {})})
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            return resp.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"null")
        except ValueError:
            return e.code, None


def github(method: str, path: str, body=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    status, data = call(method, f"https://api.github.com/repos/{os.environ['REPO']}{path}", body, headers)
    if status >= 400 and not (method == "POST" and path == "/labels" and status == 422):  # 422: the label exists
        raise SystemExit(f"GitHub {method} {path}: HTTP {status} {data}")
    return data


def question_from(title: str) -> str:
    """The question after the "ask:" prefix, on one line."""
    return re.sub(r"\s+", " ", re.sub(r"^\s*ask\s*:\s*", "", title, flags=re.I)).strip()


def links() -> dict:
    """Fact id -> its page on the site, from the same knowledge file the API answers from."""
    status, data = call("GET", f"{SITE}/knowledge.json")
    if status != 200 or not data:
        return {}
    return {f["id"]: SITE + f.get("href", "/") for f in data.get("facts", []) if f.get("id")}


def reply(question: str) -> tuple[str, str | None]:
    """The comment to post, and how to close the issue: "completed", "not_planned", or None to
    leave it open for a person."""
    footer = (
        "\n\n<sub>Ask again with a new issue titled <code>ask: …</code>, or ask from your own agent: "
        f"my site is an MCP server (<a href=\"{SITE}/agents\">how to connect</a>).</sub>"
    )
    if not 3 <= len(question) <= 300:
        return "Put a question of 3 to 300 characters after `ask:` in the title, and open a new issue." + footer, "not_planned"
    status, data = call("POST", f"{SITE}/api/ask", {"question": question})
    if status != 200 or not data or not data.get("answer"):
        why = f"HTTP {status}" if status else "no answer"
        return (
            f"My site didn't answer just now ({why}). Uptime checks watch it every minute: "
            f"[its status page]({SITE}/status) says how it is doing. I'll look at this issue myself." + footer,
            None,
        )
    pages = links()
    sources = []
    for s in data.get("sources") or []:
        title = s.get("title", "").replace("[", "(").replace("]", ")")
        href = pages.get(s.get("id", ""))
        sources.append(f"[{title}]({href})" if href else title)
    head = (
        f"> Answered by my portfolio's own [Ask API]({SITE}/about#ask): retrieval over the site's facts "
        "(BM25, no LLM), so every sentence below comes from a page you can open."
    )
    body = f"{head}\n\n{data['answer']}"
    if sources:
        body += "\n\n**From:** " + " · ".join(sources)
    return body + footer, "completed"


def main() -> int:
    number = os.environ["NUMBER"]
    text, close = reply(question_from(os.environ.get("TITLE", "")))
    github("POST", f"/issues/{number}/comments", {"body": text})
    if close == "completed":
        github("POST", "/labels", LABEL)
        github("POST", f"/issues/{number}/labels", {"labels": [LABEL["name"]]})
    if close:
        github("PATCH", f"/issues/{number}", {"state": "closed", "state_reason": close})
    print(f"closed as {close}" if close else "left open for a person")
    return 0


if __name__ == "__main__":
    sys.exit(main())
