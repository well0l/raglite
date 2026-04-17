"""Chunking sentence-aware per il laboratorio."""

from __future__ import annotations


def _split_sentences(text: str) -> list[str]:
    """Divide il testo in frasi senza spezzarle a metà."""
    text = text.strip()
    if not text:
        return []

    sentences: list[str] = []
    current: list[str] = []

    for char in text:
        current.append(char)
        if char in ".!?":
            sentence = "".join(current).strip()
            if sentence:
                sentences.append(sentence)
            current = []

    tail = "".join(current).strip()
    if tail:
        sentences.append(tail)

    return sentences

def chunk_text(text: str, size: int, overlap: int) -> list[tuple[int, str]]:
    """Restituisce chunk testuali con overlap in numero di frasi."""
    if size <= 0:
        raise ValueError("size must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")

    sentences = _split_sentences(text)
    if not sentences:
        return []

    chunks: list[tuple[int, str]] = []
    chunk_id = 0
    i = 0

    while i < len(sentences):
        acc: list[str] = []
        char_count = 0
        j = i
        while j < len(sentences):
            newl = char_count + len(sentences[j])
            if acc != []:
                    newl+=1
            if (newl <= size):
                acc.append(sentences[j])
                char_count=newl
            else:
                if acc == []:
                    acc.append(sentences[j])
                    break
                else: break  
            j+=1
        chunk_text = " ".join(acc)
        chunks.append((chunk_id, chunk_text))
        chunk_id += 1       
        newi=j-overlap
        if newi <= i: newi+=1
        i=newi
         # Aggiungi frasi intere finché il chunk resta entro size.
        # Poi salva (chunk_id, testo_chunk) e avanza lasciando overlap frasi in comune.

    return chunks