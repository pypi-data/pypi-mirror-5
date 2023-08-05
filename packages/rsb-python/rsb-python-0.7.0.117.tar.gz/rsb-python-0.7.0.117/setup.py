# ============================================================
#
# Copyright (C) 2010 by Johannes Wienke <jwienke at techfak dot uni-bielefeld dot de>
#
# This file may be licensed under the terms of the
# GNU Lesser General Public License Version 3 (the ``LGPL''),
# or (at your option) any later version.
#
# Software distributed under the License is distributed
# on an ``AS IS'' basis, WITHOUT WARRANTY OF ANY KIND, either
# express or implied. See the LGPL for the specific language
# governing rights and limitations.
#
# You should have received a copy of the LGPL along with this
# program. If not, go to http://www.gnu.org/licenses/lgpl.html
# or write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# The development of this software was supported by:
#   CoR-Lab, Research Institute for Cognition and Robotics
#     Bielefeld University
#
# ============================================================

from setuptools import setup
from setuptools import find_packages
from setuptools import Command
from setuptools.command.bdist_egg import bdist_egg

from distutils.command.build import build
from distutils.command.sdist import sdist
from distutils.spawn import find_executable

from unittest import TestResult

import os
import setuptools.command.test
import subprocess
import sys
import time
import shutil
import rsb

def findRsbPackages(ignoreProtocol=False):
    excludes = ["test", "examples", "build"]
    if ignoreProtocol:
        excludes.append("rsb/protocol")
    packages = find_packages(exclude=excludes)
    print("Relevant rsb packages: %s" % packages)
    return packages

class CommandStarter(object):

    def __init__(self, command):
        self.__open = subprocess.Popen(command)
        time.sleep(2)

    def __del__(self):
        print("Stopping command %s" % self.__open)
        self.__open.terminate()
        self.__open.wait()

class ApiDocCommand(Command):
    '''
    Distutils command used to build the api documentation with epydoc.

    @author: jwienke
    '''

    user_options = [('format=', 'f',
                     "the output format to use (html and pdf)"),
                     ("verbose", 'v', "print verbose warnings")]
    description = "generates the api documentation as html or pdf"

    FORMAT_HTML = "html"
    FORMAT_PDF = "pdf"

    def initialize_options(self):
        self.format = None
        self.verbose = False

    def finalize_options(self):
        if self.format is None:
            self.format = self.FORMAT_HTML
        if not self.format in [self.FORMAT_HTML, self.FORMAT_PDF]:
            self.format = self.FORMAT_HTML

    def run(self):

        # ensure that everything that's needed is built
        self.run_command('build')

        outdir = os.path.join("docs", self.format)
        try:
            os.makedirs(outdir)
        except OSError:
            pass

        # build the argument string
        cmdline = [sys.executable]
        cmdline.append("-c")
        cmdline.append("from epydoc import cli; cli.cli()")
        cmdline.append("--" + self.format)
        cmdline.append("-o")
        cmdline.append(outdir)
        if self.verbose:
            cmdline.append("-v")
        cmdline.append("--config")
        cmdline.append("epydoc.config")

        # call epydoc according to the selected configuration
        env = os.environ
        ppath = ""
        for p in sys.path:
            ppath += p + os.path.pathsep
        env['PYTHONPATH'] = ppath
        subprocess.call(cmdline, env=env)

class FetchProtocol(Command):
    '''
    A command which fetches the protocol files into this project

    @author: jwienke
    '''

    user_options = [('protocolroot=', 'p',
                     "root path of the protocol")]
    description = "Fetches the protocol files into this project"

    def initialize_options(self):
        self.protocolroot = None

    def finalize_options(self):
        if self.protocolroot == None:
            raise RuntimeError("No protocolroot specified. Use the config file or command line option.")

    def run(self):

        # if it does not exist, create the target directory for the copied files
        fetchedProtocolDir = "rsb/protocol"
        try:
            # in cases of source distributions this would kill also the fetched
            # proto files. However, for a source distribution we will never
            # reach this method because the protocolroot option will not be set
            shutil.rmtree(fetchedProtocolDir)
        except os.error:
            pass

        protoRoot = self.protocolroot
        print("Using protocol folder: %s" % protoRoot)
        shutil.copytree(os.path.join(protoRoot, "rsb/protocol"), fetchedProtocolDir)

class BuildProtocol(Command):
    '''
    Distutils command to build the protocol buffers.

    @author: jwienke
    '''

    user_options = [('protocolroot=', 'p',
                     "root path of the protocol"),
                    ('protoc=', 'c',
                     "the protoc compiler to use")]
    description = "Generates the protocol buffers from the previously protocol definition"

    def initialize_options(self):
        self.protoc = None

    def finalize_options(self):
        if self.protoc == None:
            self.protoc = find_executable("protoc")
        if self.protoc == None:
            raise RuntimeError("No protoc compiler specified or found. Use the config file or command line option.")

    def run(self):

        try:
            self.run_command('proto')
        except RuntimeError, e:
            # for sdist fetching the protocol may fail as long as we have
            # the protocol available. Otherwise this is a real error
            self.warn("Fetching the protocol failed, but this acceptable in cases where the files have been cached: %s" % e)
            if not os.path.exists("rsb/protocol/Notification.proto"):
                raise e

        # create output directory
        outdir = "."
        try:
            os.makedirs(outdir)
        except os.error:
            pass

        protoFiles = []
        for root, dirs, files in os.walk("rsb/protocol"):
            # collect proto files to build
            for file in files:
                if file[-6:] == ".proto":
                    protoFiles.append(os.path.join(root, file))
            # create __init__.py files for all resulting packages
            with open(os.path.join(root, '__init__.py'), 'w'):
                pass

        print("Building protocol files: %s" % protoFiles)
        for proto in protoFiles:
            # TODO use project root for out path as defined in the test command
            call = [self.protoc, "-I=.", "--python_out=" + outdir, proto]
            #print("calling: %s" % call)
            ret = subprocess.call(call)
            if ret != 0:
                raise RuntimeError("Unable to build proto file: %s" % proto)

        # reinitialize the list of packages as we have added new python modules
        self.distribution.packages = findRsbPackages()
        # also ensure that the build command for python module really gets informed about this
        self.reinitialize_command("build_py")

class Coverage(Command):
    """
    A command to generate a coverage report using coverage.py.

    @author: jwienke
    """

    user_options = [('spread=', 'd',
                     "spread executable to use")]
    description = "generates a coverage report"

    def initialize_options(self):
        self.spread = None

    def finalize_options(self):
        if self.spread == None and rsb.haveSpread():
            self.spread = find_executable("spread")
            if self.spread == None:
                print("WARNING: no spread daemon found. Make sure that one is running before starting the coverage report")

    def run(self):

        spread = None
        if self.spread:
            spread = CommandStarter([self.spread, "-n", "localhost", "-c", "test/spread.conf"])

        import coverage
        cov = coverage.coverage(branch=True, source=["rsb"], omit=["*_pb2*"])
        cov.erase()
        cov.start()
        import test
        suite = test.suite()
        results = TestResult()
        suite.run(results)
        if not results.wasSuccessful():
            print("Unit tests failed while generating test report.")
        cov.stop()
        cov.html_report(directory='covhtml')
        cov.xml_report(outfile='coverage.xml')

class BDist_egg(bdist_egg):
    """
    Simple wrapper around the normal bdist_egg command to require protobuf build
    before normal build.

    @author: jwienke
    """

    def run(self):
        self.run_command('build_proto')
        bdist_egg.run(self)

class Build(build):
    """
    Simple wrapper around the normal build command to require protobuf build
    before normal build.

    @author: jwienke
    """

    def run(self):
        self.run_command('build_proto')
        build.run(self)

class Sdist(sdist):
    """
    Simple wrapper around the normal sdist command to require protobuf build
    before generating the source distribution..

    @author: jwienke
    """

    def run(self):
        # fetch the protocol before building the source distribution so that
        # we have a cached version and each user can rebuild the protocol
        # with his own protobuf version
        self.run_command('proto')

        # reinitialize the list of packages for the distribution to include the
        # precompiled protocol results from protoc which might conflict with the
        # user's version
        self.distribution.packages = findRsbPackages(ignoreProtocol=True)

        sdist.run(self)

class Test(setuptools.command.test.test):
    """
    Wrapper for test command to execute build before testing use a custom test
    runner. It also starts a spread daemon.

    @author: jwienke
    """

    user_options = setuptools.command.test.test.user_options \
        + [ ('spread=',     'd',  "Spread executable to use"),
            ('spreadport=', 'p',  "Port the spread daemon should use"),
            ('socketport=', None, 'Port which should be used by socket transport') ]

    def initialize_options(self):
        setuptools.command.test.test.initialize_options(self)
        self.spread = None
        self.spreadport = 4803
        self.socketport = 55555

    def finalize_options(self):
        setuptools.command.test.test.finalize_options(self)
        if self.spread == None and rsb.haveSpread():
            self.spread = find_executable("spread")
            if self.spread == None:
                print("WARNING: no spread daemon found. Make sure that one is running before starting the unit tests")

    def run(self):
        self.run_command('build')

        for name, socketenabled, spreadenabled in [ ('spread', '0', '1'),
                                                    ('socket', '1', '0') ]:
            with open('test/with-%s.conf' % name, 'w') as f:
                f.write("""[transport.spread]
enabled = {spreadenabled}
port    = {spreadport}

[transport.socket]
enabled = {socketenabled}
port    = {socketport}"""
                        .format(spreadenabled = spreadenabled,
                                spreadport    = self.spreadport,
                                socketenabled = socketenabled,
                                socketport    = self.socketport))

        with open('test/spread.conf', 'w') as f:
            f.write("""Spread_Segment 127.0.0.255:{spreadport} {{
localhost 127.0.0.1
}}
SocketPortReuse = ON
                    """
                    .format(spreadport = self.spreadport))
        spread = None
        if self.spread and not self.spread == 'use-running':
            spread = CommandStarter([self.spread, "-n", "localhost", "-c", "test/spread.conf"])

        setuptools.command.test.test.run(self)

    def run_tests(self):
        """
        This method is overridden because setuptools 0.6 does not contain
        support for handling different test runners. In later versions it is
        probably not required to override this method.
        """
        import unittest
        import xmlrunner
        from pkg_resources import EntryPoint
        loader_ep = EntryPoint.parse("x=" + self.test_loader)
        loader_class = loader_ep.load(require=False)
        unittest.main(
            None, None, [unittest.__file__] + self.test_args,
            testLoader=loader_class(),
            testRunner=xmlrunner.XMLTestRunner(output='test-reports')
        )


setup(name='rsb-python',
      version='0.7.0.117',
      description='''
                  Fully event-driven Robotics Service Bus
                  ''',
      author='Johannes Wienke',
      author_email='jwienke@techfak.uni-bielefeld.de',
      license="LGPLv3+",
      url="https://code.cor-lab.org/projects/rsb",
      keywords=["middleware", "bus", "robotics"],
      classifiers=[
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Communications",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],

      setup_requires=["coverage", "epydoc", "unittest-xml-reporting", "protobuf"],

      extras_require={
        'spread-transport':  ["SpreadModule>=1.5spread4"],
      },
      
      dependency_links=['http://www.spread.org/files/SpreadModule-1.5spread4.tgz#egg=SpreadModule-1.5spread4'],

      packages=findRsbPackages(),
      test_suite="test.suite",

      cmdclass={'doc' : ApiDocCommand,
                'proto': FetchProtocol,
                'build_proto': BuildProtocol,
                'sdist' : Sdist,
                'build' : Build,
                'bdist_egg': BDist_egg,
                'test' : Test,
                'coverage' : Coverage}
      )
