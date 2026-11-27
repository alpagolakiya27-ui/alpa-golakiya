import threading

import pytest
import requests

from app.server import create_server


@pytest.fixture()
def base_url():
    """Start a fresh server on a free port for every test (isolated state)."""
    server = create_server(port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


@pytest.fixture()
def api(base_url):
    class Client:
        url = base_url

        def get(self, path, **kw):
            return requests.get(base_url + path, timeout=5, **kw)

        def post(self, path, **kw):
            return requests.post(base_url + path, timeout=5, **kw)

        def delete(self, path, **kw):
            return requests.delete(base_url + path, timeout=5, **kw)

    return Client()
