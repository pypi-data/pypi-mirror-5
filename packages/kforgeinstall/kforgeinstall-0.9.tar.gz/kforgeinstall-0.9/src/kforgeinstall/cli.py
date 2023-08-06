import os
import sys
from optparse import OptionParser
import pipes
import shutil
import pexpect

class KForgeInstallCli(object):

    usage  = '''usage: %prog [OPTIONS] [PATH]

Installs KForge software to current working directory, or PATH if provided.

See --help for options.
'''

    def __init__(self):
        self.createOptionParser()
        self.makeOptions()
        self.parseArgs()
        self.readPath()
        self.runInstaller()

    def createOptionParser(self):
        self.parser = OptionParser(self.usage)

    def makeOptions(self):
        self.parser.add_option(
            '-v', '--verbose',
            dest='isVerbose',
            action='store_true',
            help='provide more detailed information about steps taken'
        )
        self.parser.add_option(
            '-q', '--quiet',
            dest='isQuiet',
            action='store_true',
            help='supress output that indicates progress'
        )
        self.parser.add_option(
            '-p', '--python',
            dest='withPython',
            default='',
            help='the Python interpreter to use for the virtualenv'
        )
        self.parser.add_option(
            '-a', '--with-all-services',
            dest='withAll',
            action='store_true',
            help='install software needed for every kind of service (equivalent to --with-dav --with-mercurial --with-subversion --with-trac)'
        )
        self.parser.add_option(
            '--with-dav',
            dest='withDav',
            action='store_true',
            help='install software needed for Dav services'
        )
        self.parser.add_option(
            '--with-git',
            dest='withGit',
            action='store_true',
            help='this option currently has no affect'
        )
        self.parser.add_option(
            '--with-mercurial',
            dest='withMercurial',
            action='store_true',
            help='install software needed for Mercurial services'
        )
        self.parser.add_option(
            '--with-subversion',
            dest='withSvn',
            action='store_true',
            help='install software needed for Subversion services'
        )
        self.parser.add_option(
            '--with-trac',
            dest='withTrac',
            action='store_true',
            help='install software needed for Trac services'
        )
        self.parser.add_option(
            '--with-postgresql',
            dest='withPostgresql',
            action='store_true',
            help='install software needed to use PostgreSQL databases'
        )
        self.parser.add_option(
            '--with-mysql',
            dest='withMysql',
            action='store_true',
            help='install software needed to use MySQL databases'
        )
        self.parser.add_option(
            '--with-kforge',
            dest='kforge_requirement_or_url',
            default='kforge',
            help='install a specific kforge package (defaults to latest stable version of KForge obtainable from the Python Package Index)'
        )
        self.parser.add_option(
            '--with-domainmodel',
            dest='dm_requirement_or_url',
            default='',
            help='install specific domainmodel package (defaults to package required by KForge, obtained from the Python Package Index)'
        )

    def parseArgs(self):
        (self.options, self.args) = self.parser.parse_args()

    def readPath(self):
        if len(self.args) == 1:
            self.installPath = self.args[0]
        else:
            self.installPath = '.'

        try:
            self.installPath = os.path.abspath(self.installPath)
        except:
            print "Error: Couldn't make absolute path from given path: %s" % self.installPath

    def runInstaller(self):
        installer = KForgeInstaller(self.installPath, self.options)
        installer.run()
        if not self.options.isQuiet:
            print "KForge software and dependepencies installed OK"


class KForgeInstaller(object):

    def __init__(self, path, options, umask=0o22):
        os.umask(umask)
        self.path = path
        self.options = options

    def run(self):
        #print "Installing KForge software to: %s" % self.path
        self.createVirtualenv()
        self.installKForge()
        self.installDatabases()
        self.installServices()

    def createVirtualenv(self):
        args = ['virtualenv', '--no-site-packages', '--distribute', self.path]
        if self.options.withPython:
            args.append('--python')
            args.append(self.options.withPython)
        self.runCmd(args)

    # Methods to install specific software packages.

    def installDatabases(self):
        if self.options.withMysql:
            self.installMysql()
        if self.options.withPostgresql:
            self.installPostgresql()

    def installMysql(self):
        self.pipInstall('MySQL-python')
        if not self.options.isQuiet:
            print "MySql Python package installed OK"

    def installPostgresql(self):
        if not self.canPythonImport('mx.DateTime'):
            self.installMxDateTime()
        self.installPsycopg2()

    def installMxDateTime(self):
        version = '3.2.5'
        url = 'http://downloads.egenix.com/python/egenix-mx-base-%s.tar.gz' % version
        self.pipInstall(url)
        if not self.options.isQuiet:
            print "mx.DateTime Python package installed OK"

    def installPsycopg2(self):
        self.pipInstall('psycopg2')
        if not self.options.isQuiet:
            print "PostgreSQL Python package installed OK"

    def installKForge(self):
        self.installDomainModel()
        self.pipInstall(self.options.kforge_requirement_or_url)
        if not self.options.isQuiet:
            print "KForge Python package installed OK"

    def installDomainModel(self):
        if self.options.dm_requirement_or_url:
            self.pipInstall(self.options.dm_requirement_or_url)
            if not self.options.isQuiet:
                print "DomainModel Python package installed OK"

    def installServices(self):
        # Trac
        # (install Trac before Mercurial, otherwise it installs Trac 1.0, when we currently want 0.12)
        if self.options.withTrac or self.options.withAll:
            self.installTrac()
        # DAV
        if self.options.withDav or self.options.withSvn or self.options.withAll:
            self.installDav()
        # Mercurial
        if self.options.withMercurial or self.options.withAll:
            self.installMercurial()
        # Svn
        if self.options.withSvn or self.options.withAll:
            self.installSubversion()

    def installTrac(self):
        self.pipInstall('trac==1.0.1')
        if not self.options.isQuiet:
            print "Trac Python package installed OK"

    def installDav(self):
        self.pipInstall('wsgidav')
        if not self.options.isQuiet:
            print "DAV WSGI Python package installed OK"

    def installMercurial(self):
        # Trac Mercurial plugin.
        self.pipInstall('http://mercurial.selenic.com/release/mercurial-2.5.2.tar.gz')
        if not self.options.isQuiet:
            print "Mercurial Python package installed OK"
        #print "Installing Trac plugin for Mercurial repositories"
        # Since 'pip install' doesn't really work with this URL...
        #    <https://hg.edgewall.org/trac/mercurial-plugin#0.12>
        # ... so we have to do take these steps instead:
        hgUrl = 'https://hg.edgewall.org/trac/mercurial-plugin#1.0'
        hgPath = self.join(self.path, 'src-trac-mercurial-plugin-1.0')
        try:
            self.runCmd(['hg', 'clone', hgUrl, hgPath])
            self.pipInstall(hgPath)
        finally:
            shutil.rmtree(hgPath)
        if not self.options.isQuiet:
            print "Trac Mercurial Python package installed OK"

    def installSubversion(self):
        # Install Python bindings.
        # - find the svn package dir.
        self.runCmd(['/usr/bin/python', '-c', 'import svn; print svn.__file__'])
        svnPath = os.path.dirname(self.output)
        # - create a directory with symlink to system package
        linksPath = self.join(self.path, 'linked-python-subversion')
        if not os.path.exists(linksPath):
            self.runCmd(['mkdir', linksPath])
            self.runCmd(['ln', '-s', svnPath, self.join(linksPath, 'svn')])
        # - create .pth file with path to the directory containing the symlink
        self.runCmd([self.getPythonBinPath(), '-c', 'import os; print os.__file__'])
        osPath = os.path.dirname(self.output)
        pthPath = self.join(osPath, 'site-packages', 'python-subversion.pth')
        if not os.path.exists(pthPath):
            pthFile = open(pthPath, 'w')
            pthFile.write(linksPath)
            pthFile.close()
        if not self.options.isQuiet:
            print "Subversion Python package installed OK"


    # General methods used to install software.
    
    def pipInstall(self, requirement_or_url):
        pipInstallOptions = requirement_or_url.split()
        cmds = [self.getPipBinPath()]
        cmds.append('install')
        cmds += pipInstallOptions
        if self.options.isVerbose:
            cmds.append('-v')
        self.runCmd(cmds)

    def canPythonImport(self, name):
        cmds = [self.getPythonBinPath(), '-c', 'import %s' % name]
        try:
            self.runCmd(cmds)
        except:
            return False
        else:
            return True
        
    def runCmd(self, cmds, cwd=None):
        cmdstr = " ".join(pipes.quote(i) for i in cmds)
        if self.options.isVerbose:
            print cmdstr
        try:
            cmd = pexpect.spawn(cmdstr)
            self.output = ''
            while True:
                try:
                    i = cmd.read_nonblocking(size=1, timeout=None)
                except pexpect.EOF, inst:
                    i = ''
                if i == '':
                    break
                self.output += i
                if not self.options.isQuiet:
                    sys.stdout.write(i)
                    sys.stdout.flush()
            if cmd.isalive():
                cmd.wait()
            self.status = cmd.exitstatus
            if self.status is None:
                self.status = 0
        except pexpect.TIMEOUT, inst:
            raise Exception, "Error: Command timed out."
        except Exception, inst:
            import traceback
            self.status = 1
            self.output = traceback.format_exc()
        if self.status:
            msg = "Couldn't run command: %s\nCommand output:\n%s" % (cmdstr, self.output)
            raise Exception, msg

    def getPipBinPath(self):
        return self.join(self.getBinPath(), 'pip')

    def getPythonBinPath(self):
        return self.join(self.getBinPath(), 'python')

    def getBinPath(self):
        return self.join(self.path, 'bin')

    def join(self, *args):
        return os.path.join(*args)


