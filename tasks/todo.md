# Task: Aggiungere tool ckan_organization_search

## Obiettivo

Implementare un nuovo tool MCP dedicato alla ricerca di organizzazioni per nome, con interfaccia più semplice rispetto a `package_search` con sintassi Solr.

## Fasi

### Fase 1: Implementazione tool
- [ ] Aggiungere `ckan_organization_search` in `src/index.ts` (prima riga 872)
- [ ] Schema input: `server_url`, `pattern`, `response_format`
- [ ] Costruire query Solr automatica: `organization:*{pattern}*`
- [ ] Chiamare `package_search` con `rows=0` e `facet.field=organization`
- [ ] Output JSON: `{ count: N, organizations: [...] }`
- [ ] Output markdown: tabella organizzazioni con conteggio dataset

### Fase 2: Testing
- [ ] Build: `npm run build`
- [ ] Test con pattern "toscana"
- [ ] Verificare output JSON
- [ ] Verificare output markdown

### Fase 3: Documentazione
- [ ] Aggiungere esempi in `EXAMPLES.md`
- [ ] Aggiornare `LOG.md` con data e modifiche

## Dettagli Implementazione

**Posizione**: Dopo tool `ckan_organization_show` (circa riga 700) e prima di `ckan_datastore_search`

**Firma tool**:
```typescript
server.registerTool(
  "ckan_organization_search",
  {
    title: "Search CKAN Organizations by Name",
    description: "...",
    inputSchema: z.object({
      server_url: z.string().url(),
      pattern: z.string().min(1).describe("Search pattern (wildcards added automatically)"),
      response_format: ResponseFormatSchema
    }).strict(),
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: true
    }
  },
  async (params) => { ... }
)
```

**Logica**:
1. Query Solr: `organization:*${params.pattern}*`
2. API call: `package_search` con `rows=0`, `facet.field=["organization"]`, `facet.limit=500`
3. Parsing facets per estrarre organizzazioni matchate
4. Output formattato

## Note

- Molto più semplice di costruire query manualmente
- Risparmio token: restituisce solo organizzazioni, non dataset
- Pattern matching automatico (l'utente non deve ricordare wildcard Solr)

---

## Review

### Modifiche Completate

**File modificati**:
1. `src/index.ts` - Aggiunto tool `ckan_organization_search` (righe 680-785)
2. `EXAMPLES.md` - Aggiunti esempi di utilizzo (righe 54-73)
3. `LOG.md` - Documentata la nuova feature

**Implementazione**:
- Tool registrato tra `ckan_organization_show` e `ckan_datastore_search`
- Schema input: `server_url`, `pattern`, `response_format`
- Query Solr automatica: `organization:*{pattern}*`
- Utilizza `package_search` con `rows=0` per efficienza massima
- Output JSON: `{ count, total_datasets, organizations: [...] }`
- Output markdown: tabella formattata con org e conteggio dataset

**Testing**:
- Build completato con successo (47ms, esbuild)
- Test manuale con pattern "toscana": ✅
  - 2 organizzazioni trovate
  - 11.000 dataset totali
  - Output JSON corretto
  - Zero dataset scaricati (solo facet)

**Vantaggi**:
- **UX migliorata**: API semplice vs sintassi Solr
- **Efficienza**: filtraggio lato server, zero dataset trasmessi
- **Token saving**: solo metadata organizzazioni
- **Performance**: wildcard automatici, no costruzione query manuale

### Prossimi Passi

Per utilizzare il tool:
1. Riavviare Claude Code per caricare il nuovo server MCP
2. Il tool sarà disponibile come `ckan_organization_search`

### Esempio Output

```json
{
  "count": 2,
  "total_datasets": 11000,
  "organizations": [
    {
      "name": "regione-toscana",
      "display_name": "Regione Toscana",
      "dataset_count": 10988
    },
    {
      "name": "autorita-idrica-toscana",
      "display_name": "Autorità Idrica Toscana",
      "dataset_count": 12
    }
  ]
}
```
