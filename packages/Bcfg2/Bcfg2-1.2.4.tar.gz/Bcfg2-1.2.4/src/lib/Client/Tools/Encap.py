"""Bcfg2 Support for Encap Packages"""

__revision__ = '$Revision$'

import glob
import re
import Bcfg2.Client.Tools

class Encap(Bcfg2.Client.Tools.PkgTool):
    """Support for Encap packages."""
    name = 'Encap'
    __execs__ = ['/usr/local/bin/epkg']
    __handles__ = [('Package', 'encap')]
    __req__ = {'Package': ['version', 'url']}
    pkgtype = 'encap'
    pkgtool = ("/usr/local/bin/epkg -l -f -q %s", ("%s", ["url"]))
    splitter = re.compile('.*/(?P<name>[\w-]+)\-(?P<version>[\w\.+-]+)')

# If you define self.pkgtool and self.pkgname it will [use] the Pkgtool.Install
# method will do the installation stuff for you

    def RefreshPackages(self):
        """Try to find encap packages."""
        self.installed = {}
        for pkg in glob.glob("/usr/local/encap/*"):
            match = self.splitter.match(pkg)
            if match:
                self.installed[match.group('name')] = match.group('version')
            else:
                print("Failed to split name %s" % pkg)
        self.logger.debug("Encap.py: RefreshPackages: self.installed.keys() are:")
        self.logger.debug("%s" % list(self.installed.keys()))

    def VerifyPackage(self, entry, _):
        """Verify Package status for entry."""
        if not entry.get('version'):
            self.logger.info("Insufficient information of Package %s; cannot Verify" % entry.get('name'))
            return False
        cmdrc = self.cmd.run("/usr/local/bin/epkg -q -S -k %s-%s >/dev/null" %
                            (entry.get('name'), entry.get('version')))[0]
        if cmdrc != 0:
            self.logger.debug("Package %s version incorrect" % entry.get('name'))
        else:
            return True
        return False

    # Can use the FindExtraPackages method from Bcfg2.Client.Tools.PkgTool

    def RemovePackages(self, packages):
        """Deal with extra configuration detected."""
        names = " ".join([pkg.get('name') for pkg in packages])
        self.logger.info("Removing packages: %s" % (names))
        self.cmd.run("/usr/local/bin/epkg -l -q -r %s" % (names))
        self.RefreshPackages()
        self.extra = self.FindExtraPackages()
