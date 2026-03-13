# Setup: ambiente di sviluppo, pyproject.toml, Git e GitHub

| | |
|---|---|
| **Durata** | 100 minuti |
| **Prerequisiti** | Account GitHub già creato e configurato (nome utente, email, SSH key o token HTTPS) |
| **Ambiente** | PC con WSL2 installato |

---

## Risultati attesi

Al termine di questa lezione:

1. Avrai **VSCode aperto direttamente in WSL** e un progetto Python con struttura professionale.
2. Avrai scritto un file `pyproject.toml` che descrive il pacchetto `raglite` e le sue dipendenze.
3. Avrai un ambiente virtuale `.venv` attivo e il pacchetto installato in modalità *editable* (`pip install -e .`): potrai modificare il codice sorgente e vedere le modifiche attive immediatamente, senza reinstallare.
4. Avrai un file `.gitignore` che esclude correttamente i file generati.
5. Avrai un **repository GitHub** chiamato `raglite` con il codice già caricato.
6. Vedrai un primo commit visibile su GitHub con il messaggio `Initial commit`.

Alla fine della lezione, eseguendo i seguenti comandi nel terminale, tutto deve funzionare senza errori:

```bash
# Verifica Python
python --version              # Python 3.10 o superiore

# Verifica installazione pacchetto
python -c "import raglite; print('ok')"

# Verifica git
git log --oneline             # mostra: <hash> Initial commit

# Verifica GitHub
git remote -v                 # mostra l'URL del repository remoto
```

---

## Parte 1 — WSL e VSCode (15 min)

### 1.1 Aprire il terminale WSL

1. Premi `Win + R`, digita `wsl`, premi Invio.
   Si apre una finestra con il prompt della shell Linux, simile a:
   ```
   user@PC:~$
   ```

2. Verifica che Python sia disponibile:
   ```bash
   python3 --version
   ```
   Il risultato deve essere `Python 3.10.x` o superiore.
   Se il comando non esiste, chiama il docente.

3. Verifica che git sia disponibile:
   ```bash
   git --version
   ```
   Risultato atteso: `git version 2.x.x`.

### 1.2 Aprire VSCode in WSL

1. Nel terminale WSL, crea la cartella dove vivranno tutti i progetti del corso:
   ```bash
   mkdir -p ~/code
   cd ~/code
   ```

2. Crea la cartella del progetto:
   ```bash
   mkdir raglite
   cd raglite
   ```

3. Apri VSCode **dalla shell WSL** — questo passaggio è fondamentale.
   Se apri VSCode da Windows, il progetto girerà su Windows e perderai l'integrazione con l'ambiente Linux:
   ```bash
   code .
   ```
   VSCode si apre con la scritta **WSL: Ubuntu** (o simile) nell'angolo in basso a sinistra della barra di stato.
   Se compare una notifica *"Install WSL extension"*, accetta e riavvia VSCode.

### 1.3 Aprire il terminale integrato in VSCode

Usa il menu **Visualizza → Terminale**.

> **Nota per tastiera italiana:** la combinazione standard `Ctrl+backtick` di VSCode non è accessibile su layout italiano perché il backtick richiede `AltGr`. Usa il menu oppure, una volta in VSCode, vai in **File → Preferenze → Scelte rapide da tastiera**, cerca `workbench.action.terminal.toggleTerminal` e assegna una combinazione comoda (es. `Ctrl+Shift+T`).

Si apre un pannello in basso con un terminale già posizionato in `~/code/raglite` dentro WSL.
**Userai sempre questo terminale** per il resto della lezione — non il terminale Windows separato aperto prima.

---

## Parte 2 — Struttura del progetto (10 min)

Tutti i comandi da qui in avanti si eseguono nel terminale integrato di VSCode.

### 2.1 Creare le cartelle

```bash
mkdir -p raglite/templates raglite/static tests instance
```

Questo crea la seguente struttura:

```
raglite/          ← cartella radice del progetto (repository git)
  raglite/        ← pacchetto Python (stesso nome della radice, è una convenzione comune)
    templates/    ← template HTML Jinja2 (li scriveremo nelle lezioni sul frontend)
    static/       ← CSS e JavaScript (li scriveremo nelle lezioni sul frontend)
  tests/          ← test automatizzati pytest
  instance/       ← dati locali: DB SQLite e configurazione privata — NON va su Git
```

> **Perché due cartelle `raglite/`?** La cartella esterna è il *repository*: contiene tutto il progetto (codice, test, configurazione, documentazione). La cartella interna è il *pacchetto Python*: contiene solo il codice importabile. È una convenzione consolidata; evita ambiguità quando `pip` installa il pacchetto.

### 2.2 Creare i file Python iniziali (placeholder)

```bash
touch raglite/__init__.py
touch tests/__init__.py
```

`__init__.py` rende `raglite/` un **pacchetto Python importabile**: senza di esso, `import raglite` fallirebbe.
Per ora è vuoto — lo riempiremo nella prossima lezione.

---

## Parte 3 — `pyproject.toml` (15 min)

### 3.1 Cos'è `pyproject.toml`

È il file standard moderno (PEP 517/518) che descrive il progetto Python:
nome, versione, dipendenze, strumento di build. Sostituisce il vecchio `setup.py`.

Quando esegui `pip install -e .` (o quando qualcuno installa il tuo pacchetto), pip legge questo file per sapere cosa installare e come costruire il pacchetto.

### 3.2 Creare il file

In VSCode apri il pannello Explorer con `Ctrl+Shift+E`.
Fai clic destro sulla cartella radice `raglite` → **New File** → digita `pyproject.toml`.

Incolla il seguente contenuto:

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "raglite"
version = "0.1.0"
description = "RAG application with Flask and SQLite"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
  "flask>=3.0",
  "numpy>=1.26",
  "httpx>=0.28",
]

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[tool.setuptools.packages.find]
include = ["raglite*"]
namespaces = false

[tool.pytest.ini_options]
testpaths = ["tests"]
```

Salva con `Ctrl+S`.

### 3.3 Lettura guidata

| Sezione | Significato |
|---|---|
| `[build-system]` | Usa `setuptools` per costruire il pacchetto distribuibile; richiesto da `pip install` |
| `[project]` | Metadati: nome, versione, dipendenze obbligatorie |
| `dependencies` | Flask (web framework), numpy (algebra lineare per i vettori), httpx (client HTTP) |
| `[project.optional-dependencies]` | `pip install -e ".[dev]"` installa anche pytest — non serve in produzione |
| `[tool.setuptools.packages.find]` | Individua automaticamente il pacchetto `raglite/` senza elencarlo a mano |
| `[tool.pytest.ini_options]` | Dice a pytest dove cercare i test, così `pytest` funziona senza argomenti |

---

## Parte 4 — Ambiente virtuale e installazione (10 min)

### 4.1 Creare l'ambiente virtuale

```bash
python3 -m venv .venv
```

Questo crea la cartella `.venv/` con un interprete Python e una copia di `pip` completamente isolati dal sistema.

> **Perché un ambiente virtuale?**
> Ogni progetto può richiedere versioni diverse delle stesse librerie. Senza isolamento, installare `flask 3.0` per un progetto potrebbe rompere un altro progetto che usa `flask 2.x`. L'ambiente virtuale risolve il problema: ogni progetto ha il suo spazio separato.

### 4.2 Attivare l'ambiente

```bash
source .venv/bin/activate
```

Il prompt cambia e mostra `(.venv)` all'inizio — è il segnale visivo che l'ambiente è attivo:
```
(.venv) user@PC:~/code/raglite$
```

Da questo momento, `python` e `pip` puntano all'ambiente isolato, non al Python di sistema.

> **Nota:** l'ambiente va **riattivato ogni volta** che si apre un nuovo terminale.
> Per automatizzarlo in VSCode: apri il Command Palette con `Ctrl+Shift+P` → digita `Python: Select Interpreter` → scegli `.venv`.
> Ogni nuovo terminale aperto da VSCode lo attiverà automaticamente.

### 4.3 Installare il pacchetto in modalità editable

```bash
pip install -e ".[dev]"
```

**Cosa significa `-e` (editable) e perché è importante per lo sviluppo?**

Con una normale installazione (`pip install .`), pip *copia* i file del pacchetto in `.venv/lib/python3.x/site-packages/raglite/`. Se poi modifichi il codice sorgente in `raglite/`, Python continua a usare la copia vecchia — devi reinstallare ad ogni modifica.

Con `-e`, pip non copia nulla: registra un collegamento diretto alla tua cartella sorgente. Ogni volta che esegui `import raglite`, Python legge i file in `raglite/` così come sono sul disco *in quel momento*. Puoi modificare il codice e i cambiamenti sono immediatamente visibili, senza nessuna reinstallazione.

Questo è il modo standard di lavorare su un pacchetto Python durante lo sviluppo.

`[dev]` attiva le dipendenze opzionali definite in `[project.optional-dependencies]`, installando anche `pytest`.

> **Semplificazione adottata in questo progetto:** gestiamo un unico ambiente con tutte le dipendenze insieme. In un progetto con più componenti separati (es. frontend e backend come pacchetti distinti, oppure deployment via container) la gestione degli ambienti diventa più articolata.

Verifica l'installazione:
```bash
python -c "import raglite; print('Pacchetto importabile correttamente')"
```

---

## Parte 5 — `README.md` e `.gitignore` (10 min)

### 5.1 README

Crea il file `README.md` nella cartella radice. Per ora è una descrizione essenziale — la amplieremo man mano che il progetto cresce:

```markdown
# RAGlite

Applicazione RAG (Retrieval-Augmented Generation) costruita con
Flask, SQLite e numpy.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```
```

> Il blocco di codice nel README va chiuso con tre backtick su una riga a sé.

### 5.2 `.gitignore`

Crea il file `.gitignore` nella cartella radice. Questo file dice a git quali file e cartelle ignorare completamente:

```gitignore
# Ambiente virtuale Python
.venv/

# Dati locali (DB SQLite e configurazione privata con eventuali token)
instance/

# File compilati Python — generati automaticamente, non fanno parte del codice
__pycache__/
*.pyc
*.pyo
*.pyd

# Metadati del pacchetto generati da pip install -e .
*.egg-info/
dist/
build/

# Impostazioni editor (opzionale — alcuni preferiscono versionarle)
.vscode/

# Variabili d'ambiente con segreti
.env
```

Salva con `Ctrl+S`.

**Perché `instance/` è in `.gitignore`?**
La cartella `instance/` conterrà il database SQLite con i dati dell'applicazione e un file `config.py` che potrà includere token API e chiavi segrete. Questi file non devono mai finire su un repository pubblico — e nemmeno su uno privato condiviso con persone non autorizzate. Una volta caricati su GitHub, rimuoverli dalla *storia* git è possibile ma complesso. Escluderli dal controllo versione fin dall'inizio è la soluzione corretta.

---

## Parte 6 — Git locale: primo commit (15 min)

### 6.1 Inizializzare il repository

```bash
git init
```

Output:
```
Initialized empty Git repository in ~/code/raglite/.git/
```

La cartella nascosta `.git/` è il cuore del repository: contiene tutta la storia dei commit, la configurazione e gli oggetti interni di git. Non toccarla mai manualmente.

### 6.2 Configurare la propria identità (solo se non già fatto)

Git richiede nome e email per firmare ogni commit. Se non li hai ancora configurati:

```bash
git config --global user.name "Nome Cognome"
git config --global user.email "tua@email.com"
```

`--global` scrive la configurazione in `~/.gitconfig`: vale per tutti i repository sul tuo sistema.

### 6.3 Verificare cosa git vede

```bash
git status
```

Vedrai i file *Untracked* elencati in rosso. Nota che `.venv/` e `instance/` **non compaiono** — git le ignora grazie a `.gitignore`.

### 6.4 Aggiungere i file all'area di staging

```bash
git add .
```

Poi verifica di nuovo:
```bash
git status
```

I file ora compaiono in verde sotto *"Changes to be committed"*: sono nell'**area di staging**, pronti per essere inclusi nel prossimo commit.

> **Staging area:** git distingue tra "ho modificato questi file" e "voglio includere queste modifiche nel prossimo commit". L'area di staging è lo spazio intermedio dove raccogli esattamente le modifiche da salvare. Nelle lezioni successive userai `git add -p` per gestirla in modo più preciso.

### 6.5 Primo commit

```bash
git commit -m "Initial commit"
```

Output simile a:
```
[main (root-commit) abc1234] Initial commit
 6 files changed, ...
```

Visualizza la storia dei commit:
```bash
git log --oneline
```

Vedrai una sola riga: `abc1234 Initial commit`. Ogni commit futuro apparirà in questa lista — è la storia completa del progetto.

---

## Parte 7 — GitHub: creare il repository e fare il push (15 min)

### 7.1 Creare il repository su GitHub

1. Apri [github.com](https://github.com) nel browser e accedi al tuo account.
2. Clicca **"+"** in alto a destra → **"New repository"**.
3. Compila il modulo:
   - **Repository name:** `raglite`
   - **Description:** `RAG application — corso Flask`
   - **Visibility:** Public o Private, a tua scelta
   - **⚠️ NON spuntare** nessuna delle opzioni aggiuntive (*Add a README file*, *Add .gitignore*, *Choose a license*) — il repository deve essere **completamente vuoto**, altrimenti il push fallirà per conflitti di storia.
4. Clicca **"Create repository"**.

### 7.2 Collegare il repository locale a GitHub

GitHub ti mostrerà una pagina con le istruzioni. Copia l'URL HTTPS del repository, nella forma `https://github.com/tuonome/raglite.git`.

Nel terminale VSCode aggiungi il remote:
```bash
git remote add origin https://github.com/TUONOME/raglite.git
```

Sostituisci `TUONOME` con il tuo nome utente GitHub.

Verifica:
```bash
git remote -v
```

Output atteso:
```
origin  https://github.com/TUONOME/raglite.git (fetch)
origin  https://github.com/TUONOME/raglite.git (push)
```

**Cos'è `origin`?** È il nome convenzionale del repository remoto principale. Tecnicamente potresti chiamarlo in altro modo, ma `origin` è lo standard de facto e tutti i tool git lo assumono come nome di default.

### 7.3 Rinominare il branch e fare il push

```bash
git branch -M main
git push -u origin main
```

- `git branch -M main` rinomina il branch corrente in `main` (GitHub usa `main` come nome predefinito per i nuovi repository).
- `-u` collega il branch locale `main` al remoto `origin/main`: da ora in avanti basterà `git push` senza argomenti.

Git potrebbe chiederti le credenziali GitHub (username e Personal Access Token).

### 7.4 Verifica su GitHub

Apri `https://github.com/TUONOME/raglite` nel browser.
Dovresti vedere tutti i file del progetto e il commit "Initial commit".
Clicca sul nome del commit per vedere esattamente quali file sono stati inclusi e le loro differenze.

---

## Parte 8 — Il flusso git che userai ad ogni lezione (10 min)

Ogni lezione termina con un **commit e un push**. Questo flusso diventerà un'abitudine:

```bash
# 1. Vedere cosa è cambiato rispetto all'ultimo commit
git status

# 2. Aggiungere i file modificati in modo interattivo
git add -p

# 3. Committare con un messaggio descrittivo
git commit -m "feat: descrizione di cosa hai aggiunto"

# 4. Inviare su GitHub
git push
```

### `git add -p` — staging interattivo

`git add .` aggiunge tutto indiscriminatamente. `git add -p` (patch mode) ti mostra ogni blocco di modifiche uno per uno e ti chiede cosa fare:

```
Stage this hunk [y,n,q,a,d,/,e,?]?
```

| Tasto | Significato |
|---|---|
| `y` | Sì, includi questa modifica nel commit |
| `n` | No, salta questa modifica |
| `q` | Esci dallo staging interattivo |
| `?` | Mostra la lista completa dei comandi |

Usare `git add -p` ti costringe a **leggere ogni riga che stai committando**. È una buona abitudine: evita di includere per errore debug print, segreti lasciati in un commento, o modifiche non correlate al commit corrente.

### Convenzione per i messaggi di commit

Usiamo un prefisso che indica la natura della modifica:

| Prefisso | Quando usarlo |
|---|---|
| `feat:` | nuova funzionalità |
| `fix:` | correzione di un bug |
| `test:` | aggiunta o modifica di test |
| `docs:` | documentazione |
| `refactor:` | riscrittura senza cambiare il comportamento |

Esempi:
```
feat: flask app factory
feat: chunking and ingest with mock embed
fix: handle empty text in chunk_text
test: smoke suite for ingest and query
```

Questi prefissi seguono la convenzione [Conventional Commits](https://www.conventionalcommits.org/), adottata da moltissimi progetti open source.

---

## Verifica finale (5 min)

Esegui questi comandi nell'ordine. Tutti devono completare senza errori:

```bash
# 1. Ambiente virtuale attivo?
which python
# atteso: .../raglite/.venv/bin/python

# 2. Pacchetto importabile?
python -c "import raglite; print('ok')"
# atteso: ok

# 3. Dipendenze installate?
python -c "import flask, numpy, httpx; print('deps ok')"
# atteso: deps ok

# 4. Git configurato?
git log --oneline
# atteso: <hash> Initial commit

# 5. Connesso a GitHub?
git remote -v
# atteso: origin  https://github.com/... (fetch) e (push)
```

---

## Possibili problemi e soluzioni

| Problema | Causa probabile | Soluzione |
|---|---|---|
| `python3: command not found` | Python non installato in WSL | `sudo apt update && sudo apt install python3 python3-venv` |
| `code .` non apre VSCode | Estensione WSL non installata o `code` non nel PATH | Installa l'estensione "WSL" da VSCode Marketplace, poi riavvia VSCode da Windows |
| `python -c "import raglite"` → `ModuleNotFoundError` | Ambiente virtuale non attivo o `pip install -e .` non eseguito | `source .venv/bin/activate` poi `pip install -e ".[dev]"` |
| `git push` → errore di autenticazione | Token GitHub scaduto o SSH non configurato | Genera un nuovo Personal Access Token su GitHub → Settings → Developer settings |
| `.venv/` compare in `git status` | `.gitignore` non salvato o riga mancante | Verifica che `.gitignore` contenga `.venv/` e salva con `Ctrl+S` |
| `git commit` → *"Please tell me who you are"* | Identità git non configurata | `git config --global user.name "..."` e `git config --global user.email "..."` |
| `git push` → *"rejected — non-fast-forward"* | Il repository GitHub non era vuoto al momento della creazione | `git pull --rebase origin main` poi `git push` |

---

## Struttura finale del progetto

Alla fine di questa lezione la cartella `~/code/raglite` deve avere esattamente questa struttura:

```
raglite/                ← repository git (contiene .git/)
  raglite/              ← pacchetto Python
    __init__.py         ← file vuoto — rende la cartella importabile
    templates/          ← cartella vuota
    static/             ← cartella vuota
  tests/
    __init__.py         ← file vuoto
  instance/             ← esclusa da git (.gitignore)
  .gitignore
  pyproject.toml
  README.md
```

---

*Nella prossima lezione implementerai la **Flask application factory**, registrerai un Blueprint e creerai il primo endpoint dell'applicazione.*
