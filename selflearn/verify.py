"""
Human verification of the learned store.

  python -m selflearn.verify list                     unverified records (add --all for every record)
  python -m selflearn.verify verify ID --by NAME --how "how it was checked"
  python -m selflearn.verify reject ID --by NAME --how "why it was rejected"

The store path is selflearn/store/learned.jsonl, or SELFLEARN_STORE if set.
"""

import argparse
import sys

from .schema import known
from .store import Store


def main(argv=None):
    ap = argparse.ArgumentParser(prog='python -m selflearn.verify')
    sub = ap.add_subparsers(dest='cmd', required=True)
    ls = sub.add_parser('list')
    ls.add_argument('--all', action='store_true')
    for name in ('verify', 'reject'):
        p = sub.add_parser(name)
        p.add_argument('id')
        p.add_argument('--by', required=True)
        p.add_argument('--how', required=True)
    a = ap.parse_args(argv)
    st = Store()
    if a.cmd == 'list':
        recs = [r for r in st.records() if a.all or r['status'] == 'unverified']
        print(f'{len(recs)} record(s) in {st.path}' + ('' if a.all else ' with status unverified'))
        for r in recs:
            print(f"- {r['id']} [{r['status']}] {r['created']} best: {r['suggested_best']['family_name']} "
                  f"({r['suggested_best']['family_id']}); features {known(r['profile'])}; "
                  f"query: {r['query_text'] if r['consent'] else '(not kept, no consent)'}")
        return 0
    rec = st.set_status(a.id, 'verified' if a.cmd == 'verify' else 'rejected', a.by, a.how)
    print(f"{rec['id']} -> {rec['status']} by {rec['verified_by']} at {rec['verified_at']}: {rec['verified_how']}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
