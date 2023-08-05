import os.path

from fabric.api import settings, run, cd, lcd, put, get, local, env, with_settings
from fabric.contrib.files import append
from fabric.colors import green

from . import versions
from .cache import cache
from .tools import rsync
from .defaults import debian as debian_defaults
from .defaults import centos as centos_defaults

#
# Used to represent the remote build distribution
#

class Distro(object):
    space = '.parcel-build-temp'
    pip_download_cache = '/tmp/pip-download-cache/'

    def __init__(self):
        pass

    def mkdir(self, remote):
        return run('mkdir -p "%s" && cd "%s" && pwd'%(remote,remote))

    def update_packages(self):
        """This method should update the packages on the remote box.
        """
        raise NotImplementedError

    def build_deps(self, deps):
        """This method should install the build dependencies on the remote box.
        """
        raise NotImplementedError

    def version(self,package):
        """Look at the distro's packaging system for the package and return a version"""
        raise NotImplementedError
	
    def push_files(self,pathlist,dst):
        for path in pathlist:
            put(path, os.path.join(dst,os.path.basename(path)))
    	
    def check(self):
        """Check the remote build host to see if the relevant software to build packages is installed"""
        raise NotImplementedError
    
    def setup(self):
        """This method should set up a remote box for parcel package building.
        It should install fpm.
        """
        raise NotImplementedError

    def install_package(self, pkg):
        """Installs package on the host using apt-get install bypassing
        authentication. This method should be used for testing package
        installation before using push_to_repo."""
        raise NotImplementedError

    def _cleanup(self):
        run("rm -rf '%s'"%self.space)  

    def _setup(self, clean=True):
        # first cleanup any broken stale previous builds
        if clean:
            self._cleanup()

        # make fresh directories
        base_dir = self.mkdir(self.space)
        src_dir = self.mkdir(self.space+"/src")
        build_dir = self.mkdir(self.space+"/build")
        return base_dir, src_dir, build_dir


class Debian(Distro):

    def __init__(self):
        self.defaults = debian_defaults

    def update_packages(self):
        with settings(user='root'):
            run("apt-get update -qq")

    def build_deps(self, deps):
        with settings(user='root'):
            run("apt-get install -qq %s"%(' '.join(deps)))

    def version(self,package):
        """Look at the debian apt package system for a package with this name and return its version.
        Return None if there is no such package.
        """
        with settings(warn_only=True):
            vstring = run('apt-cache show %s 2>/dev/null | sed -nr "s/^Version: ([0-9]+)(-.+)?/\\1/p"'%(package))
            if vstring.return_code:
                # error fetching package info. Assume there is no such named package. Return None
                return None
            return versions.Version(vstring)

    def check(self):
        """Check the remote build host to see if the relevant software to build packages is installed"""
        with settings(warn_only=True):
            # check for fpm
            result = run('which fpm')
            if result.return_code:
                raise Exception("Build host does not have fpm installed and on the executable path")
            
            # check for checkinstall
            result = run('which checkinstall')
            if result.return_code:
                raise Exception("Build host does not have checkinstall installed and on the executable path")

    def setup(self):
        """this method sets up a remote debian box for parcel package building.
        Installs fpm, easyinstall and some libraries.
        """
        with settings(user='root'):
            self.build_deps(['libyaml-ruby','libzlib-ruby','ruby','ruby-dev','checkinstall'])

            base_dir, src_dir, build_dir = self._setup()
            
            # get rubygems and copy it across
            path = cache.get("http://production.cf.rubygems.org/rubygems/rubygems-1.8.24.tgz")
            self.push_files([path],src_dir)
            filename = os.path.basename(path)
            
            with cd(build_dir):
                run("tar xvfz ../src/%s"%filename)
                with cd("rubygems-1.8.24"):
                    run("ruby setup.rb")
            run("gem1.8 install fpm")

    def install_package(self, pkg):
        """Installs package on the host using apt-get install bypassing
        authentication. This method should be used for testing package
        installation before using push_to_repo."""
        base_dir, src_dir, build_dir = debian._setup(clean=False)
        pkg_dir = self.mkdir(base_dir+"/pkg_dir")
        rsync(pkg,pkg_dir)
        with cd(pkg_dir):
            print green(append("/etc/apt/sources.list", "deb file://{0} /".format(pkg_dir))) 
            print green(run("dpkg-scanpackages . /dev/null | gzip -c -9 > Packages.gz"))
            pkg_name = run("dpkg -f {0} | grep '^Package: ' | sed -e 's/Package: //'".format(pkg))
            pkg_version = run("dpkg -f {0} | grep '^Version: ' | sed -e 's/Version: //'".format(pkg))
            print green(run("apt-get update -qq"))
            print green(run("apt-get install {0}={1} -qq --allow-unauthenticated".format(pkg_name,pkg_version)))


    def build_package(self, deployment=None):
        """
        Runs architecture specific packaging tasks
        """
        assert deployment
        
        with cd(deployment.root_path):
            rv = run(
                'fpm -s dir -t deb -n {0.pkg_name} -v {0.version} '
                '-a all -x "*.git" -x "*.bak" -x "*.orig" {0.hooks_str} '
                '--description "Automated build. '
                'No Version Control." '
                '{0.deps_str} {0.dirs_str}'
                .format(deployment)
            )

            filename = rv.split('"')[-2]
            get(filename, './')
            run("rm '%s'"%filename)
            print green(os.path.basename(filename))


class Ubuntu(Debian):

    def setup(self):
        """this method sets up a remote ubuntu box for parcel package building.
        Installs fpm and also rubygems if not present.
        """
        with settings(user='root'):
            run("apt-get install rubygems -y")
            run("gem install fpm")


class Centos(Distro):

    def __init__(self):
        self.defaults = centos_defaults

    def update_packages(self):
        with settings(user='root'):
            run("yum update -y")

    def build_deps(self, deps):
        with settings(user='root'):
            run("yum install -y %s"%(' '.join(deps)))

    def version(self,package):
        """Look at the debian apt package system for a package with this name and return its version.
        Return None if there is no such package.
        """
        with settings(warn_only=True):
            vstring = run('rpm -qi %s 2>/dev/null | sed -nr "s/^Version.+: ([0-9]+)(-.+)?/\\1/p"' % (package))
            if vstring.return_code:
                # error fetching package info. Assume there is no such named package. Return None
                return None

            # remove vender part of string
            vstring = vstring.split()[0]
            return versions.Version(vstring)

    def check(self):
        """Check the remote build host to see if the relevant software to build packages is installed"""
        with settings(warn_only=True):
            # check for fpm
            result = run('which fpm')
            if result.return_code:
                raise Exception("Build host does not have fpm installed and on the executable path")

    def setup(self):
        """this method sets up a remote centos box for parcel package building.
        Installs fpm and also rubygems if not present.
        """
        with settings(user='root'):
            run("yum install rubygems -y")
            run("gem install fpm")
            run("yum install rpm-build -y")
            run("yum install rsync -y")            

    def build_package(self, deployment=None):
        """
        Runs architecture specific packaging tasks
        """
        assert deployment
        
        with cd(deployment.root_path):
            rv = run(
                'fpm -s dir -t rpm -n {0.pkg_name} -v {0.version} '
                '-a all -x "*.git" -x "*.bak" -x "*.orig" {0.hooks_str} '
                '--description "Automated build. '
                'No Version Control." '
                '{0.deps_str} {0.dirs_str}'
                .format(deployment)
            )

            filename = rv.split('"')[-2]
            get(filename, './')
            run("rm '%s'"%filename)
            print green(os.path.basename(filename))



# the distribution module instances
debian = Debian()
ubuntu = Ubuntu()
centos = Centos()
