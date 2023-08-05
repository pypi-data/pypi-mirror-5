from vcs import *

from pyg.log import logger


def vcs(url, dest=None):
    schemes = ('git+', 'hg+', 'bzr+', 'svn+', 'dir+')
    for scheme in schemes:
        if url.startswith(scheme):
           break
    else:
        logger.fatal('Error: URL should start with one of these schemes:\n{0}', schemes, exc=ValueError)
    if not '#egg=' in url:
        logger.fatal('Error: URL should contain `#egg=PACKAGE`', exc=ValueError)

    MAP = {
        'git': Git,
        'hg': Hg,
        'bzr': Bzr,
        'svn': Svn,
        'dir': Local,
    }

    return MAP[scheme[:-1]](url, dest)