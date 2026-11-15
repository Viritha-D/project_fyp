"""The root app.py (Streamlit Cloud main file) renders the same precomputed page as app/streamlit_app.py."""
import json

from streamlit.testing.v1 import AppTest

import core

ROOT_APP = str(core.ROOT / 'app.py')


def test_root_entrypoint_renders_gallery(monkeypatch):
    monkeypatch.delenv('DEMO_MODE', raising=False)
    at = AppTest.from_file(ROOT_APP, default_timeout=60)
    at.run()
    assert not at.exception, at.exception
    labels = [e.label for e in at.expander]
    for item in json.loads((core.APP / 'gallery.json').read_text())['items']:
        assert any(l.startswith(item['query_id']) for l in labels)
    assert any('Mode: precomputed' in c.value for c in at.caption)
