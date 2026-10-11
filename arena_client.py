"""Battle Arena client. Handles auth, retries, rate limits and credit accounting.

Keeps one persistent HTTP(S) connection per thread, so a call costs one round trip instead of a
fresh TCP + TLS handshake. Safe to share one Arena object between threads.
"""
import http.client, json, os, threading, time, urllib.parse


class Exhausted(Exception):
    """Out of credits. Final: every metered call will fail from now on."""


class WrongPhase(RuntimeError):
    """The call is not allowed in the current phase (e.g. an offer during recon). HTTP 409."""


class Arena:
    def __init__(self, base=None, key=None, timeout=20):
        self.base = (base or os.environ.get("ARENA_URL", "http://localhost:8000")).rstrip("/")
        self.key = key or os.environ["ARENA_KEY"]
        self.timeout, self.credits_remaining, self.calls = timeout, None, 0
        self.rate_limited = 0                  # how many 429 rate_limited responses we backed off from
        u = urllib.parse.urlsplit(self.base)
        self._https, self._host, self._port, self._prefix = u.scheme == "https", u.hostname, u.port, u.path
        self._local = threading.local()

    def _conn(self):
        c = getattr(self._local, "conn", None)
        if c is None:
            cls = http.client.HTTPSConnection if self._https else http.client.HTTPConnection
            c = self._local.conn = cls(self._host, self._port, timeout=self.timeout)
        return c

    def _drop(self):
        c = getattr(self._local, "conn", None)
        if c is not None:
            c.close()
        self._local.conn = None

    def _call(self, path, method="GET", body=None, tries=6):
        data = json.dumps(body).encode() if body is not None else None
        hdrs = {"X-Arena-Key": self.key, "content-type": "application/json"}
        for attempt in range(tries):
            try:
                c = self._conn()
                c.request(method, self._prefix + path, body=data, headers=hdrs)
                r = c.getresponse()
                raw = r.read()
            except (http.client.HTTPException, OSError):
                self._drop()                           # network trouble or a closed idle connection
                time.sleep(0.5 * attempt)              # retry at once the first time, then back off
                continue
            cr = r.getheader("X-Credits-Remaining")
            if cr is not None: self.credits_remaining = int(cr)
            if r.status < 300:
                self.calls += 1
                return json.loads(raw or b"{}")
            text = raw.decode(errors="replace")[:300]
            if r.status == 429 and "credits_exhausted" in text:
                self.credits_remaining = 0
                raise Exhausted(text)
            if r.status == 429:                        # rate limited: back off and retry
                self.rate_limited += 1
                time.sleep(0.15 * (attempt + 1)); continue
            if r.status in (500, 502, 503, 504):
                time.sleep(0.3 * (attempt + 1)); continue
            if r.status == 409:
                raise WrongPhase(f"409: {text}")
            raise RuntimeError(f"{r.status}: {text}")
        raise RuntimeError(f"gave up on {path}")

    # --- endpoints -------------------------------------------------------
    def requisitions(self):                 return self._call("/requisitions")
    def search(self, q="", role=None, city=None, page=0, size=100):
        p = f"/search?q={urllib.parse.quote(q)}&page={page}&size={size}"
        if role: p += "&role=" + urllib.parse.quote(role)
        if city: p += "&city=" + urllib.parse.quote(city)
        return self._call(p)
    def candidate(self, cid):               return self._call(f"/candidate/{urllib.parse.quote(cid)}")
    def batch(self, ids):                   return self._call("/candidates/batch", "POST", {"ids": list(ids)[:50]})
    def assess(self, cid):                  return self._call(f"/assess/{urllib.parse.quote(cid)}")
    def offer(self, cid, req_id):           return self._call("/offer", "POST", {"candidate_id": cid, "req_id": req_id}, tries=1)
    def release(self, cid):                 return self._call(f"/offer/{urllib.parse.quote(cid)}", "DELETE")
    def market(self):                       return self._call("/market")
    def ledger(self):                       return self._call("/ledger")
    def reason(self, prompt, max_tokens=400):
        return self._call("/reason", "POST", {"prompt": prompt, "max_tokens": max_tokens})
