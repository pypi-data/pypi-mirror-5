# kippo-extra
Set of extra commands for the kippo SSH honeypot daemon (http://code.google.com/p/kippo/).

## Provided commands
* `/usr/bin/env` - current environment variables
* `/usr/bin/gcc` - fake compiler with file output
* `/sbin/iptables` - fake firewall management, supports flush and list for different tables/chains
* `/bin/which` - path of binary
* `/bin/netstat` - work in progress

The commands are based on the x64 build of Debian 5.

## Installation
Please read the full installation part.

Python 2.7 or later is required (Python 3.x isn't). Note that the minimal version is different from kippo itself.

Install kippo-extra via `pip install kippo-extra`, or clone this repository, `cd` into the newly created directory and run `python setup.py install`. In case one of both ways fail, make sure you have proper permissions. To check if everythin works, you can run `python -c 'import kippo_extra'` which should not produce any errors.

Kippo doesn't come with a plugin system. Therefore, the kippo source should be modified. Open the file `KIPPO_ROOT/kippo/__init__.py`. By default, it is an empty file. Insert the line `from kippo_extra import loader` and save the file.

### Note 1
The commands require you have a fake filesystem ready with fake links to the commands. Therefore, make sure the `/path/to/command` is in your fake filesystem. If a command does not work in a session, try to `touch /path/to/command` and then try again. If it works now, then you do not have the fake links in your fake filesystem.

This issue has been reported. See https://code.google.com/p/kippo/issues/detail?id=59 for more information.

### Note 2
A small portion of the kippo source code is modified at runtime by intercepting imports (See PEP302). However, these patches are dependend on the version of kippo. At this moment, the patches are based on SVN Revision 246. In case a new version is available and kippo fails to start, you can try to manually apply the patches to the kippo source (see the directory `kippo_extra/patches`). Insert `PATCH_SOURCE = False` in `KIPPO_ROOT/kippo/__init__.py` to disable runtime patching.

## Known issues
Probably a lot.

I'm not a Unix guru, so I have no advanced knowledge of all commands and possible options. I have implemented the basic options to make an honeypot session more realistic.

Feel free to fork or submit issues!

## License
See the `LICENSE` file (MIT license).
