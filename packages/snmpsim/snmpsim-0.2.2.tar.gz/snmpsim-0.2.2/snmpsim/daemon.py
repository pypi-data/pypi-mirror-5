# UNIX-specific process daemonization tools
import sys
from snmpsim import log, error

if sys.platform[:3] == 'win':
    def daemonize(pidfile):
        raise error.SnmpsimError('Windows is not inhabited with daemons!')
    def dropPrivileges(uname, gname):
        return
else:
    import os, pwd, grp, atexit, signal, tempfile

    def daemonize(pidfile):
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit first parent
                os._exit(0) 
        except OSError:
            raise error.SnmpsimError('ERROR: fork #1 failed: %s' % sys.exc_info()[1])
            
        # decouple from parent environment
        os.chdir('/') 
        os.setsid() 
        os.umask(0) 
            
        # do second fork
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit from second parent
                os._exit(0) 
        except OSError:
            raise error.SnmpsimError('ERROR: fork #2 failed: %s' % sys.exc_info()[1])

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
          
        def cb(s,f):
            raise KeyboardInterrupt
        for s in signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT:
            signal.signal(s, cb)
             
        # write pidfile
        atexit.register(lambda pidfile=pidfile: os.remove(pidfile))

        try:
            fd, nm = tempfile.mkstemp()
            os.write(fd, '%d\n' % os.getpid())
            os.close(fd)
            os.rename(nm, pidfile)
        except:
            raise error.SnmpsimError('Failed to create PID file %s: %s' % (pidfile, sys.exc_info()[1]))

    def dropPrivileges(uname, gname):
        if os.getuid() != 0:
            if uname and uname != pwd.getpwnam(uname).pw_name or \
                    gname and gname != grp.getgrnam(gname).gr_name:
                raise error.SnmpsimError('Process is running under different UID/GID')
            else:
                return
        else:
            if not uname or not gname:
                raise error.SnmpsimError('Must drop priveleges to a non-priveleged user&group')

        try:
            runningUid = pwd.getpwnam(uname).pw_uid
            runningGid = grp.getgrnam(gname).gr_gid
        except Exception:
            raise error.SnmpsimError('getpwnam()/getgrnam() failed for %s/%s: %s' % (uname, gname, sys.exc_info()[1]))

        try:
            os.setgroups([])
        except Exception:
            raise error.SnmpsimError('setgroups() failed: %s' % sys.exc_info()[1])

        try:
            os.setgid(runningGid)
            os.setuid(runningUid)
        except Exception:
            raise error.SnmpsimError('setgid()/setuid() failed for %s/%s: %s' % (runningGid, runningUid, sys.exc_info()[1]))

        os.umask(511)
