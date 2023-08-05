import os.path
import util, error

class AptGetPackage(object):
    path = None

    def install(self, name):
        try:
            return util.shell('export DEBIAN_FRONTEND=noninteractive && %s -qq -y install %s' % (self.path, name))
        except error.CalledProcessError, e:
            raise error.PackageError(str(e))

    def list(self):
        '''Return a list of all installed packages on the system'''
        packages = []
        for item in util.shell('dpkg --get-selections').strip().splitlines():
            packages.append(item.split()[0])

        return packages

    def extract(self, name, to_path):
        '''Download a given package along with its dependencies, then extract all files into the given folder'''
        util.shell('%s clean' % self.path)
        util.shell('%s -qq -y -d install %s' % (self.path, name))

        if not os.path.exists(to_path):
            os.makedirs(to_path, 0777)

        for path in [os.path.join('/var/cache/apt/archives/', path) for path in os.listdir('/var/cache/apt/archives') if path.endswith('.deb')]:
            util.shell('dpkg-deb -x %s %s' % (path, to_path))

    def update(self):
        try:
            return util.shell('export DEBIAN_FRONTEND=noninteractive && %s -qq -y update' % self.path)
        except error.CalledProcessError, e:
            raise error.PackageError(str(e))

    def upgrade(self):
        try:
            return util.shell('export DEBIAN_FRONTEND=noninteractive && %s -qq -y -o Dpkg::Options::="--force-confold" upgrade' % self.path)
        except error.CalledProcessError, e:
            raise error.PackageError(str(e))


class YumPackage(object):
    path = None

    def install(self, name):
        try:
            return util.shell('%s -q -y install %s' % (self.path, name))
        except error.CalledProcessError, e:
            raise error.PackageError(str(e))

    def list(self):
        '''Return a list of all installed packages on the system'''
        packages = []
        for item in util.shell('%s -q list installed' % self.path).strip().splitlines()[1:]:
            if item.startswith(' '): continue
            item = item.split()[0]
            if '.' in item: item = item.rsplit('.', 1)[0]
            packages.append(item)

        return packages

    def update(self):
        try:
            return util.shell('%s -q update' % self.path)
        except error.CalledProcessError, e:
            raise error.PackageError(str(e))

    def upgrade(self):
        try:
            return util.shell('%s -q upgrade' % self.path)
        except error.CalledProcessError, e:
            raise error.PackageError(str(e))

    def extract(self, name, path):
        raise NotImplementedError('auto-generating roles from packages is not supported on yum-based systems')


class PipPackage(object):
    path = None

    def __init__(self):
        self.path = search_path('pip')

    def install(self, name, upgrade=False):
        try:
            if upgrade:
                return util.shell('%s -q install -U %s' % (self.path, name))
            else:
                return util.shell('%s -q install %s' % (self.path, name))
        except error.CalledProcessError, e:
            raise error.PackageError(str(e))

    def list(self):
        packages = []
        for item in util.shell('%s freeze -q' % self.path).strip().splitlines():
            if item.startswith('#') or item.startswith('Warning:'): continue

            try:
                pkg_name, pkg_ver = item.strip().split('==', 2)
            except:
                continue

            packages.append(pkg_name)
        return packages

    def extract(self, name, path):
        raise NotImplementedError('auto-generating roles from packages is not supported for pip packages')

    def update(self):
        '''Pip doesn't maintain a local cache of package versions, so no-op here'''
        pass

    def upgrade(self):
        for package in self.list():
            self.install(package, upgrade=True)


class UnknownPackage(object):
    '''If we can't find a package manager, allow Bishop to run but do not allow any package installation to take place'''
    def install(self, name):
        raise NotImplementedError('Package management is disabled, since yum and apt-get were not found')
    def list(self):
        raise NotImplementedError('Package management is disabled, since yum and apt-get were not found')
    def extract(self, name, path):
        raise NotImplementedError('Package management is disabled, since yum and apt-get were not found')
    def update(self):
        raise NotImplementedError('Package management is disabled, since yum and apt-get were not found')
    def upgrade(self):
        raise NotImplementedError('Package management is disabled, since yum and apt-get were not found')


def search_path(bin):
    '''Given a binary name, search the environment PATH for a matching name'''
    path = os.getenv('PATH', '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin')
    for location in path.split(os.pathsep):
        test_path = os.path.join(location, bin)
        if os.path.exists(test_path):
            return test_path

    raise ValueError('Could not find binary in path matching program name %s' % bin)


#Dynamically set Package class at time of import depending on the available binaries in the system
try:
    apt_path = search_path('apt-get')
    AptGetPackage.path = apt_path
    Package = AptGetPackage
except ValueError, e:
    try:
        yum_path = search_path('yum')
        YumPackage.path = yum_path
        Package = YumPackage
    except ValueError, e:
        Package = UnknownPackage


repos = {
    'apt': AptGetPackage,
    'yum': YumPackage,
    'default': Package,
    'pip': PipPackage
}
