import pytest
from requests.exceptions import ConnectionError

from poetry.repositories import Pool
from poetry.repositories import Repository
from poetry.repositories.legacy_repository import LegacyRepository

from poetry.repositories.exceptions import PackageNotFound
from tests.repositories.test_pypi_repository import MockRepository


def test_pool_raises_package_not_found_when_no_package_is_found():
    pool = Pool()
    pool.add_repository(Repository())

    with pytest.raises(PackageNotFound):
        pool.package("foo", "1.0.0")


def test_pool_raises_connection_error_when_offline():
    pool = Pool()
    pool.add_repository(LegacyRepository(url="http://fake.url/simple", name="fake"))

    with pytest.raises(ConnectionError):
        pool.package("foo", "1.0.0")


def test_pool_fallback_through_repos():
    pool = Pool()
    pool.add_repository(LegacyRepository(url="http://fake.url/simple", name="fake"))
    pool.add_repository(MockRepository())

    package = pool.package("requests", "2.18.4")
    assert package.name == "requests"
    assert len(package.requires) == 4
    assert len(package.extras["security"]) == 3
    assert len(package.extras["socks"]) == 2

    win_inet = package.extras["socks"][0]
    assert win_inet.name == "win-inet-pton"
    assert win_inet.python_versions == "~2.7 || ~2.6"
    assert str(win_inet.marker) == (
        'sys_platform == "win32" and (python_version == "2.7" '
        'or python_version == "2.6") and extra == "socks"'
    )
