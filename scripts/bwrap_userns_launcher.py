#!/usr/bin/python3
"""Opt-in sudo bootstrap for Bubblewrap on Ubuntu's restricted userns hosts.

The privileged parent only maps a fresh user namespace to SUDO_UID/SUDO_GID.
The child has capabilities only inside that namespace; Bubblewrap maps the
final process to the invoking user ID and drops all capabilities. No host policy, filesystem permission, or network setting is modified.
"""
import ctypes
import os
from pathlib import Path
import signal
import sys


def main():
    args = sys.argv[1:]
    required = {'--unshare-all', '--unshare-user', '--unshare-net', '--clearenv',
                '--die-with-parent', '--new-session', '--disable-userns'}
    if not required.issubset(args) or not any(args[i:i+2] == ['--cap-drop', 'ALL'] for i in range(len(args))):
        raise SystemExit('Use only as the PersonaScienceBench isolated sandbox launcher.')
    if any(x in args for x in ('--share-net', '--share-user', '--uid', '--gid', '--cap-add', '--userns')):
        raise SystemExit('Refusing namespace or identity overrides.')
    if os.getuid() != 0:
        os.execv('/usr/bin/sudo', ['sudo', '-n', '/usr/bin/python3', '-I', str(Path(__file__).resolve()), *args])
    uid, gid = int(os.environ.get('SUDO_UID', '0')), int(os.environ.get('SUDO_GID', '0'))
    if not uid or not gid:
        raise SystemExit('Must be invoked through sudo by a non-root user.')
    ready_r, ready_w = os.pipe()
    mapped_r, mapped_w = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(ready_r)
        os.close(mapped_w)
        libc = ctypes.CDLL(None, use_errno=True)
        if libc.unshare(0x10000000):  # CLONE_NEWUSER; all other isolation remains Bubblewrap's job.
            os._exit(125)
        os.write(ready_w, b'1')
        os.close(ready_w)
        if os.read(mapped_r, 1) != b'1':
            os._exit(125)
        os.close(mapped_r)
        os.setresgid(0, 0, 0)
        os.setresuid(0, 0, 0)
        os.execve('/usr/bin/bwrap', ['bwrap', '--uid', str(uid), '--gid', str(gid), *args], {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'})
    os.close(ready_w)
    os.close(mapped_r)
    try:
        if os.read(ready_r, 1) != b'1':
            raise RuntimeError('Could not create the bootstrap user namespace')
        ns = Path('/proc') / str(pid)
        (ns / 'uid_map').write_text(f'0 {uid} 1\n')
        (ns / 'setgroups').write_text('deny\n')
        (ns / 'gid_map').write_text(f'0 {gid} 1\n')
        os.write(mapped_w, b'1')
    except BaseException:
        os.kill(pid, signal.SIGKILL)
        os.waitpid(pid, 0)
        raise
    finally:
        os.close(ready_r)
        os.close(mapped_w)
    _, status = os.waitpid(pid, 0)
    return os.waitstatus_to_exitcode(status)


if __name__ == '__main__':
    raise SystemExit(main())
