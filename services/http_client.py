import httpx
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class HttpClient:
    """
    Paylaşımlı httpx.AsyncClient yönetimi için yardımcı sınıf.
    Connection pooling avantajı sağlar ve her istekte yeni client oluşturma maliyetini önler.
    """
    client: Optional[httpx.AsyncClient] = None

    def start(self):
        """Uygulama başlangıcında client'ı ilklendirir."""
        if self.client is None:
            self.client = httpx.AsyncClient()
            logger.info("Shared httpx.AsyncClient started.")

    async def stop(self):
        """Uygulama kapanışında client'ı kapatır."""
        if self.client is not None:
            await self.client.aclose()
            self.client = None
            logger.info("Shared httpx.AsyncClient stopped.")

    def get_client(self) -> httpx.AsyncClient:
        """Client'ı döndürür. start() çağrılmamışsa hata fırlatabilir veya otomatik oluşturabilir."""
        if self.client is None:
            # Fallback: lifespan kullanılmazsa otomatik oluştur
            self.client = httpx.AsyncClient()
            logger.warning("httpx.AsyncClient was not started via start(). Creating a fallback instance.")
        return self.client

# Singleton örneği
http_client = HttpClient()
