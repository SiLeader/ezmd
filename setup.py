"""
    Copyright 2018 SiLeader and Cerussite.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from setuptools import setup, find_packages


try:
    with open('README.md') as f:
        readme = f.read()
except IOError:
    readme = ''


def _requires_from_file(filename):
    return open(filename).read().splitlines()


setup(
    name='ezmd',
    version='1.0.0',
    packages=find_packages(),
    install_requires=_requires_from_file("requirements.txt"),
    url='https://github.com/SiLeader/ezmd',
    license='Apache 2.0',
    author='SiLeader',
    author_email='sileader.dev@gmail.com',
    maintainer='SiLeader',
    maintainer_email='sileader.dev@gmail.com',
    description='Useful and easy markdown formatter and converter',
    long_description=readme,
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: Apache Software License',
    ],
    py_modules=["ezmd"]
)
