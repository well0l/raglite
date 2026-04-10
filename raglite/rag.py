"""Blueprint con le route dell'applicazione RAGlite."""

from __future__ import annotations

from flask import Blueprint, jsonify

from . import db

bp = Blueprint("rag", __name__)  # TODO: dai un nome al blueprint (sarà il prefisso in url_for)


@bp.get("/api/health")  # TODO: scegli il decoratore HTTP e l'URL dell'endpoint (vedi "Risultati attesi")
def health():
    """Endpoint di verifica: l'app è in piedi?"""
    return jsonify({"ok": True, "version": "stub"})  # TODO: usa la funzione Flask che serializza in JSON

@bp.get("/api/stats")
def stats():
    """Conta gli elementi indicizzati nel database."""
    conn = db.get_db()
    docs_row   = conn.execute("SELECT COUNT(*) AS n FROM documents").fetchone()
    chunks_row = conn.execute("SELECT COUNT(*) AS n FROM chunks").fetchone()
    emb_row    = conn.execute("SELECT COUNT(*) AS n FROM embeddings").fetchone()
    return jsonify({
        "chunks_indexed":     int(chunks_row["n"]),
        "docs_indexed":       int(docs_row["n"]),
        "embeddings_indexed": int(emb_row["n"]),
    })