from schroot.utils import run_command
from schroot.core import log
from schroot.errors import SchrootError

from contextlib import contextmanager
import configparser
import shutil
import os


class SchrootCommandError(SchrootError):
    pass


SCHROOT_BASE = "/var/lib/schroot"


class SchrootChroot(object):
    __slots__ = ('session', 'active')

    def __init__(self):
        self.session = None
        self.active = False

    def _safe_run(self, cmd):
        # log.debug("Command: %s" % (" ".join(cmd)))
        out, err, ret = run_command(cmd)
        if ret != 0:
            raise SchrootCommandError()
        return out, err, ret

    @property
    def location(self):
        obj = self.get_session_config()
        return obj['mount-location']

    def copy(self, what, whence, user=None):
        o, e, r = self.run(["mktemp", "-d"],
                           return_codes=0)  # Don't pass user.
        # it'll set the perms wonky.
        where = o.strip()
        what = os.path.abspath(what)
        fname = os.path.basename(what)
        internal = os.path.join(where, fname)
        l = self.location
        l = l if not l.endswith("/") else l[:-1]
        pth = "%s/%s" % (l, internal)
        shutil.copy(what, pth)
        self.run(['mv', internal, whence], user=user, return_codes=0)
        self.run(['rm', '-rf', where], user=user, return_codes=0)

    def get_session_config(self):
        cfg = configparser.ConfigParser()
        fil = os.path.join(SCHROOT_BASE, 'session', self.session)
        if cfg.read(fil) == []:
            raise SchrootError("SANITY FAILURE")
        return cfg[self.session]

    def start(self, chroot_name):
        out, err, ret = self._safe_run(['schroot', '-b', '-c', chroot_name])
        self.session = out.strip()
        self.active = True
        log.debug("new session: %s" % (self.session))

    def end(self):
        out, err, ret = self._safe_run(['schroot', '-e', '-c', self.session])

    def run(self, cmd, user=None, return_codes=None):
        if not isinstance(cmd, list):
            cmd = [cmd]

        if return_codes is not None:
            if not isinstance(return_codes, tuple):
                return_codes = (return_codes, )

        command = ['schroot', '-r', '-c', self.session]
        if user:
            command += ['-u', user]
        command += ['--'] + cmd
        log.debug(" ".join((str(x) for x in command)))
        out, err, ret = run_command(command)

        if ret not in return_codes:
            raise SchrootCommandError("Bad return code")

        return out, err, ret

    def __lt__(self, other):
        return self.run(other, return_codes=0)

    def __floordiv__(self, other):
        return UserProxy(other, self)


class UserProxy(SchrootChroot):
    __slots__ = ('user')

    def __init__(self, user, other):
        super(UserProxy, self).__init__()
        self.user = user
        for entry in other.__slots__:
            setattr(self, entry, getattr(other, entry))

    def run(self, cmd, return_codes=None):
        return super(UserProxy, self).run(cmd, user=self.user,
                                          return_codes=return_codes)


@contextmanager
def schroot(name):
    ch = SchrootChroot()
    try:
        ch.start(name)
        yield ch
    finally:
        ch.end()
