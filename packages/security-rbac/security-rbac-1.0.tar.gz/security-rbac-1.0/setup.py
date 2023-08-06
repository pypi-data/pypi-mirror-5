
'''
Created on Oct 1, 2013
 
@package: distribution_manager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Cristian Domsa
 
Setup configuration for components/plugins needed for pypi.
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(packages=find_packages('.'),
     platforms=['all'],
     zip_safe=True,
     license='GPL v3',
     url='http://www.sourcefabric.org/en/superdesk/', # project home page     description='This plugin handles the support for RBAC security.',
     author='Ioan Pocol',
     install_requires=['security >= 1.0'],
     author_email='ioan.pocol@sourcefabric.org',
     version='1.0',
     keywords=['Ally', 'REST', 'plugin', 'support', 'RBAC'],
     name='security-rbac',

     )