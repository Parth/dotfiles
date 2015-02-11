import sys
from pyasn1.compat.octets import octs2ints
from pyasn1 import error

flagNone     = 0x0000
flagEncoder  = 0x0001
flagDecoder  = 0x0002
flagAll      = 0xffff

flagMap = {
    'encoder': flagEncoder,
    'decoder': flagDecoder,
    'all': flagAll
    }

class Debug:
    defaultPrinter = sys.stderr.write
    def __init__(self, *flags):
        self._flags = flagNone
        self._printer = self.defaultPrinter
        for f in flags:
            if f not in flagMap:
                raise error.PyAsn1Error('bad debug flag %s' % (f,))
            self._flags = self._flags | flagMap[f]
            self('debug category %s enabled' % f)
        
    def __str__(self):
        return 'logger %s, flags %x' % (self._printer, self._flags)
    
    def __call__(self, msg):
        self._printer('DBG: %s\n' % msg)

    def __and__(self, flag):
        return self._flags & flag

    def __rand__(self, flag):
        return flag & self._flags

logger = 0

def setLogger(l):
    global logger
    logger = l

def hexdump(octets):
    return ' '.join(
            [ '%s%.2X' % (n%16 == 0 and ('\n%.5d: ' % n) or '', x) 
              for n,x in zip(range(len(octets)), octs2ints(octets)) ]
        )
