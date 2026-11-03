import os
import math
import hashlib
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class LocalDeterministicEmbeddingFunction(EmbeddingFunction):
    """
    100% Free, local, CPU-based deterministic dense embedding function.
    Eliminates all external network dependencies and HuggingFace download latency.
    """
    def __init__(self, dim: int = 384):
        self.dim = dim

    def name(self) -> str:
        return "local_deterministic_dense"

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            vec = [0.0] * self.dim
            tokens = text.lower().split()
            if not tokens:
                embeddings.append(vec)
                continue
            for t in tokens:
                h = int(hashlib.md5(t.encode("utf-8")).hexdigest(), 16)
                idx = h % self.dim
                sign = 1.0 if ((h >> 8) & 1) else -1.0
                vec[idx] += sign
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            vec = [round(x / norm, 6) for x in vec]
            embeddings.append(vec)
        return embeddings

class LocalVectorStore:
    def __init__(self):
        self._client = None
        self._collection = None
        self.embedding_fn = LocalDeterministicEmbeddingFunction()

    @property
    def client(self):
        if self._client is None:
            os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
            try:
                self._client = chromadb.PersistentClient(
                    path=settings.CHROMA_PERSIST_DIR,
                    settings=ChromaSettings(anonymized_telemetry=False)
                )
            except Exception as e:
                logger.warning(f"ChromaDB PersistentClient locked or failed ({e}). Falling back to EphemeralClient.")
                self._client = chromadb.EphemeralClient(
                    settings=ChromaSettings(anonymized_telemetry=False)
                )
        return self._client

    @property
    def collection(self):
        if self._collection is None:
            try:
                self._collection = self.client.get_or_create_collection(
                    name=settings.CHROMA_COLLECTION_NAME,
                    embedding_function=self.embedding_fn,
                    metadata={"description": "Document RAG Chunks Collection"}
                )
                logger.info("ChromaDB collection ready with local embedding engine.")
            except Exception as e:
                logger.warning(f"Error accessing collection: {e}. Reinitializing with EphemeralClient.")
                self._client = chromadb.EphemeralClient(
                    settings=ChromaSettings(anonymized_telemetry=False)
                )
                self._collection = self._client.get_or_create_collection(
                    name=settings.CHROMA_COLLECTION_NAME,
                    embedding_function=self.embedding_fn,
                    metadata={"description": "Document RAG Chunks Collection"}
                )
        return self._collection

    def add_chunks(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[str]:
        if not chunks:
            return []

        ids = [c["id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [c.get("metadata", {}) for c in chunks]

        sanitized_metadatas = []
        for m in metadatas:
            sanitized = {}
            for k, v in m.items():
                if isinstance(v, (str, int, float, bool)):
                    sanitized[k] = v
                else:
                    sanitized[k] = str(v)
            sanitized_metadatas.append(sanitized)

        try:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=sanitized_metadatas
            )
            logger.info(f"Indexed {len(chunks)} chunks into ChromaDB.")
            return ids
        except Exception as e:
            logger.error(f"Error adding chunks to ChromaDB: {e}")
            return []

    def query_similar(
        self,
        query: str,
        user_id: str,
        document_id: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        where_filter: Dict[str, Any] = {"user_id": user_id}
        if document_id:
            where_filter = {
                "$and": [
                    {"user_id": user_id},
                    {"document_id": document_id}
                ]
            }

        try:
            count = self.collection.count()
            if count == 0:
                return []

            results = self.collection.query(
                query_texts=[query],
                n_results=min(top_k, count),
                where=where_filter
            )

            hits = []
            if results and results.get("documents") and results["documents"][0]:
                docs = results["documents"][0]
                metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
                distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)
                ids = results["ids"][0] if results.get("ids") else [""] * len(docs)

                for doc_id, text, meta, dist in zip(ids, docs, metas, distances):
                    hits.append({
                        "id": doc_id,
                        "text": text,
                        "metadata": meta,
                        "score": round(1.0 - float(dist), 4) if dist is not None else 1.0
                    })
            return hits
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return []

    def delete_document_chunks(self, document_id: str):
        try:
            self.collection.delete(
                where={"document_id": document_id}
            )
            logger.info(f"Deleted chunks for document {document_id}")
        except Exception as e:
            logger.warning(f"Failed to delete chunks for document {document_id}: {e}")

vector_store = LocalVectorStore()
