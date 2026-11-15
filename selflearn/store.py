"""
Two-tier learned store: selflearn/store/learned.jsonl (JSON lines; plain git, not Git LFS; outside every frozen path).

Record fields: id, created (UTC ISO), profile (feature profile), shortlist (family ids and names), suggested_best
(family id and name), status unverified | verified | rejected, verified_by, verified_at, verified_how, consent
(whether the query text may be kept) and query_text (only when consent is True, otherwise null), key (duplicate key).

Rules:
- New records are always added as "unverified"; only `python -m selflearn.verify` changes the status.
- Duplicates are not added: the key is the sha256 of the known features (canonical JSON) plus the suggested family.
- A rejected suggestion is not repeated: rejected_for(profile) returns the families rejected for similar profiles, and
  the module removes them before suggesting.
- A later similar query may see earlier suggestions (candidates_for), each labelled with its status.
- Unverified records never count as evidence: evidence_count counts verified records only, and the confidence
  trigger (selflearn.trigger) never reads the store at all.
- read_only=True (hosted/cloud mode, where the file system is not durable): add/set_status refuse to write.

"Similar" (fixed a priori): the two profiles share at least 2 known comparable features and disagree on none of them.
"""

import hashlib
import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .schema import known

DEFAULT_PATH = Path(__file__).resolve().parent / 'store' / 'learned.jsonl'
STATUSES = ('unverified', 'verified', 'rejected')


def _comparable(profile):
    k = known(profile)
    k.pop('n_objectives', None)
    return k


def profile_key(profile, best_id):
    canon = json.dumps({'features': _comparable(profile), 'best': best_id}, sort_keys=True)
    return hashlib.sha256(canon.encode('utf-8')).hexdigest()


def similar(p1, p2):
    a, b = _comparable(p1), _comparable(p2)
    shared = set(a) & set(b)
    return len(shared) >= 2 and all(a[k] == b[k] for k in shared)


class ReadOnlyStore(RuntimeError):
    pass


class Store:
    def __init__(self, path=None, read_only=False):
        self.path = Path(path or os.environ.get('SELFLEARN_STORE') or DEFAULT_PATH)
        self.read_only = read_only

    # ---- reading
    def records(self):
        if not self.path.exists():
            return []
        return [json.loads(l) for l in self.path.read_text(encoding='utf-8').splitlines() if l.strip()]

    def get(self, rid):
        return next((r for r in self.records() if r['id'] == rid), None)

    def rejected_for(self, profile):
        return {r['suggested_best']['family_id'] for r in self.records()
                if r['status'] == 'rejected' and similar(r['profile'], profile)}

    def candidates_for(self, profile):
        """Earlier suggestions for similar profiles that were not rejected, each with its status label."""
        out, seen = [], set()
        for r in self.records():
            b = r['suggested_best']['family_id']
            if r['status'] != 'rejected' and similar(r['profile'], profile) and b not in seen:
                seen.add(b)
                out.append({'family_id': b, 'family_name': r['suggested_best']['family_name'], 'status': r['status'],
                            'record_id': r['id']})
        return out

    def evidence_count(self, profile):
        """Verified records for similar profiles. Unverified records never count."""
        return sum(1 for r in self.records() if r['status'] == 'verified' and similar(r['profile'], profile))

    # ---- writing
    def _write_all(self, recs):
        if self.read_only:
            raise ReadOnlyStore('the store is read-only here (the hosted file system is not durable)')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, suffix='.tmp')
        with os.fdopen(fd, 'w', encoding='utf-8') as fh:
            for r in recs:
                fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n')
        os.replace(tmp, self.path)

    def add(self, profile, shortlist, best, query_text=None, consent=False):
        """Add an unverified record. Returns (record, None) or (None, reason) when not added."""
        if self.read_only:
            return None, 'read-only store'
        key = profile_key(profile, best['family_id'])
        recs = self.records()
        if any(r['key'] == key for r in recs):
            return None, 'duplicate'
        if best['family_id'] in self.rejected_for(profile):
            return None, 'suggestion was rejected for a similar profile'
        rec = {'id': uuid.uuid4().hex[:12], 'created': datetime.now(timezone.utc).isoformat(timespec='seconds'),
               'key': key, 'profile': profile,
               'shortlist': [{'family_id': s['family_id'], 'family_name': s['family_name']} for s in shortlist],
               'suggested_best': {'family_id': best['family_id'], 'family_name': best['family_name']},
               'status': 'unverified', 'verified_by': None, 'verified_at': None, 'verified_how': None,
               'consent': bool(consent), 'query_text': query_text if consent else None}
        self._write_all(recs + [rec])
        return rec, None

    def set_status(self, rid, status, by, how):
        if status not in ('verified', 'rejected'):
            raise ValueError('status must be verified or rejected')
        if not by or not how:
            raise ValueError('who verified (--by) and how (--how) are required')
        recs = self.records()
        hit = [r for r in recs if r['id'] == rid]
        if not hit:
            raise KeyError(rid)
        hit[0].update(status=status, verified_by=by, verified_how=how,
                      verified_at=datetime.now(timezone.utc).isoformat(timespec='seconds'))
        self._write_all(recs)
        return hit[0]
