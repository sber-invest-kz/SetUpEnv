#!/usr/bin/env python3
"""Make authenticated LocalSber Task Tracker requests without printing credentials."""

import argparse
import json
import os
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("method", choices=("GET", "POST"))
    parser.add_argument("path", help="Tracker API path beginning with /")
    parser.add_argument("--file", type=Path)
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    base = os.environ.get("TASK_TRACKER_URL", "").rstrip("/")
    token = os.environ.get("TASK_TRACKER_TOKEN", "")
    owner = os.environ.get("TASK_TRACKER_OWNER", "")
    parsed = urlsplit(base)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username is not None or parsed.query or parsed.fragment:
        parser.error("TASK_TRACKER_URL must be an HTTP(S) base URL without credentials, a query, or a fragment")
    if not args.path.startswith("/") or args.path.startswith("//"):
        parser.error("path must begin with a single /")
    if not token and args.path != "/healthz":
        parser.error("set TASK_TRACKER_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    path = args.path
    data = None

    try:
        if args.file:
            if args.method != "POST" or not path.endswith("/attachments") or not owner:
                parser.error("--file requires a POST to /tasks/{id}/attachments and TASK_TRACKER_OWNER")
            with args.file.open("rb") as handle:
                data = handle.read((10 << 20) + 1)
            if not 0 < len(data) <= 10 << 20:
                parser.error("attachment must be nonempty and no larger than 10 MiB")
            path += "?" + urlencode({"filename": args.file.name, "actor": owner, "note": args.note})
            headers["Content-Type"] = "application/octet-stream"
        elif args.method == "POST":
            data = sys.stdin.buffer.read()
            if not isinstance(json.loads(data), dict):
                parser.error("POST requires a JSON object on stdin")
            headers["Content-Type"] = "application/json"

        request = Request(base + path, data=data, headers=headers, method=args.method)
        with build_opener(NoRedirect()).open(request, timeout=15) as response:
            sys.stdout.buffer.write(response.read())
        return 0
    except HTTPError as error:
        print(f"Task Tracker returned HTTP {error.code}", file=sys.stderr)
        sys.stderr.buffer.write(error.read(65536))
    except (OSError, URLError, ValueError) as error:
        print(f"Task Tracker request failed: {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
