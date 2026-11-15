"""Usage: OPEN_LOG=<log> python app/tools/lfs_proof/log_opens.py app.py [streamlit options]

Run `streamlit run <args>` with a Python audit hook that logs the absolute path of every file opened (event 'open')."""
import os
import sys

_fd = os.open(os.environ['OPEN_LOG'], os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)


def _hook(event, args):
    if event != 'open':
        return
    p = args[0]
    if isinstance(p, int):
        return
    try:
        p = os.path.abspath(os.fsdecode(p))
    except Exception:
        return
    os.write(_fd, (p + '\n').encode('utf-8', 'surrogateescape'))


sys.addaudithook(_hook)
from streamlit.web import cli  # noqa: E402
sys.argv = ['streamlit', 'run'] + sys.argv[1:]
sys.exit(cli.main())
