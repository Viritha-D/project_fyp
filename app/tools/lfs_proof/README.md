# Proof that the app does not depend on Git LFS

These three tools reproduce the clean-clone test in `docs/data.md` ("Files the app reads").

| file | role |
|---|---|
| `log_opens.py` | runs `streamlit run …` with a Python audit hook that logs every file opened to `$OPEN_LOG` |
| `drive_app.js` | Playwright driver: loads the page, opens the six gallery examples, and in live mode asks three questions |
| `check_no_lfs_pointers.py` | fails if any file the app opened starts with `version https://git-lfs.github.com/spec` |

```
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/Viritha-D/project_fyp /tmp/clean
cd /tmp/clean && GIT_LFS_SKIP_SMUDGE=1 git checkout claude/magical-pascal-uxsxvk
python3.13 -m venv /tmp/clean_venv && /tmp/clean_venv/bin/pip install -r requirements.txt
mkdir -p /tmp/lfslog
OPEN_LOG=/tmp/lfslog/open_clean.log strace -f -qq -e trace=openat -o /tmp/lfslog/strace_clean.log \
  /tmp/clean_venv/bin/python app/tools/lfs_proof/log_opens.py app.py --server.headless true --server.port 8611 &
node app/tools/lfs_proof/drive_app.js 8611 precomputed      # after the server is up; then stop it
python3 app/tools/lfs_proof/check_no_lfs_pointers.py /tmp/lfslog /tmp/clean
```

Without strace, create an empty `strace_clean.log`. The audit-hook log alone covers every file opened from Python.
