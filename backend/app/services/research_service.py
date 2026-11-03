import logging
import socket
from datetime import datetime, timezone
from typing import List, Dict, Any
from duckduckgo_search import DDGS
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class WebResearchService:
    def __init__(self):
        self.max_results = settings.MAX_SEARCH_RESULTS

    def _has_connectivity(self) -> bool:
        """Quick check to avoid blocking on network if offline or inside restricted sandbox."""
        try:
            with socket.create_connection(("1.1.1.1", 53), timeout=0.4):
                return True
        except (socket.timeout, OSError):
            return False

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Executes a 100% free web search via DuckDuckGo and formats the citations.
        Returns a list of dicts: {title, url, snippet, retrieval_date}
        """
        results: List[Dict[str, Any]] = []
        if not query or not query.strip():
            return results

        if not self._has_connectivity():
            logger.info("Internet connection not reachable. Returning empty research citations.")
            return results

        now_str = datetime.now(timezone.utc).isoformat()

        try:
            with DDGS(timeout=5) as ddgs:
                ddg_gen = ddgs.text(
                    query.strip(),
                    max_results=max_results or self.max_results
                )
                for item in ddg_gen:
                    results.append({
                        "title": item.get("title", "Untitled Source"),
                        "url": item.get("href", ""),
                        "snippet": item.get("body", ""),
                        "retrieval_date": now_str
                    })
            logger.info(f"DuckDuckGo search for '{query}' returned {len(results)} results.")
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed for query '{query}': {e}")
        
        return results

research_service = WebResearchService()
