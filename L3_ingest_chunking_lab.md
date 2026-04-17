# L3 — Laboratorio guidato: dal documento ai chunk indicizzati

| | |
|---|---|
| **Durata** | 110 minuti |
| **Prerequisiti** | `L2_database` completata: database inizializzato, `GET /api/stats` restituisce conteggi a zero |
| **Ambiente** | WSL2 + VSCode, `.venv` attiva |

---

## Risultati attesi

Al termine di questa lezione:

1. Saprai distinguere in modo operativo `document`, `chunk`, `embedding` e `message`.
2. Avrai aggiunto in `create_app()` la configurazione di `RAG_CHUNK_SIZE` e `RAG_CHUNK_OVERLAP`.
3. Avrai scritto `raglite/chunking.py` con una funzione `chunk_text(...)` che non spezza le frasi a metà.
4. Avrai scritto `raglite/embedding.py` con un vettore locale deterministico e `vector_to_blob(...)`.
5. Avrai esteso il Blueprint `rag` già introdotto in `L1` con `POST /api/ingest`.
6. Avrai verificato che un ingest riuscito fa crescere i conteggi letti da `GET /api/stats`.

---

## Come usare questo laboratorio

Questo laboratorio contiene alcuni punti intenzionalmente incompleti:

- scelte di implementazione da motivare
- funzioni da completare a partire da vincoli espliciti
- passaggi di integrazione da ricostruire leggendo il contesto

Quando trovi un punto incompleto, usa queste fonti in quest'ordine:

1. il testo del laboratorio
2. i file già presenti nel repository
3. l'output dei comandi, gli errori e i traceback
4. la documentazione ufficiale di Flask o Python, se ti serve conferma su un comportamento preciso

Durante il laboratorio non cercare scorciatoie (soluzioni, copia-incolla da AI).

Se un punto resta ambiguo:

- annota il problema
- spiega che cosa hai provato
- chiama il docente

---

## Parte 1 — Punto di partenza della lezione (10 min)

Prima di modificare il codice, fissa bene che cosa esiste già:

- in `L1` hai creato il Blueprint `rag` e l'endpoint `GET /api/health`
- in `L2` hai aggiunto `db.py`, lo schema SQL e `GET /api/stats`
- nel database esistono già `documents`, `chunks`, `embeddings` e `messages`

In `L3` non stai progettando ancora la chat completa.  
Stai costruendo una pipeline molto precisa:

1. ricevere un testo sorgente
2. registrarlo come `document`
3. dividerlo in `chunks`
4. associare un `embedding` a ogni chunk
5. salvare tutto nel database

In questa lezione `message` non entra ancora nella pipeline di ingest.

### Checkpoint 1

Rispondi prima di aprire i file:

1. Dopo un ingest riuscito, quali tabelle devono cambiare subito e quale invece deve restare invariata?
2. Perché in questa lezione ha senso estendere il Blueprint `rag` già esistente invece di crearne uno nuovo?
3. Quale informazione collega l'inserimento di un `document` agli inserimenti successivi in `chunks`?

---

## Parte 2 — Configurazione del chunking in `create_app()` (15 min)

Apri `raglite/__init__.py` e aggiungi alla configurazione base:

- `RAG_CHUNK_SIZE=110`
- `RAG_CHUNK_OVERLAP=1`

Per il laboratorio questi valori sono intenzionali:

- `110` è abbastanza piccolo da rendere visibile il chunking con il testo di prova finale
- `1` rende osservabile l'overlap senza complicare troppo la lettura dell'output

Non hard-codare questi valori dentro la route: devono stare in configurazione.

### Checkpoint 2

1. Quale comportamento della lezione diventerebbe meno osservabile se `RAG_CHUNK_SIZE` fosse molto più grande?
2. Perché `RAG_CHUNK_OVERLAP` ha senso come configurazione dell'app e non come costante nascosta dentro `chunk_text(...)`?

---

## Parte 3 — `raglite/chunking.py` (30 min)

### Obiettivo

La funzione `chunk_text(text, size, overlap)` deve:

1. dividere il testo in frasi
2. costruire chunk senza spezzare le frasi a metà
3. restituire una lista di tuple `(chunk_index, chunk_text)`
4. riusare le ultime `overlap` frasi come contesto del chunk successivo

In questa lezione non usiamo espressioni regolari.  
Per introdurre il concetto di chunking basta una soluzione più semplice e leggibile: una scansione carattere per carattere che chiude una frase quando incontra `.`, `!` oppure `?`.

### Punto di partenza

Crea `raglite/chunking.py` e inserisci subito questo helper completo:

```python
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
```

Questo helper non risolve tutti i casi linguistici reali.  
Per il laboratorio basta, perché rende osservabile il passaggio da testo completo a frasi intere senza introdurre strumenti nuovi non necessari.

### Vincoli per `chunk_text(...)`

Completa ora `chunk_text(...)` rispettando questi vincoli:

- se `size <= 0`, solleva `ValueError("size must be > 0")`
- se `overlap < 0`, solleva `ValueError("overlap must be >= 0")`
- se il testo è vuoto o contiene solo spazi, restituisci `[]`
- costruisci chunk aggiungendo frasi intere finché resti entro `size`
- l'overlap è espresso in numero di frasi, non in caratteri
- una frase molto lunga può restare da sola in un chunk

Usa questo scheletro:

```python
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

        # Aggiungi frasi intere finché il chunk resta entro size.
        # Poi salva (chunk_id, testo_chunk) e avanza lasciando overlap frasi in comune.

    return chunks
```

### Verifica rapida

Apri una shell Python:

```bash
python
```

Poi prova:

```python
from raglite.chunking import chunk_text
print(chunk_text("Una frase. Due frasi. Tre frasi.", size=20, overlap=1))
```

Controlla che:

- il risultato sia una lista
- ogni elemento sia una coppia `(indice, testo)`
- una frase finale del primo chunk compaia anche nel successivo

### Checkpoint 3

1. Perché l'overlap è espresso in frasi e non in caratteri?
2. Quale comportamento sbagliato otterresti se tagliassi il testo a lunghezza fissa senza rispettare i confini di frase?

---

## Parte 4 — `raglite/embedding.py` (20 min)

### Obiettivo

Qui non ti serve ancora un embedding semanticamente ricco.  
Ti serve un vettore locale, piccolo e deterministico, utile per:

- esercitare la pipeline completa
- vedere dati coerenti nel database
- fare debug senza dipendenze esterne aggiuntive

### Vincoli

L'embedding deve:

- avere dimensione fissa `4`
- restituire sempre lo stesso output a parità di input
- usare solo dati immediatamente ricavabili dal testo
- poter essere serializzato in un BLOB SQLite

Per questa lezione usa queste quattro caratteristiche:

1. lunghezza in byte
2. somma totale dei byte
3. primo byte
4. ultimo byte

### Scheletro da completare

Crea `raglite/embedding.py` a partire da queste firme:

```python
"""Embedding locale deterministico per il laboratorio."""

from __future__ import annotations

from array import array


def embed_text(text: str) -> list[float]:
    """Restituisce un embedding deterministico 4D."""
    ...


def vector_to_blob(vector: list[float]) -> bytes:
    """Serializza il vettore come BLOB SQLite."""
    ...
```

Vincoli di implementazione:

- usa `text.encode("utf8")`
- converti i quattro valori in `float`
- per il BLOB usa `array("f", vector).tobytes()`

### Verifica rapida

```bash
python -c "from raglite.embedding import embed_text; print(len(embed_text('ciao')))"
```

L'output atteso è:

```text
4
```

### Checkpoint 4

1. Perché un embedding deterministico è utile a questo punto dello sviluppo?
2. Quale parte del sistema stai verificando con `vector_to_blob(...)`, oltre al semplice calcolo del vettore?

### Commit 1

Se hai completato e verificato:

- la configurazione in `create_app()`
- `raglite/chunking.py`
- `raglite/embedding.py`

allora salva subito questa prima milestone:

```bash
git status
git add raglite/__init__.py raglite/chunking.py raglite/embedding.py
git commit -m "L3 feat: add chunking and embedding helpers"
```

---

## Parte 5 — Estendere `raglite/rag.py` con `POST /api/ingest` (30 min)

### Punto di partenza

In `raglite/rag.py` esistono già:

- il Blueprint `bp` introdotto in `L1`
- `GET /api/health`
- `GET /api/stats`

In questa lezione non devi riscrivere quel file da zero.  
Devi estenderlo.

### Obiettivo della route

La nuova route deve:

1. leggere `title` e `text` dal JSON in ingresso
2. rifiutare un `text` vuoto con `400`
3. recuperare la `Default Session` dal database
4. creare un `document`
5. creare i `chunks`
6. creare un `embedding` per ogni chunk
7. fare `commit()`
8. restituire un riepilogo JSON

In questa lezione:

- non creare righe in `messages`
- non assumere `session_id = 1`
- non nascondere il passaggio `document -> chunks -> embeddings`

### Cosa devi aggiungere

Aggiorna prima gli import del file per usare:

- `datetime`, `timezone`
- `current_app`, `request`
- `db`
- `chunk_text`
- `embed_text`, `vector_to_blob`

Poi aggiungi sotto `stats()` questa nuova funzione:

```python
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
```

### Nota tecnica su `lastrowid`

Quando esegui un `INSERT` con SQLite tramite `conn.execute(...)`, il valore restituito è un cursor.

Su quel cursor puoi leggere `lastrowid`, cioè l'id della riga appena inserita.

Qui serve in due punti:

- dopo l'`INSERT` in `documents`, per ottenere `document_id`
- dopo l'`INSERT` in `chunks`, per ottenere l'id reale del chunk da usare in `embeddings.chunk_id`

### Checkpoint 5

1. Perché la route deve leggere la `Default Session` dal database invece di assumere direttamente un id?
2. Perché `document` va inserito prima di `chunks`?
3. Quale confusione introdurresti se in questa stessa route cominciassi già a salvare anche `messages`?

---

## Parte 6 — Verifica finale (10 min)

Avvia:

```bash
flask --app raglite init-db
flask --app raglite run --debug
```

In un secondo terminale:

```bash
curl -s -X POST http://127.0.0.1:5000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"title":"rag-intro","text":"RAG recupera chunk rilevanti. SQLite conserva i dati locali. Il chunking non deve spezzare le frasi a metà."}'
```

Poi:

```bash
curl -s http://127.0.0.1:5000/api/stats
```

Controlla che:

- `docs_indexed` sia `1`
- `chunks_indexed` sia maggiore di `0`
- `embeddings_indexed` coincida con `chunks_indexed`

### Commit 2

Se anche `POST /api/ingest` funziona e la verifica finale passa, salva la seconda milestone:

```bash
git status
git add raglite/rag.py
git commit -m "L3 feat: add indexed ingest endpoint"
```

---

## Auto-verifica finale

1. Perché in questo punto del corso `document` e `message` devono restare separati?
2. Quale proprietà del chunking rende più leggibile il comportamento della pipeline durante il debug?
3. Che cosa stai realmente verificando quando `GET /api/stats` passa da zero a valori positivi?

---

## Controllo finale della storia Git

Quando tutto funziona:

- verifica lo stato del repo
- controlla che i commit intermedi siano presenti e leggibili
- non aggiungere un commit finale ridondante solo per "chiudere" la lezione

```bash
git status
git log --oneline -n 4
```

---

## Note libere

Annota qui:

- casi limite del chunking trovati durante la prova
- dubbi sul significato di `document` rispetto a `message`
- errori incontrati nell'ingest
- punti da chiarire meglio nel laboratorio
