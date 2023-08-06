from distutils.version import StrictVersion, LooseVersion
from pkgtools.pypi import PyPIXmlRpc
from .errors import DoesNotExists


class Version(object):

    def __init__(self, number):
        try:
            number = StrictVersion(number)
        except ValueError:
            number = LooseVersion(number)
        self.number = number

    def __repr__(self):
        return '.'.join(map(str, self.number.version))

    def __str__(self):
        return self.__repr__()

    def version_wrapper(func):
        def decorator(first, second):
            if isinstance(second, Version):
                second = second.number
            return func(first, second)
        return decorator

    @version_wrapper
    def __eq__(self, second):
        return self.number == second

    @version_wrapper
    def __ne__(self, second):
        return self.number != second

    @version_wrapper
    def __lt__(self, second):
        return self.number < second

    @version_wrapper
    def __gt__(self, second):
        return self.number > second

    @version_wrapper
    def __le__(self, second):
        return self.number <= second

    @version_wrapper
    def __ge__(self, second):
        return self.number >= second


class Package(object):

    def __init__(self, name, version=None, client=None):
        self.name = name
        self.client = client or PyPIXmlRpc()
        if version:
            self.version = Version(version)
        else:
            self.version = Version(self.last_release)

    @property
    def metadata(self):
        description = self.client.release_data(self.name, str(self.version))
        if not description:
            raise DoesNotExists
        return description

    @property
    def releases(self):
        try:
            self.__releases = self.__releases
        except AttributeError:
            self.__releases = self.client.package_releases(self.name)
        return sorted(self.__releases)

    @property
    def last_release(self):
        try:
            return self.releases[-1]
        except IndexError:
            raise DoesNotExists

    @property
    def urls(self):
        urls = self.client.release_urls(self.name, str(self.version))
        return urls[0]

    def __eq__(self, second):
        return self.name == second.name and self.version == second.version

    def __ne__(self, second):
        return self.name != second.name or self.version != second.version

    def __repr__(self):
        return "{}({})".format(self.name, '.'.join(map(str, self.version.number.version)))

    def __iter__(self):

        items = (
            ('name', self.name),
            ('version', self.version),
        )

        for item in items:
            yield item
