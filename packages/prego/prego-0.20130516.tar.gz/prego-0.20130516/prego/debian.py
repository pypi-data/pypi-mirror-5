# -*- coding:utf-8; tab-width:4; mode:python -*-
'''
Debian related assertion
'''

from StringIO import StringIO

from commodity.type_ import checked_type
from commodity.os_ import SubProcess
from commodity.str_ import Printable

from .assertion import Matcher


class Package(Printable):
    def __init__(self, name):
        self.name = checked_type(str, name)

    def __unicode__(self):
        return unicode(self.name)


class DebPackageInstalled(Matcher):
    def __init__(self, min_version):
        self.version = min_version
        super(DebPackageInstalled, self).__init__()

    def _matches(self, package):
        self.package = package

        out = StringIO()
        sp = SubProcess('dpkg -l %s | grep ^ii' % self.package.name,
                        stdout=out, shell=True)
        retval = not sp.wait()

        if retval and self.version is not None:
            installed = out.getvalue().split()[2].strip()
            retval &= installed >= self.version

#            Log.debug("%s: pkg:%s inst:%s req:%s" %
#                      (self.__class__.__name__, self.package,
#                       installed, self.version))

        return retval

    def describe_to(self, description):
        description.append_text('package is installed')


def installed(min_version=None):
    return DebPackageInstalled(min_version)
