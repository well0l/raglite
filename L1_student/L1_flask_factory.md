# Flask application factory, Blueprint e primo endpoint

| | |
|---|---|
| **Durata** | 120 minuti |
| **Prerequisiti** | Lezione precedente completata: progetto su GitHub, ambiente virtuale attivo, `pip install -e ".[dev]"` eseguito |
| **Ambiente** | WSL2 + VSCode, `.venv` attivo |

---

## Risultati attesi

Al termine di questa lezione:

1. Saprai cos'è l'*application factory* e perché è preferibile a creare l'app come variabile globale.
2. Avrai scritto `raglite/__init__.py` con la funzione `create_app()` che configura e restituisce l'applicazione Flask.
3. Avrai scritto `raglite/rag.py` con un Blueprint registrato sull'app.
4. Avrai il tuo primo endpoint funzionante: `GET /api/health` risponde con `{"ok": true, "version": "stub"}`.
5. Saprai avviare il server in modalità debug e vedere il reload automatico in azione.

Alla fine della lezione, eseguendo questi comandi, tutto deve funzionare senza errori:

```bash
flask --app raglite run --debug
```

```bash
# In un secondo terminale, oppure con un client HTTP:
curl http://127.0.0.1:5000/api/health
# atteso: {"ok":true,"version":"stub"}
```

---

## Parte 1 — Il problema che l'application factory risolve (15 min)

### 1.1 L'approccio "globale" e i suoi limiti

Il modo più semplice per creare un'app Flask è questo:

```python
from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "ciao"
```

Funziona per un tutorial di dieci righe. Non funziona bene appena il progetto cresce, per due ragioni concrete:

**Problema 1 — configurazione per i test.**
Nei test automatizzati hai bisogno di un database separato, di timeout ridotti, di funzionalità disabilitate. Se l'app è una variabile globale, al momento dell'import è già costruita con la configurazione di default — non puoi cambiarla prima che esista.

**Problema 2 — import circolari.**
Un'app reale ha più file: `db.py`, `rag.py`, `auth.py`... Ognuno importa `app` per registrarsi. Se `app` è globale in `__init__.py`, e `__init__.py` importa `db.py`, e `db.py` importa `app` da `__init__.py`, Python va in loop.

### 1.2 La soluzione: factory function

Invece di costruire l'app al momento dell'import, la costruiamo dentro una funzione:

```python
def create_app(test_config=None):
    app = Flask(__name__)
    # ... configura, registra blueprint, ecc.
    return app
```

Ogni chiamata a `create_app()` produce un'istanza fresca e indipendente.  
I test chiamano `create_app({"DATABASE": ":memory:"})` e ottengono un'app isolata.  
Flask sa già cercare questa funzione: se `__init__.py` la definisce, `flask --app raglite run` la trova automaticamente.

**Rispondi prima di continuare:**

1. Nei test, ogni test chiama esplicitamente `create_app()`. Le due istanze di app condividono stato? Cosa succederebbe invece con l'approccio globale, dove `app` è creata al momento dell'import?
2. Nell'approccio globale, `db.py` importa `app` da `__init__.py` e `__init__.py` importa `db.py`. Disegna il grafo delle dipendenze: dove si forma il ciclo? Perché con la factory il ciclo non si forma?
3. `flask --app raglite run` trova `create_app` automaticamente. Come fa Flask a sapere dove cercarla — cosa deve essere vero nel file `__init__.py`?

---

## Parte 2 — `raglite/__init__.py`: la factory (25 min)

Apri il file `raglite/__init__.py` in VSCode. È ancora vuoto. Implementa `create_app()` partendo da questo scheletro — riempi ogni `???` basandoti sulla spiegazione della Parte 1:

```python
"""Application factory per RAGlite."""

from __future__ import annotations

import os

from flask import Flask


def create_app(test_config: dict | None = None) -> Flask:
    """Crea e configura l'istanza Flask.

    Args:
        test_config: dizionario di configurazione usato nei test
                     per sovrascrivere i valori di default.
                     Se None, viene caricato instance/config.py (se esiste).
    """
    app = Flask(__name__, instance_relative_config=???)  # TODO: True o False? Perché?

    app.config.from_mapping(
        SECRET_KEY=???,  # TODO: setta la key per lo sviluppo locale?
        DATABASE=os.path.join(???, "raglite.sqlite"),  # TODO: leggi da app il path giusto
    )

    if test_config is None:
        app.config.from_pyfile(???, silent=???)  # TODO: specifica il file di config; perché silent=True?
    else:
        ???  # TODO: il dizionario test_config?

    os.makedirs(???, exist_ok=True)  # TODO: usa l'attributo di app con il path di instance/

    from . import rag
    ???  # TODO: registra il blueprint?

    return app
```

**Verifica prima di andare avanti:** aggiungi temporaneamente `print(app.instance_path)` dopo `os.makedirs(...)` e avvia il server con `flask --app raglite run`. Il path stampato è quello che ti aspettavi? Cosa cambia se togli `instance_relative_config=True`? Rimuovi il print quando hai capito.

Salva con `Ctrl+S`.

### 2.1 Lettura riga per riga

Usa questa sezione per verificare le scelte che hai fatto nello scheletro, non come fonte da cui copiare.

**`from __future__ import annotations`**  
Permette di usare `dict | None` nelle type annotation anche su Python 3.9. Buona abitudine da mettere sempre nei file nuovi.

**`Flask(__name__, instance_relative_config=True)`**  
- `__name__` dice a Flask dove si trova il pacchetto, per trovare template e file statici.  
- `instance_relative_config=True` fa sì che i path di configurazione siano relativi alla cartella `instance/` invece che alla radice del pacchetto. Questo separa il codice (versionato) dai dati locali (non versionati).

**`app.config.from_mapping(...)`**  
Imposta i valori di default. Ogni chiave è una stringa maiuscola — è la convenzione Flask.

| Chiave | Valore di default | Significato |
|---|---|---|
| `SECRET_KEY` | `"dev"` | Chiave per firmare le sessioni. In produzione deve essere un valore casuale lungo e segreto. |
| `DATABASE` | `instance/raglite.sqlite` | Path assoluto del file SQLite. |

> **Nota:** `SECRET_KEY = "dev"` è adatto solo allo sviluppo locale. In produzione si imposta in `instance/config.py` con un valore generato da `python -c "import secrets; print(secrets.token_hex())"`.

**`app.config.from_pyfile("config.py", silent=True)`**  
Carica `instance/config.py` se esiste, sovrascrivendo i default. `silent=True` significa che se il file non esiste, non viene sollevato un errore — è opzionale per design.

**`app.config.update(test_config)`**  
Nei test, invece del file, usiamo un dizionario passato direttamente. Questo consente a ciascun test di avere una configurazione diversa senza toccare il filesystem.

**`os.makedirs(app.instance_path, exist_ok=True)`**  
Crea la cartella `instance/` se non esiste. SQLite non può creare il file `.sqlite` se la cartella padre non esiste.

**`from . import rag` e `app.register_blueprint(rag.bp)`**  
Importa il modulo `rag` (che creeremo tra poco) e registra il suo Blueprint sull'app. L'import è dentro la funzione per evitare import circolari — quando Python esegue questa riga, `create_app` è già definita.

---

## Parte 3 — I Blueprint (15 min)

### 3.1 Cos'è un Blueprint

Un **Blueprint** è un modo per organizzare un gruppo di route, template e file statici come un'unità separata, da registrare poi sull'app principale.

Senza Blueprint, tutte le route stanno in `__init__.py` o in un unico file gigante. Con Blueprint, puoi scrivere:

```
raglite/
  rag.py      ← Blueprint con le route /api/...
  auth.py     ← Blueprint con le route /login, /logout  (se servisse)
```

Ogni Blueprint ha un nome (`"rag"`), un `__name__` per trovare i suoi template, e una lista di route. Viene "montato" sull'app con `app.register_blueprint()`.

> **Semplificazione adottata in questo progetto:** usiamo un unico Blueprint (`rag`) per tutte le route. In un progetto con aree funzionali molto diverse (es. autenticazione separata, API pubblica separata) si userebbero più Blueprint con prefix URL distinti.

### 3.2 Creare `raglite/rag.py`

Crea il file `raglite/rag.py` in VSCode. Implementa il Blueprint partendo da questo scheletro:

```python
"""Blueprint con le route dell'applicazione RAGlite."""

from __future__ import annotations

from flask import Blueprint, jsonify

bp = Blueprint(???, __name__)  # TODO: dai un nome al blueprint (sarà il prefisso in url_for)


@bp.???(???)  # TODO: scegli il decoratore HTTP e l'URL dell'endpoint (vedi "Risultati attesi")
def health():
    """Endpoint di verifica: l'app è in piedi?"""
    return ???({"ok": True, "version": "stub"})  # TODO: usa la funzione Flask che serializza in JSON
```

Salva con `Ctrl+S`.

**Cosa succede riga per riga:**

`bp = Blueprint("rag", __name__)`  
Crea il Blueprint. Il primo argomento (`"rag"`) è il nome interno — deve essere unico nell'app. Serve a Flask per costruire i nomi delle route: `url_for("rag.health")`.

`@bp.get("/api/health")`  
Registra la funzione `health` come handler per le richieste `GET /api/health`. `@bp.get(...)` è equivalente a `@bp.route(..., methods=["GET"])`, più conciso.

`jsonify({"ok": True, "version": "stub"})`  
Costruisce una risposta HTTP con `Content-Type: application/json` e serializza il dizionario Python in JSON.  
Il campo `"version": "stub"` segnala esplicitamente che questo endpoint non è ancora completo — lo aggiorneremo nelle prossime lezioni man mano che aggiungiamo funzionalità reali.

---

## Parte 4 — Avviare il server e testare l'endpoint (20 min)

### 4.1 Avviare Flask in modalità debug

Nel terminale integrato di VSCode (con `.venv` attivo):

```bash
flask --app raglite run --debug
```

Output atteso:
```
 * Serving Flask app 'raglite'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Restarting with stat
 * Debugger is active!
```

- `--app raglite` dice a Flask di cercare `create_app` nel pacchetto `raglite`.
- `--debug` attiva due cose: il **reloader** (il server si riavvia automaticamente quando salvi un file) e il **debugger interattivo** (mostra stacktrace nel browser in caso di errore).

> **Il server occupa il terminale.** Per eseguire altri comandi mentre il server gira, apri un secondo terminale con `Ctrl+Shift+5` (o dal menu **Terminale → Nuovo terminale**).

### 4.2 Testare con curl

In un secondo terminale:

```bash
curl -s http://127.0.0.1:5000/api/health
```

Risposta attesa:
```json
{"ok":true,"version":"stub"}
```

**Approfondimento su `url_for`:** apri una shell Flask in un secondo terminale:

```bash
flask --app raglite shell
```

Poi esegui:

```python
print(app.url_map)
```

Con quale nome è registrata la route `GET /api/health`? Perché compare un prefisso prima di `health`? Questo risponde alla domanda 3 del checkpoint della Parte 1.

### 4.3 Testare con l'estensione REST Client (opzionale, consigliato)

Installa l'estensione **REST Client** di Huachao Mao dal Marketplace di VSCode.  
Crea il file `requests.http` nella cartella radice del progetto:

```http
### Health check
GET http://127.0.0.1:5000/api/health
```

Salva il file. Sopra la riga `GET` appare il link **Send Request** — cliccalo.  
La risposta appare in un pannello laterale con status, header e body.

Userai questo file per testare tutti gli endpoint man mano che li costruisci.  
Aggiungilo al repository — è documentazione eseguibile.

> **Challenge (opzionale):** aggiungi nello stesso Blueprint un secondo endpoint `GET /api/version` che legge la versione del pacchetto con `importlib.metadata.version("raglite")` e la restituisce come JSON, ad esempio `{"version": "0.1.0"}`. Aggiungi la richiesta corrispondente in `requests.http` e testala con **Send Request**. Come verifichi già a questo punto — senza avviare il server — che l'endpoint sia registrato sul Blueprint corretto?

### 4.4 Verificare il reload automatico e diagnosticare un errore

**Esperimento 1 — errore programmato:** prima di toccare il codice del health check, fai questa prova. In `__init__.py` commenta la riga `app.register_blueprint(rag.bp)` e salva. Il server si ricarica automaticamente. Ora esegui:

```bash
curl -s http://127.0.0.1:5000/api/health
```

Cosa risponde Flask? Qual è lo status HTTP? Leggi il messaggio di errore: cosa ti dice esattamente? Ripristina la riga (togli il commento) e verifica che l'endpoint torni a rispondere correttamente.

**Esperimento 2 — reload in azione:** con il server in esecuzione e l'endpoint funzionante, apri `raglite/rag.py` e modifica la risposta:

```python
return jsonify({"ok": True, "version": "stub", "test": "reload"})
```

Salva con `Ctrl+S`. Nel terminale del server vedrai:

```
 * Detected change in '.../rag.py', reloading
 * Restarting with stat
```

Ripeti il `curl` o la richiesta da REST Client — la risposta ora include `"test": "reload"`.

Rimuovi il campo `"test"` e salva di nuovo. Hai visto il ciclo completo: modifica → salva → il server si aggiorna da solo, senza doverlo riavviare manualmente.

---

## Parte 5 — Commit e push (10 min)

Ferma il server con `Ctrl+C` nel terminale dove è in esecuzione.

Aggiungi il file `requests.http` a `.gitignore` oppure tienilo — entrambe le scelte sono valide. In questo corso lo teniamo nel repository perché documenta come usare le API.

Assicurati che `instance/` sia nel `.gitignore` — contiene il database locale e non deve essere versionata:

```bash
grep -q "instance/" .gitignore || echo "instance/" >> .gitignore
```

Verifica le modifiche:

```bash
git status
```

Dovresti vedere `raglite/__init__.py` e `raglite/rag.py` come file modificati, e `requests.http` come nuovo file untracked.

**Prima di procedere, rispondi senza guardare il codice:**

1. Descrivi il flusso completo da `flask --app raglite run` fino all'esecuzione di `health()`: quanti file entrano in gioco e in che ordine?
2. Se dovessi aggiungere un Blueprint `auth` con route `/login`, dove lo creeresti e quali due righe dovresti aggiungere in `__init__.py`?
3. Cosa restituisce `url_for("rag.health")`? E `url_for("health")`? Perché il comportamento è diverso?

Staging interattivo:

```bash
git add -p
```

Scorri le modifiche con `y` per includerle. Poi aggiungi il file nuovo:

```bash
git add requests.http
```

Commit:

```bash
git commit -m "feat: flask app factory and health endpoint stub"
```

Push:

```bash
git push
```

Vai su GitHub e verifica che i due file Python siano aggiornati e il commit sia visibile.

---

## Verifica finale (5 min)

```bash
# Il server si avvia senza errori?
flask --app raglite run --debug
# atteso: "Running on http://127.0.0.1:5000"

# (secondo terminale) L'endpoint risponde?
curl -s http://127.0.0.1:5000/api/health
# atteso: {"ok":true,"version":"stub"}

# Il pacchetto è importabile senza avviare il server?
python -c "from raglite import create_app; app = create_app(); print(app.name)"
# atteso: raglite
```

---

## Possibili problemi e soluzioni

| Problema | Causa probabile | Soluzione |
|---|---|---|
| `flask: command not found` | Ambiente virtuale non attivo | `source .venv/bin/activate` |
| `Error: Could not locate a Flask application` | `create_app` non definita o typo nel nome del pacchetto | Verifica che `raglite/__init__.py` definisca `create_app` |
| `ImportError: cannot import name 'bp' from 'raglite.rag'` | `rag.py` non contiene `bp` oppure ha un errore di sintassi | Controlla `raglite/rag.py`; esegui `python -c "from raglite import rag"` per vedere l'errore preciso |
| `Address already in use` | Un altro processo usa la porta 5000 | `lsof -i :5000` per trovare il processo; oppure `flask run --port 5001` |
| Il reload non funziona | `--debug` non specificato | Assicurati di usare `flask run --debug`, non solo `flask run` |
| `curl` restituisce HTML invece di JSON | Stai chiamando un URL sbagliato | Verifica di usare `/api/health`, non solo `/` |

---

## Struttura del progetto al termine di questa lezione

```
raglite/
  raglite/
    __init__.py     ← create_app() — MODIFICATO
    rag.py          ← Blueprint bp, GET /api/health — NUOVO
    templates/
    static/
  tests/
    __init__.py
  instance/         ← esclusa da git
  requests.http     ← NUOVO
  .gitignore
  pyproject.toml
  README.md
```

---

*Nella prossima lezione aggiungerai il database SQLite: schema, connessione con `flask.g`, comando CLI `init-db`, e il primo endpoint con dati reali.*
