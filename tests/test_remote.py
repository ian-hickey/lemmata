"""A published registry served over HTTP, consumed through RemoteRegistry."""

import functools
import http.server
import threading

import pytest

from lemmata.index import build_index
from lemmata.registry import Registry, RegistryError, RemoteRegistry
from lemmata.verify import verify_workbook
from lemmata.xlsx import inject

REG = Registry.default()


@pytest.fixture(scope="module")
def served(tmp_path_factory):
    dist = tmp_path_factory.mktemp("dist")
    build_index(REG, dist)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(dist))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}/"
    httpd.shutdown()


def test_remote_registry_downloads_and_rehashes(served, tmp_path):
    remote = RemoteRegistry(served, cache_dir=tmp_path / "cache")
    assert {m.id for m in remote.modules} == {m.id for m in REG.modules}
    for m in remote.modules:
        assert m.module_hash == REG.get(m.id).module_hash
    # Second instance hits the cache: no index needed to load folders already present.
    again = RemoteRegistry(served, cache_dir=tmp_path / "cache")
    assert len(again.modules) == len(REG.modules)


def test_remote_registry_rejects_tampered_download(served, tmp_path):
    remote = RemoteRegistry(served, cache_dir=tmp_path / "cache")
    _ = remote.modules
    folder = next((tmp_path / "cache" / "modules").iterdir())
    lam = folder / "formula.lambda"
    lam.write_text(lam.read_text().replace("- 1", "- 2"))
    fresh = RemoteRegistry(served, cache_dir=tmp_path / "cache")
    with pytest.raises(RegistryError):
        _ = fresh.modules


def test_verify_through_remote_registry(served, tmp_path):
    remote = RemoteRegistry(served, cache_dir=tmp_path / "cache")
    path = tmp_path / "m.xlsx"
    inject(path, remote.with_dependencies([remote.get("gross_margin")]))
    report = verify_workbook(path, remote)
    assert report["ok"] and report["names"][0]["status"] == "current"


def test_default_registry_resolution(monkeypatch, served):
    monkeypatch.setenv("LEMMATA_REGISTRY", served)
    assert isinstance(Registry.default(), RemoteRegistry)
    monkeypatch.setenv("LEMMATA_REGISTRY", str(REG.root))
    assert not isinstance(Registry.default(), RemoteRegistry)
