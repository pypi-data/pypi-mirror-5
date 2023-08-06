
The ``rmoldkernels`` utility removes old. no longer used, kernels
from on Ubuntu systems, thus freeing up space on ``/boot`` (or ``/``).

The currently active kernel is kept, as is the last one installed
(numeric wise), normally that would be the one that becomes active on
a reboot. Any 'older' or intermediate kernels (those that got installed after
a reboot except for the last one) will be deleted.

If ran as normal user, you will be asked for a ``sudo`` password.

The commandline handed to ``apt-get`` for removal is echoed, and you
do have to confirm the removal. 

You can specify a number of extra kernels to keep, these are counted
from the last and do include the last one if that is not the active one.

It probably works on Debian as well, but that has not been tested as
of Nov. 2013.

Report bugs at https://bitbucket.org/ruamel/rmoldkernels/issues

and checkout repositories at https://bitbucket.org/ruamel/rmoldkernels
