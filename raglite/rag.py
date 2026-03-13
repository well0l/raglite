"""Blueprint con le route dell'applicazione RAGlite."""

from __future__ import annotations

from flask import Blueprint, jsonify

bp = Blueprint("rag", __name__)  # TODO: dai un nome al blueprint (sarà il prefisso in url_for)


@bp.get("/api/health")  # TODO: scegli il decoratore HTTP e l'URL dell'endpoint (vedi "Risultati attesi")
def health():
    """Endpoint di verifica: l'app è in piedi?"""
    return jsonify({"ok": True, "version": "stub"})  # TODO: usa la funzione Flask che serializza in JSON