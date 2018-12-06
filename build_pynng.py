# build the pynng interface.
#
# This script assumes the nng library has already been built; the setup.py
# script should ensure that it is built before running.  It looks in this file
# to see what the expected object file is based on the platform.
from cffi import FFI
import shutil
import sys

ffibuilder = FFI()

if sys.platform == 'win32':
    if shutil.which('ninja'):
        objects = ['./nng/build/nng.lib']
    else:
        objects = ['./nng/build/Release/nng.lib']
    # libraries determined to be necessary through trial and error
    libraries = ['Ws2_32', 'Advapi32']
else:
    objects = ['./nng/build/libnng.a']
    libraries = ['rt']


ffibuilder.set_source(
    "pynng._nng",
    r""" // passed to the real C compiler,
         // contains implementation of things declared in cdef()
         #define NNG_DECL
         #include <nng/nng.h>
         #include <nng/protocol/bus0/bus.h>
         #include <nng/protocol/pair0/pair.h>
         #include <nng/protocol/pair1/pair.h>
         #include <nng/protocol/pipeline0/pull.h>
         #include <nng/protocol/pipeline0/push.h>
         #include <nng/protocol/pubsub0/pub.h>
         #include <nng/protocol/pubsub0/sub.h>
         #include <nng/protocol/reqrep0/req.h>
         #include <nng/protocol/reqrep0/rep.h>
         #include <nng/protocol/survey0/respond.h>
         #include <nng/protocol/survey0/survey.h>
    """,
    libraries=libraries,
    # library_dirs=['nng/build/Debug',],
    # (more arguments like setup.py's Extension class:
    include_dirs=['nng/include'],
    extra_objects=objects,
)


with open('nng_api.h') as f:
    api = f.read()

rest = """
    extern "Python" void _async_complete(void *);
"""
ffibuilder.cdef(api + rest)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
