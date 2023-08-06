#! /usr/bin/env python
#
# Copyright (C) 2012 Michael Waskom <mwaskom@stanford.edu>

descr = """Seaborn: improved statistical visualization using Matplotlib"""

import os


DISTNAME = 'seaborn'
DESCRIPTION = descr
MAINTAINER = 'Michael Waskom'
MAINTAINER_EMAIL = 'mwaskom@stanford.edu'
URL = 'https://github.com/mwaskom/seaborn'
LICENSE = 'BSD (3-clause)'
DOWNLOAD_URL = 'https://github.com/mwaskom/seaborn'
VERSION = '0.1'

from numpy.distutils.core import setup


if __name__ == "__main__":
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

    setup(name=DISTNAME,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        description=DESCRIPTION,
        license=LICENSE,
        url=URL,
        version=VERSION,
        download_url=DOWNLOAD_URL,
        packages=['seaborn', 'seaborn.tests'],
        classifiers=['Intended Audience :: Science/Research',
                     'Programming Language :: Python',
                     'License :: OSI Approved',
                     'Topic :: Scientific/Engineering',           
                     'Operating System :: POSIX',
                     'Operating System :: Unix',
                     'Operating System :: MacOS']
        
          )
