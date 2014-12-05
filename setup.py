# VMware vCloud CLI
# Copyright (c) 2014 VMware, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup


setup(
    name='vca-cli',
    version='0.0.1',
    description='VMware vCloud CLI',
    url='https://github.com/vmware/vca-cli',
    author='VMware, Inc.',
    author_email='pgomez@vmware.com',
    packages=['vca_cli'],
    install_requires=[
        'Click',
        # Colorama is only required for Windows.
        'colorama',
        'pyvcloud'
    ],
    license='License :: OSI Approved :: Apache Software License',
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',      
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
    ],
    keywords='pyvcloud vcloud vcloudair vmware cli',
    platforms=['Windows', 'Linux', 'Solaris', 'Mac OS-X', 'Unix'],
    test_suite='tests',
    tests_require=[],
    zip_safe=True,
    entry_points='''
        [console_scripts]
        vca=vca_cli.vca_cli:cli
    ''',
    
)