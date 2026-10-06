#!/usr/bin/env python3
"""Local preview for _drafts/*.md (and _posts/*.md), styled like the minima theme.

    python3 _preview/preview.py            # then open http://localhost:4000

No dependencies. Markdown is rendered in the browser with markdown-it, Liquid
`{{ site.* }}` tags are filled from _config.yml, Obsidian `![[image.png]]`
embeds are resolved, and the page reloads whenever the file is saved.
This folder starts with "_" so Jekyll/GitHub Pages ignores it.
"""
import html
import json
import mimetypes
import re
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
SOURCES = {"drafts": ROOT / "_drafts", "posts": ROOT / "_posts"}


def load_config():
    cfg = {}
    for line in (ROOT / "_config.yml").read_text().splitlines():
        m = re.match(r'^(\w+):\s*"?([^"#]*?)"?\s*(#.*)?$', line)
        if m:
            cfg[m.group(1)] = m.group(2)
    return cfg


def split_front_matter(text):
    meta = {}
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return meta, text
    for line in m.group(1).splitlines():
        kv = re.match(r'^(\w+):\s*"?(.*?)"?\s*$', line)
        if kv:
            meta[kv.group(1)] = kv.group(2)
    return meta, text[m.end():]


def find_embed(name, folder):
    for cand in (folder / name, folder / "images" / name, ROOT / "assets" / name):
        if cand.is_file():
            return "/" + cand.relative_to(ROOT).as_posix()
    hits = list(folder.rglob(name)) or list((ROOT / "assets").rglob(name))
    return "/" + hits[0].relative_to(ROOT).as_posix() if hits else name


def preprocess(body, folder, cfg):
    # Liquid: {{ site.x }} -> value from _config.yml ({{ site.baseurl }} -> "" locally)
    body = re.sub(r"\{\{\s*site\.(\w+)\s*\}\}",
                  lambda m: "" if m.group(1) == "baseurl" else cfg.get(m.group(1), ""), body)
    body = re.sub(r"\{%.*?%\}", "", body)
    # Obsidian embeds: ![[file.png]] / ![[file.png|alt]]
    body = re.sub(r"!\[\[([^\]|]+)(?:\|([^\]]*))?\]\]",
                  lambda m: f"![{m.group(2) or m.group(1)}]({quote(find_embed(m.group(1).strip(), folder))})",
                  body)
    return body


def list_files():
    out = []
    for kind, folder in SOURCES.items():
        for p in sorted(folder.glob("*.md")):
            meta, _ = split_front_matter(p.read_text(encoding="utf-8"))
            out.append((kind, p.name, meta.get("title", p.stem)))
    return out


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def log_message(self, *a):
        pass

    def send(self, body, ctype="text/html; charset=utf-8", code=200):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def resolve(self, kind, name):
        folder = SOURCES.get(kind)
        if not folder:
            return None
        path = (folder / unquote(name)).resolve()
        if path.parent != folder.resolve() or not path.is_file():
            return None
        return path

    def do_GET(self):
        url = urlparse(self.path)
        parts = [p for p in url.path.split("/") if p]
        tpl = (HERE / "template.html").read_text()
        cfg = load_config()

        if not parts:
            items = "".join(
                f'<li><span class="post-meta">{kind[:-1]}</span>'
                f'<h3><a class="post-link" href="/{kind}/{quote(name)}">{html.escape(title)}</a></h3></li>'
                for kind, name, title in list_files())
            page = f'<h2 class="post-list-heading">Drafts &amp; posts</h2><ul class="post-list">{items}</ul>'
            return self.send(tpl.replace("__SITE_TITLE__", html.escape(cfg.get("title", "")))
                                .replace("__CONTENT__", page).replace("__DATA__", "null"))

        if len(parts) == 2 and parts[0] in SOURCES:
            path = self.resolve(parts[0], parts[1])
            if not path:
                return self.send("Not found", "text/plain", 404)
            if "mtime" in parse_qs(url.query):
                return self.send(str(path.stat().st_mtime_ns), "text/plain")
            meta, body = split_front_matter(path.read_text(encoding="utf-8"))
            date = meta.get("date") or (path.name[:10] if re.match(r"\d{4}-\d{2}-\d{2}", path.name) else "")
            data = {
                "title": meta.get("title", path.stem),
                "date": date,
                "kind": parts[0],
                "markdown": preprocess(body, path.parent, cfg),
                "mtimeUrl": f"/{parts[0]}/{quote(path.name)}?mtime=1",
                "mtime": str(path.stat().st_mtime_ns),
            }
            blob = json.dumps(data).replace("</", "<\\/")
            return self.send(tpl.replace("__SITE_TITLE__", html.escape(cfg.get("title", "")))
                                .replace("__CONTENT__", "").replace("__DATA__", blob))

        # Everything else (assets/, _drafts/images/, iframes…) is served from the repo root.
        return super().do_GET()


mimetypes.add_type("text/html", ".html")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Previewing drafts at http://localhost:{port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
