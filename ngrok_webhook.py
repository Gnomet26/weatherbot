from pyngrok import ngrok
from secret import NGROK_TOKEN, BASE_PORT, BOT_TOKEN
from threading import Lock

class NgrokClass:
    def __init__(self):
        self.port = BASE_PORT
        ngrok.set_auth_token(NGROK_TOKEN)
        self._public_url = None
        self._lock = Lock()

    def _ensure_tunnel(self):
        if self._public_url is None:
            with self._lock:
                if self._public_url is None:  # Double-checked locking
                    tunnel = ngrok.connect(self.port, bind_tls=True)
                    self._public_url = tunnel.public_url

    def webhook_url(self):
        self._ensure_tunnel()
        return f"{self._public_url}/{BOT_TOKEN}"
