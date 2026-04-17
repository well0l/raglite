"""Embedding locale deterministico per il laboratorio."""

from __future__ import annotations

from array import array


def embed_text(text: str) -> list[float]:
    """Restituisce un embedding deterministico 4D."""
    byte_text = text.encode('utf8')
    byte_len=len(byte_text)
    if byte_len == 0:
        byte_sum=0
        firstb=0
        lastb=0
    else:
        byte_sum=sum(byte_text)
        firstb=byte_text[0]
        lastb=byte_text[-1]

    res = [float(byte_len), float(byte_sum), float(firstb), float(lastb)]
    return res 


def vector_to_blob(vector: list[float]) -> bytes:
    """Serializza il vettore come BLOB SQLite."""
    vec = array("f", vector).tobytes()
    return vec