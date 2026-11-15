"""
Usage: python app/tools/lfs_proof/check_no_lfs_pointers.py <log_dir> <clone_dir>

Reads <log_dir>/open_clean.log (from log_opens.py) and <log_dir>/strace_clean.log (strace -e openat; may be empty),
and fails if any regular file the app opened starts with the Git LFS pointer header.
"""
import os, re, sys
L, repo = sys.argv[1], os.path.realpath(sys.argv[2])
paths = {l.strip() for l in open(f'{L}/open_clean.log') if l.strip()}
for l in open(f'{L}/strace_clean.log'):
    m = re.search(r'openat\([^,]+, "([^"]+)", [^)]*\) = \d+', l)
    if m: paths.add(os.path.join(repo, m.group(1)) if not m.group(1).startswith('/') else m.group(1))
files = sorted({os.path.realpath(p) for p in paths if os.path.isfile(p)})
PREFIX = b'version https://git-lfs.github.com/spec'
bad = [p for p in files if open(p, 'rb').read(len(PREFIX)) == PREFIX]
inrepo = [p for p in files if p.startswith(repo + os.sep)]
print(f'files the app opened (regular files, hook + strace): {len(files)}; inside the clone: {len(inrepo)}')
for p in inrepo: print('  ', os.path.relpath(p, repo), os.path.getsize(p), 'bytes')
print(f'files starting with "version https://git-lfs.github.com/spec": {len(bad)}', bad)
assert not bad, 'LFS pointer opened'
print('ASSERTION PASSED: no file the app opened is a Git LFS pointer')
