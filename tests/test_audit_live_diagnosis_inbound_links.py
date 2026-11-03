"""Offline tests for read-only live inbound-link sampler."""
import importlib.util
from pathlib import Path
import unittest
from email.message import Message
from urllib.error import HTTPError

FILE = Path(__file__).resolve().parents[1] / 'tools' / 'audit_live_diagnosis_inbound_links.py'
spec = importlib.util.spec_from_file_location('sampler', FILE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class FakeResponse:
    status = 200
    def __init__(self, body, code=200):
        self.body = body
        self.status = code
        self.headers = Message()
        self.headers['ETag'] = '"test"'
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self, limit): return self.body[:limit]
    def getcode(self): return self.status


class FakeOpener:
    def __init__(self, responses): self.responses = responses; self.requests = []
    def open(self, req, timeout):
        self.requests.append((req.full_url, req.get_method(), timeout))
        result = self.responses[req.full_url]
        if isinstance(result, Exception): raise result
        return result


class TestSampler(unittest.TestCase):
    def test_resolves_relative_links_and_ignores_external_or_other_targets(self):
        url = m.SITE + '/residential/'
        data = b'''<a href="../shindan.html">old</a><A HREF="/photo-diagnosis/?campaign=1">new</A>
        <a href="https://elsewhere.example/shindan.html">x</a>
        <a href="mailto:a@example.com">mail</a><a href="/shindan.htmlish">x</a>'''
        result = m.inspect(FakeOpener({url: FakeResponse(data)}), '/residential/')
        self.assertEqual(result['tracked_anchor_counts'], {'/shindan.html': 1, '/photo-diagnosis/': 1})
        self.assertEqual(result['total_anchors'], 5)

    def test_no_redirect_follow_and_no_false_counts(self):
        url = m.SITE + '/faq.html'
        exc = HTTPError(url, 301, 'Moved', Message(), None)
        opener = FakeOpener({url: exc})
        result = m.inspect(opener, '/faq.html')
        self.assertEqual(result['http_status'], 301)
        self.assertNotIn('tracked_anchor_counts', result)
        self.assertEqual(opener.requests, [(url, 'GET', 10)])

    def test_exact_fixed_scope_and_totals(self):
        responses = {m.SITE+p: FakeResponse(b'<a href="/shindan.html">old</a>') for p in m.PATHS}
        opener = FakeOpener(responses)
        result = m.collect(opener)
        self.assertTrue(result['complete'])
        self.assertEqual(result['anchor_totals']['/shindan.html'], 5)
        self.assertEqual(result['anchor_totals']['/photo-diagnosis/'], 0)
        self.assertEqual(len(opener.requests), 5)

    def test_missing_page_marks_sample_incomplete(self):
        responses = {m.SITE+p: FakeResponse(b'<p>empty</p>') for p in m.PATHS}
        responses[m.SITE+'/contact.html'] = FakeResponse(b'', code=404)
        result = m.collect(FakeOpener(responses))
        self.assertFalse(result['complete'])
        self.assertEqual(result['anchor_totals']['/shindan.html'], 0)

    def test_maximum_bytes_is_enforced(self):
        url = m.SITE+'/contact.html'
        result = m.inspect(FakeOpener({url: FakeResponse(b'X' * (m.MAX_BYTES + 10))}), '/contact.html')
        self.assertEqual(result['error'], 'HTML_EXCEEDS_READ_CAP')
        self.assertNotIn('tracked_anchor_counts', result)


if __name__ == '__main__': unittest.main()
