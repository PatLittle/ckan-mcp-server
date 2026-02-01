# Perché CKAN MCP Server? 🚀

Hai mai provato a cercare dati aperti e ti sei perso tra interfacce web complicate? Clicca qui, filtra là, cambia pagina, torna indietro, rifiltra... frustrante, vero?

**C'è un modo migliore**: chiedere quello che vuoi, in linguaggio naturale, e ottenere risposte precise. Come una conversazione con un amico che conosce perfettamente tutti i cataloghi dati aperti.

## Come Funziona (in Breve)

Questo strumento si integra con **la tua AI preferita** e ti permette di interrogare **qualsiasi portale CKAN** (dati.gov.it, data.gov.uk, data.gov, ecc.) usando domande normali.

Impari una volta, usi ovunque. 🌍

---

## Esempi Pratici (Dal Più Semplice al Più Potente)

### 🎯 Livello 1: La Ricerca Semplice

**Tu chiedi**: "Mostrami tutti i dataset sulla mobilità su dati.gov.it"

**Risultato**: 1.758 dataset trovati!

Invece di navigare pagine e pagine del catalogo, ottieni tutto in un colpo. Facile!

**Tool usato**: `ckan_package_search`

---

### 🔍 Livello 2: Affina la Ricerca

**Tu chiedi**: "Voglio solo dataset che hanno 'bike' o 'bici' nel titolo"

**La query usata**:

```
title:bike OR title:bici*
```

**Risultato**: 43 dataset mirati (invece di 1.758!).

Il simbolo `*` è un jolly (wildcard) che trova anche "bicicletta", "biciclette", ecc. Vedi? Già molto più preciso!

**Bonus**: "Mostrami i dettagli del primo dataset"

Ottieni:
- Titolo completo
- Descrizione
- Organizzazione che l'ha pubblicato
- Risorse disponibili (CSV, JSON, ecc.)
- Licenza
- Date di creazione e aggiornamento
- Link diretto

**Tool usati**: `ckan_package_search` + `ckan_package_show`

---

### 📊 Livello 3: Analisi Esplorativa

**Tu chiedi**: "Quali organizzazioni hanno creato più dataset negli ultimi 6 mesi su dati.gov.it?"

**Il sistema interroga** il catalogo con filtri temporali e aggregazioni.

**Risultato**: 40.072 dataset creati negli ultimi 6 mesi, con la classifica delle top 50 organizzazioni!

**Top 3**:
1. Regione Toscana: 12.602 dataset
2. Regione Veneto: 6.555 dataset
3. Regione Lombardia: 3.304 dataset

Perfetto per capire chi è più attivo nell'open data, senza scaricare nulla!

**Tool usato**: `ckan_package_search` (con faceting per aggregazioni)

---

### 🎯 Livello 4: Query Mirate (Filtri Multipli)

**Tu chiedi**: "Dataset su appalti o contratti pubblicati negli ultimi 3 mesi"

**Filtri combinati**:
- Ricerca nel titolo: `title:appalti OR title:contratti`
- Filtro temporale: ultimi 3 mesi

**Risultato**: 127 dataset trovati!

Esempio di dataset:
- **Titolo**: "Gare e appalti"
- **Organizzazione**: Comune di Bologna
- **Ultimo aggiornamento**: 2026-01-29
- **Formati**: CSV, JSON, Parquet, RDF...

Boom! 💥 Dati freschi sulla trasparenza degli appalti pubblici.

**Bonus**: "Cosa pubblica in totale il Comune di Bologna?"

Ottieni tutti i dataset pubblicati da quell'organizzazione, con statistiche complete.

**Tool usati**: `ckan_package_search` (filtri multipli) + `ckan_organization_show`

---

### 🌍 Livello 5: Stesso Approccio, Portale Diverso

**Tu chiedi**: "Stessa ricerca su bike, ma sul portale del Regno Unito (data.gov.uk)"

**La query usata**:

```
title:bike OR title:cycling
```

**Risultato**: 366 dataset!

**La parte magica**: impari a usare questo strumento una volta, poi funziona su **qualsiasi portale CKAN del mondo**. Italia, USA, UK, Canada, EU... stesso metodo, dati diversi!

**Tool usato**: `ckan_package_search` (su server diverso)

---

### 💎 Livello 6: Interrogare Direttamente i Dati (DataStore)

Finora abbiamo visto solo **metadati** (titoli, descrizioni, organizzazioni). Ma alcuni portali CKAN hanno il **DataStore** attivo, che ti permette di interrogare direttamente i dati dentro i CSV!

#### Esempio Reale: Ordinanze Viabili del Comune di Messina

**Server**: `dati.comune.messina.it`
**Dataset**: "Ordinanze viabili"
**Totale record**: 2.041 ordinanze

**Tu chiedi**: "Dammi solo le ordinanze di tipo 'divieto_transito'"

**Filtro applicato**:

```
filters: { "tipo": "divieto_transito" }
```

**Risultato**: 259 ordinanze (su 2.041 totali)!

**Campi disponibili**:
- `numero`: numero ordinanza
- `data_pubblicazione`: quando è stata pubblicata
- `inizio_validita`, `fine_validita`: periodo di validità
- `aree`: zone interessate
- `tipo`: tipo di ordinanza
- `sintesi`: descrizione breve

**Esempio di risultato**:

| numero | data_pubblicazione | tipo | sintesi |
|--------|-------------------|------|---------|
| 153 | 2026-01-30 | divieto_transito | Viale S. Martino, limitazione 30 km/h |

**Nota importante**: il DataStore è disponibile principalmente sui **portali locali** (comuni, regioni), mentre il portale nazionale `dati.gov.it` raccoglie i metadati ma non attiva il DataStore. Se vuoi interrogare direttamente i dati, cerca dataset sui portali locali!

**Tool usato**: `ckan_datastore_search` (interroga dati tabellari)

---

## 🦸 Altri Super Poteri

Hai visto i tool principali in azione. Ma ce ne sono altri che ti danno poteri extra!

### 🎯 Trova i Dataset Più Rilevanti

**Tu chiedi**: "Quali sono i dataset più rilevanti sulla sanità e ospedali?"

Il sistema usa un **algoritmo di ranking** che considera titolo, descrizione, tag e organizzazione per darti i risultati **più pertinenti** in cima.

**Risultato**: 38 dataset ordinati per rilevanza!

**Tool usato**: `ckan_find_relevant_datasets`

---

### 🏢 Cerca Organizzazioni

**Tu chiedi**: "Quali organizzazioni hanno 'salute' nel nome?"

Ricerca tra tutte le organizzazioni registrate sul portale.

**Risultato**: 7 organizzazioni trovate, tra cui:
- Ministero della Salute (51 dataset)
- Agenzia di Tutela della Salute di Pavia (10 dataset)
- Agenzia di Tutela della Salute di Brescia (10 dataset)

**Tool usato**: `ckan_organization_search`

---

### 🏷️ Scopri i Tag Più Popolari

**Tu chiedi**: "Quali sono i 10 tag più usati su dati.gov.it?"

Ottieni la classifica dei tag più popolari, perfetto per capire quali temi sono più coperti!

**Top 3**:
1. "eu": 8.032 dataset
2. "N_A": 7.285 dataset
3. "lamma": 6.443 dataset

**Tool usato**: `ckan_tag_list`

---

### 📁 Esplora Gruppi Tematici

**Tu chiedi**: "Quanti dataset ci sono nel gruppo 'Ambiente' su dati.gov.it?"

Vedi tutti i dataset di quel gruppo tematico.

**Risultato**: 8.947 dataset sul tema Ambiente!

I gruppi sono raccolte curate di dataset su temi specifici (Ambiente, Salute, Economia, ecc.).

**Tool usato**: `ckan_group_show`

---

### ✅ Verifica la Qualità di un Dataset

**Tu chiedi**: "Qual è il punteggio di qualità del dataset sugli appalti ANAC 2018?" (solo su dati.gov.it)

Il sistema interroga le **metriche MQA** (Metadata Quality Assessment) di data.europa.eu:

**Dataset**: "ocds-appalti-ordinari-anno-2018" (ANAC)
**Punteggio complessivo**: 395/405 (quasi perfetto!)

**Dettaglio dimensioni**:
- ✅ Accessibilità: 100/100
- ⚠️ Riusabilità: 65/75
- ✅ Interoperabilità: 110/110
- ✅ Rintracciabilità: 100/100
- ✅ Contestualità: 20/20

Perfetto per valutare se un dataset è ben documentato e utilizzabile!

**Tool usato**: `ckan_get_mqa_quality`

---

### 🔍 Query SQL Avanzate (DataStore)

**Tu chiedi**: "Conta quante ordinanze per tipo ci sono nel dataset di Messina"

SQL direttamente sul DataStore:

```sql
SELECT tipo, COUNT(*) as totale
FROM "17301b8b-2a5b-425f-80b0-5b75bb1793e9"
GROUP BY tipo
ORDER BY totale DESC
LIMIT 5
```

**Risultato**:
1. divieto_sosta: 1.015
2. lavori: 267
3. divieto_transito: 259
4. autorizzazione: 192
5. divieto_sosta, divieto_transito: 186

Per analisi complesse, quando i filtri semplici non bastano!

**Tool usato**: `ckan_datastore_search_sql`

---

### 🌐 Verifica se un Portale è Online

**Tu chiedi**: "Il portale dati.gov.it è raggiungibile? Che versione usa?"

Verifica lo stato del server:
- ✅ Online
- Versione CKAN: 2.10.3
- Titolo: "Dati Gov IT"
- Descrizione: "Portale Nazionale Dati Aperti - AGID"

Utile prima di lanciare query su portali che non conosci!

**Tool usato**: `ckan_status_show`

---

## 📊 Comparazione: Web vs MCP Server

| Metodo | Steps | Tempo | Precisione |
|--------|-------|-------|-----------|
| **Interfaccia Web** | Clicca → cerca → filtra → pagina → rifiltra → pagina → esporta → analizza | 10-15 minuti | Dipende da te |
| **MCP Server** | Chiedi → ottieni | 30 secondi | Sempre precisa |

Vedi la differenza? 😎

---

## 🎯 Casi d'Uso Reali

### Giornalista Data-Driven 📰

**Scenario**: Stai scrivendo un articolo su appalti pubblici e vuoi dati freschi.

**Domanda**: "Trova dataset su appalti aggiornati negli ultimi 3 mesi su dati.gov.it"

**Risultato**: 127 dataset, tutti recenti e pronti per l'analisi!

---

### Ricercatore Open Data 🔬

**Scenario**: Vuoi studiare quali enti pubblicano più dati aperti.

**Domanda**: "Analizza quali organizzazioni hanno creato più dataset negli ultimi 6 mesi"

**Risultato**: Classifica pronta (Toscana: 12.602, Veneto: 6.555, Lombardia: 3.304), perfetta per il tuo paper!

---

### Civic Hacker 💻

**Scenario**: Vuoi monitorare nuovi dataset su mobilità urbana per creare una app.

**Domanda**: "Cerca dataset su mobilità urbana pubblicati nell'ultimo mese"

**Risultato**: Feed di novità, sempre aggiornato.

---

## 🚀 Getting Started

Vuoi provare? La configurazione richiede **2 minuti**:

1. Installa il server (vedi [README.md](../README.md))
2. Configura il tuo client MCP
3. Inizia a chiedere!

La tua AI fa il resto. Nessun codice da scrivere, solo domande da fare.

---

## 🌟 Cosa Rende Speciale Questo Strumento?

- ✅ **Impari una volta, usi ovunque**: stesso metodo per tutti i portali CKAN
- ✅ **Veloce**: secondi invece di minuti
- ✅ **Preciso**: query avanzate senza imparare linguaggi complicati
- ✅ **Flessibile**: da ricerche semplici ad analisi complesse
- ✅ **Accessibile**: nessuna programmazione richiesta
- ✅ **Open Source**: codice libero, migliora con la community!
- ✅ **DataStore**: interroga direttamente i dati (quando disponibile)

---

## 🤔 Domande Frequenti

**Q: Devo imparare a programmare?**
A: No! Chiedi in linguaggio naturale, la tua AI traduce per te.

**Q: Funziona solo su dati.gov.it?**
A: No! Funziona su **qualsiasi portale CKAN**: Italia, USA, UK, Canada, EU...

**Q: Posso interrogare direttamente i dati nei CSV?**
A: Sì, se il portale ha il DataStore attivo (tipicamente portali locali come comuni e regioni).

**Q: Con quale AI funziona?**
A: Con qualsiasi client che supporta MCP (Model Context Protocol).

**Q: È gratis?**
A: Sì, il server è open source. Serve un client MCP compatibile.

**Q: Posso contribuire?**
A: Assolutamente! Questo è un progetto open source: [GitHub repo](https://github.com/yourusername/ckan-mcp-server)

---

## 💡 Prossimi Passi

Pronto a provare? Vai al [README.md](../README.md) per l'installazione!

Hai domande o idee? Apri una [issue su GitHub](https://github.com/yourusername/ckan-mcp-server/issues)!

---

**Happy data hunting!** 🎉📊🔍
