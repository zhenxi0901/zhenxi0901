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
    """One HTTP request: (status, parsed JSON or None). Status 0 means no answer at all: refused,
    reset or timed out. Never raises, so every failure still gets a reply on the issue."""
    # Plain UTF-8: escaped as \uXXXX pairs, a 300-character question of emoji would be too big for the API.
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={"User-Agent": AGENT, **(headers or {})})
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status, raw = resp.status, resp.read()
    except urllib.error.HTTPError as e:
        status, raw = e.code, e.read()
    except (OSError, ValueError):  # URLError and TimeoutError are OSErrors
        return 0, None
    try:
        return status, (json.loads(raw) if raw else None)
    except ValueError:  # an answer that isn't JSON: a proxy's error page, say
        return status, None


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


ASK = re.compile(r"^\s*ask\s*[:：]\s*(.*)$", re.I | re.S)  # "ask:", "Ask :", "ASK：" (full-width)


def question_from(title: str) -> str | None:
    """The question after the "ask:" prefix, on one line; None if the title isn't an ask."""
    m = ASK.match(title)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else None


def note_from(body: str) -> str:
    """What the asker wrote besides the question: the form's optional note, or a blank issue's body."""
    body = (body or "").strip()
    m = re.search(r"###\s*Anything else\?[^\n]*\n+(.*)", body, re.S)
    note = (m.group(1) if m else body).strip()
    return "" if note in ("", "_No response_") else note


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
    if status in (400, 413):  # the site's own words on what was wrong with it
        why = (data or {}).get("error") or "It couldn't take that question."
        return f"My site couldn't take that question: {why} Try a plainer one in a new issue." + footer, "not_planned"
    if status == 429:
        return "My site is answering a lot of questions right now. Ask again in a minute, in a new issue." + footer, "not_planned"
    if status == 200 and data and data.get("answer") and data.get("mode") != "retrieval":
        # Only retrieval answers are repeated here: sentences from the site's own pages, which a
        # question can't steer. A model's answer could be, so that one waits for me.
        return "My site answered with a language model this time, so I'll answer this one myself." + footer, None
    if status == 200 and data and data.get("answer") and not data.get("sources"):
        # The site's facts don't cover it (its reply is "I couldn't find that…"): no pretending.
        return (
            "My site's facts don't cover that one, so I'll answer it myself. Meanwhile, my "
            f"[portfolio]({SITE}) has the whole story, and a [contact form]({SITE}/about) that reaches me directly." + footer,
            None,
        )
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
    # No mentions, even by accident: "@name" gets a zero-width space, so nobody is pinged.
    answer = re.sub(r"(^|\s)@(\w)", "\\1@\u200b\\2", data["answer"])
    body = f"{head}\n\n{answer}"
    if sources:
        body += "\n\n**From:** " + " · ".join(sources)
    return body + footer, "completed"


def main() -> int:
    number = os.environ["NUMBER"]
    question = question_from(os.environ.get("TITLE", ""))
    if question is None:  # the workflow's filter is looser ("ask…"); anything else is left alone
        print("not an ask issue: left alone")
        return 0
    text, close = reply(question)
    if close == "completed" and note_from(os.environ.get("BODY", "")):
        # The form promises a person reads the note, so the issue stays open for one.
        text += "\n\nYou added a note as well, so I'll read it and reply to that part myself."
        close = None
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
