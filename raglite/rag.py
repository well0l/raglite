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

@bp.post("/api/ingest")
def ingest():
    """Indicizza un documento nella sessione di default."""
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    text = (payload.get("text") or "").strip()
    

    # 1. Se text è vuoto, restituisci {"error": "text is required"}, 400.
    # 2. Se title è vuoto, genera un titolo automatico con timestamp UTC.
    # 3. Recupera dal database l'id della "Default Session".
    # 4. Se la sessione non esiste, restituisci {"error": "default session not found"}, 500.
    # 5. Inserisci il document e conserva document_id.
    # 6. Calcola i chunk usando la configurazione dell'app.
    # 7. Per ogni chunk:
    #    - inserisci una riga in chunks
    #    - calcola il vettore
    #    - inserisci una riga in embeddings usando l'id reale del chunk appena creato
    # 8. Fai commit e restituisci title, document_id, chunks_indexed, embeddings_indexed.