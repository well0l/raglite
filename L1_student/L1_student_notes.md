# L1 — Note di laboratorio: Flask application factory

> **Istruzioni per la consegna**
>
> 1. Copia questo file nel tuo repository nella cartella `docs/lezioni/` con il nome `L1_flask_factory.md`.
> 2. Compila ogni sezione **durante** la lezione, non a posteriori.
> 3. Scrivi con parole tue — non copiare dalla lezione o da altri. L'obiettivo è che il documento rifletta *la tua* comprensione.
> 4. Le sezioni contrassegnate con *(opzionale)* possono essere omesse se non hai completato la parte corrispondente.
> 5. Fai il commit di questo file insieme al codice della lezione:
>    ```bash
>    git add docs/lezioni/L1_flask_factory.md
>    git commit -m "docs: note di laboratorio L1"
>    git push
>    ```

---

## Informazioni

| | |
|---|---|
| **Nome** | |
| **Data** | |
| **Commit del codice** | *(link GitHub al commit con `__init__.py` e `rag.py`)* |

---

## Checkpoint — Parte 1 (prima di scrivere codice)

*Rispondi dopo aver letto la Parte 1, prima di aprire `__init__.py`.*

**1.** Nei test, ogni test chiama esplicitamente `create_app()`. Le due istanze di app condividono stato? Cosa succederebbe invece con l'approccio globale?

> *La tua risposta:*

**2.** Nell'approccio globale, `db.py` importa `app` da `__init__.py` e `__init__.py` importa `db.py`. Dove si forma il ciclo? Perché con la factory non si forma?

> *La tua risposta (puoi usare uno schema testuale):*

**3.** `flask --app raglite run` trova `create_app` automaticamente. Come fa Flask a sapere dove cercarla?

> *La tua risposta:*

---

## Parte 2 — Verifica `instance_path`

*Dopo aver aggiunto temporaneamente `print(app.instance_path)` e avviato il server:*

**Path stampato a runtime:**

```
(incolla qui l'output del print)
```

**Cosa cambia se rimuovi `instance_relative_config=True`?**

> *La tua risposta:*

---

## Parte 4 — Esplorazione `url_map`

*Dopo aver eseguito `print(app.url_map)` nella shell Flask:*

**Output di `app.url_map`:**

```
(incolla qui l'output)
```

**Con quale nome è registrata la route `GET /api/health`? Perché compare un prefisso?**

> *La tua risposta:*

---

## Parte 4 — Errore programmato: `register_blueprint` commentato

*Dopo aver commentato `app.register_blueprint(rag.bp)` e chiamato l'endpoint:*

**Status HTTP restituito da curl:**

```
(es. HTTP 404)
```

**Messaggio di Flask:**

```
(incolla qui l'output di curl -s)
```

**In una riga: cosa stava mancando e perché Flask non sapeva gestire la richiesta?**

> *La tua risposta:*

---

## Auto-verifica pre-commit

*Rispondi senza guardare il codice, prima di eseguire `git add`.*

**1.** Descrivi il flusso completo da `flask --app raglite run` fino all'esecuzione di `health()`: quanti file entrano in gioco e in che ordine?

> *La tua risposta:*

**2.** Se dovessi aggiungere un Blueprint `auth` con route `/login`, dove lo creeresti e quali due righe dovresti aggiungere in `__init__.py`?

> *La tua risposta:*

**3.** Cosa restituisce `url_for("rag.health")`? E `url_for("health")`? Perché il comportamento è diverso?

> *La tua risposta:*

---

## Challenge *(opzionale)*

*Compila questa sezione solo se hai implementato `GET /api/version`.*

**Implementazione aggiunta a `rag.py`:**

```python
# incolla qui il codice del nuovo endpoint
```

**Come hai verificato che fosse registrato sul Blueprint corretto senza avviare il server?**

> *La tua risposta:*

---

## Note libere

*Difficoltà incontrate, errori inaspettati, domande aperte, osservazioni personali.*

>
