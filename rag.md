# Introduzione agli LLM e ai Database Vettoriali

## Un esempio completo con RAG (Retrieval-Augmented Generation)


# 1. Obiettivi

Comprendere:

- Cos'è un **LLM**
- Cos'è un **embedding**
- Cos'è un **database vettoriale**
- Cos'è il **RAG**
- Come questi componenti si integrano in un sistema reale


# 2. Il Problema di Partenza

Immaginiamo di avere un documento interno:

```

Acme VPN Policy (v1)
Employees must use the corporate VPN for remote access.
VPN access requires multi-factor authentication (MFA).
If MFA is unavailable, employees must contact IT for a temporary access code.
Temporary codes expire after 24 hours.

```

Domanda dell’utente:

> What should I do if MFA is unavailable?

Vogliamo che il sistema:
- risponda correttamente
- usi SOLO il documento fornito
- mostri quali parti del documento ha utilizzato


# 3. Cos’è un LLM?

Un **Large Language Model (LLM)** è un modello statistico che:

> Dato un testo in input, predice il testo più probabile che dovrebbe seguire.

Esempio:

Input:
```

If MFA is unavailable, the employee must...

```

Output:
```

...contact IT to obtain a temporary access code.

```

⚠️ Importante:  
Un LLM NON conosce i tuoi documenti privati.  
Genera testo plausibile basato sull’addestramento generale.

Senza controllo può:
- inventare informazioni
- rispondere in modo impreciso

Questo fenomeno si chiama **hallucination**.


# 4. Il Limite dell’LLM Puro

Se chiediamo:

> What should I do if MFA is unavailable?

Senza fornire il documento, il modello potrebbe:
- indovinare
- rispondere in modo generico
- fornire informazioni errate

Serve un meccanismo per:

- collegare il modello ai nostri documenti
- controllare le fonti
- rendere il sistema verificabile

Qui entra in gioco il RAG.


# 5. Cos’è il RAG

RAG significa:

> Retrieval-Augmented Generation  
> Generazione aumentata da recupero

Il processo è composto da due fasi:

1. **Retrieval** → Recupero delle parti rilevanti del documento
2. **Generation** → Generazione della risposta usando solo quel contesto


# 6/7. Come Funziona il Retrieval?

Qui entra in gioco il concetto di embedding.

Un embedding è:

> Una rappresentazione numerica di un testo.

Ad esempio, la frase:

```

Temporary codes expire after 24 hours.

```

diventa un vettore numerico:

```

[-0.012, 0.044, -0.003, 0.091, ...]

```

Questo vettore ha molte dimensioni (es. 384).

Frasi con significato simile avranno vettori vicini tra loro.

Esempio:

"Temporary codes last one day." → vettore molto simile.


# 8. Cos’è un Database Vettoriale?

Un database vettoriale:

- salva vettori numerici
- permette di cercare i vettori più simili a uno dato

Non è una ricerca per parola chiave.
È una ricerca per **somiglianza semantica**.


# 9. Fase 1: Indicizzazione del Documento

## Step 1 — Chunking

Il documento viene diviso in parti (chunk):

Chunk 0:
```

Employees must use the corporate VPN...

```

Chunk 1:
```

VPN access requires MFA.
If MFA is unavailable, employees must contact IT...

```

Chunk 2:
```

Temporary codes expire after 24 hours.

```


## Step 2 — Embedding

Per ogni chunk calcoliamo un embedding.

Salviamo nel database:

| chunk_id | testo | vettore |
|----------|-------|---------|
| 101 | chunk 0 | [ ... ] |
| 102 | chunk 1 | [ ... ] |
| 103 | chunk 2 | [ ... ] |

In questa fase NON viene usato l’LLM generativo.


# 10. Fase 2: Query dell’Utente

Domanda:

> What should I do if MFA is unavailable?


## Step 1 — Embedding della domanda

La domanda viene trasformata in un vettore.


## Step 2 — Similarità Coseno

Confrontiamo il vettore della domanda con tutti i vettori dei chunk.

La similarità coseno misura:

> Quanto due vettori puntano nella stessa direzione.

Valori:
- 1 → identici
- 0 → non correlati
- -1 → opposti

Esempio di risultati:

| chunk_id | score |
|----------|-------|
| 101 | 0.21 |
| 102 | 0.87 |
| 103 | 0.34 |

Il chunk 102 è il più rilevante.


# 11. Retrieval-Only (Senza LLM)

Il sistema potrebbe fermarsi qui e restituire:

```

Relevant passage:
If MFA is unavailable, employees must contact IT...

```

Questo è già utile.
È solo matematica + ricerca semantica.


# 12. Fase 3: Generazione (LLM)

Costruiamo un prompt:

```

Answer using ONLY the context below.

CONTEXT:
If MFA is unavailable, employees must contact IT for a temporary access code.
Temporary codes expire after 24 hours.

QUESTION:
What should I do if MFA is unavailable?

````

L’LLM genera:

> If MFA is unavailable, contact IT to obtain a temporary access code. Temporary codes expire after 24 hours.


# 13. Output Finale del Sistema

Il sistema restituisce:

```json
{
  "answer": "If MFA is unavailable, contact IT...",
  "contexts": [
    {
      "chunk_id": 102,
      "score": 0.87,
      "text": "If MFA is unavailable..."
    },
    {
      "chunk_id": 103,
      "score": 0.34,
      "text": "Temporary codes expire..."
    }
  ]
}
````

Quindi il sistema produce:

* Risposta generata
* Evidenze usate
* Punteggi di similarità
* Tracciabilità completa


# 14. Perché Separare Retrieval e Generation?

| Retrieval      | Generation      |
| -------------- | --------------- |
| Deterministico | Probabilistico  |
| Riproducibile  | Variabile       |
| Economico      | Più costoso     |
| Spiegabile     | Meno spiegabile |

Questa separazione è il cuore dei sistemi LLM moderni.


# 15. Vantaggi del RAG

* Riduce le hallucination
* Permette audit e tracciabilità
* Usa documenti aggiornabili
* Separa conoscenza dai pesi del modello


# 16. Architettura Complessiva

```
Documento
   ↓
Chunking
   ↓
Embedding
   ↓
Database vettoriale
   ↓
Query utente
   ↓
Similarità coseno
   ↓
Top-K chunk
   ↓
Prompt LLM
   ↓
Risposta
```


# 17. Concetti Appresi

Questa architettura introduce:

* REST API
* server → server calls
* pipeline di elaborazione
* spazio vettoriale
* similarità coseno
* controllo hallucination
* auditabilità


# 18. Conclusione

Un sistema RAG è composto da:

1. Database testuale
2. Database vettoriale
3. Motore di ricerca semantica
4. LLM generativo

La qualità della risposta dipende:

* dalla qualità del retrieval
* dalla qualità del prompt
* dal controllo dei parametri di generazione


# 19. Idea Chiave Finale

L’LLM scrive.

Il database vettoriale trova.

Il RAG orchestra.

E tutto il sistema è verificabile.
