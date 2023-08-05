import ctypes
from select import select as _select
try:
    import signal
except ImportError:
    signal = None

from pulsar.utils.importer import import_module, module_attribute
from pulsar.utils.pep import iteritems, native_str

__all__ = ['ALL_SIGNALS',
           'SIG_NAMES',
           'SKIP_SIGNALS',
           'MAXFD',
           'set_proctitle',
           'set_owner_process',
           'IObase',
           'EpollInterface',
           'IOselect']


SIG_NAMES = {}
MAXFD = 1024
SKIP_SIGNALS = frozenset(('KILL', 'STOP', 'WINCH'))

def all_signals():
    if signal:
        for sig in dir(signal):
            if sig.startswith('SIG') and sig[3] != "_":
                val = getattr(signal, sig)
                if isinstance(val, int):
                    name = sig[3:]
                    if name not in SKIP_SIGNALS:
                        SIG_NAMES[val] = name
                        yield name

            
ALL_SIGNALS = tuple(all_signals())


try:
    from setproctitle import setproctitle
    def set_proctitle(title):
        setproctitle(title)
        return True 
except ImportError: #pragma    nocover
    def set_proctitle(title):
        return


def set_owner_process(uid,gid):
    """ set user and group of workers processes """
    if gid:
        try:
            os.setgid(gid)
        except OverflowError:
            # versions of python < 2.6.2 don't manage unsigned int for
            # groups like on osx or fedora
            os.setgid(-ctypes.c_int(-gid).value)
            
    if uid:
        os.setuid(uid)
    

class IObase(object):
    # Constants from the epoll module
    _EPOLLIN = 0x001
    _EPOLLPRI = 0x002
    _EPOLLOUT = 0x004
    _EPOLLERR = 0x008
    _EPOLLHUP = 0x010
    _EPOLLRDHUP = 0x2000
    _EPOLLONESHOT = (1 << 30)
    _EPOLLET = (1 << 31)

    # Our events map exactly to the epoll events
    NONE = 0
    READ = _EPOLLIN
    WRITE = _EPOLLOUT
    ERROR = _EPOLLERR | _EPOLLHUP | _EPOLLRDHUP
        
    
class EpollInterface(object):
    
    def close(self):
        raise NotImplementedError
    
    def fileno(self):
        raise NotImplementedError
    
    def fromfd(self, fd):
        raise NotImplementedError
    
    def register(self, fd, events):
        raise NotImplementedError
    
    def modify(self, fd, events):
        raise NotImplementedError
    
    def unregister(self, fd):
        raise NotImplementedError
    
    def poll(self, timeout=-1):
        raise NotImplementedError
        
        
class IOselect(EpollInterface):
    '''An epoll like select class.'''
    def __init__(self):
        self.read_fds = set()
        self.write_fds = set()
        self.error_fds = set()
        self.fd_dict = (self.read_fds, self.write_fds, self.error_fds)

    def fileno(self):
        return None
    
    def register(self, fd, events):
        if events & IObase.READ:
            self.read_fds.add(fd)
        if events & IObase.WRITE:
            self.write_fds.add(fd)
        if events & IObase.ERROR:
            self.error_fds.add(fd)
            # Closed connections are reported as errors by epoll and kqueue,
            # but as zero-byte reads by select, so when errors are requested
            # we need to listen for both read and error.
            self.read_fds.add(fd)
                
    def modify(self, fd, events):
        self.unregister(fd)
        self.register(fd, events)

    def unregister(self, fd):
        self.read_fds.discard(fd)
        self.write_fds.discard(fd)
        self.error_fds.discard(fd)
            
    def poll(self, timeout=None):
        readable, writeable, errors = _select(
            self.read_fds, self.write_fds, self.error_fds, timeout)
        return self.get_events(readable, writeable, errors)
    
    def get_events(self, readable, writeable, errors):
        events = {}
        for fd in readable:
            events[fd] = events.get(fd, 0) | IObase.READ
        for fd in writeable:
            events[fd] = events.get(fd, 0) | IObase.WRITE
        for fd in errors:
            events[fd] = events.get(fd, 0) | IObase.ERROR
        return list(iteritems(events))
    

Epoll = IOselect
