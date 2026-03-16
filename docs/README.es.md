# Agent Fact Check Verify

**Selector de idioma**: [中文](../README.md) | [English](README.en.md) | **Español (actual)** | [العربية](README.ar.md)

Versión: **1.0.1**  
Autor: **Allen Niu**  
Licencia: **MIT**

`agent-fact-check-verify` es una habilidad de verificación rigurosa para agentes de IA. Extrae afirmaciones verificables, realiza verificación cruzada multi‑fuente (oficial, medios principales, sitios de fact-check y señales sociales), aplica reglas internas deterministas y entrega una respuesta neutral e integrada sin mostrar puntuaciones internas al usuario.

---

## 1. Objetivos de diseño y principios profesionales

Esta habilidad está construida para flujos auditables y reproducibles, no para textos “que suenan convincentes”.

- **Reproducible**: misma evidencia, misma decisión.
- **Trazable**: cada conclusión se vincula con fuentes.
- **Auditable**: reglas internas fijas; sin puntuación arbitraria.
- **Neutral**: redacción sin postura política.
- **Costo acotado**: presupuesto de búsquedas por afirmación.

---

## 2. Alcance (qué hace / qué no hace)

### 2.1 Incluye

1. Extracción de afirmaciones desde texto largo.
2. Clasificación de tipo: statistical / causal / attribution / event / prediction / opinion / satire.
3. Verificación en tres rondas: oficial → mainstream → contraevidencia.
4. Decisión interna determinista por bandas.
5. Respuesta integrada al usuario sin mostrar puntuación.

### 2.2 Excluye

1. No fuerza veredicto verdadero/falso para opiniones puras.
2. No toma volumen social como prueba principal.
3. No usa lenguaje de persuasión política.
4. No garantiza cobertura de material privado o de pago.

---

## 3. Estructura del proyecto

```text
agent-fact-check-verify/
├── SKILL.md
├── LICENSE
├── README.md                    # Chino por defecto
├── scripts/
│   └── factcheck_engine.py      # extract / score / compose
├── references/
│   ├── scoring-rubric.md
│   └── source-policy.md
└── docs/
    ├── README.en.md
    ├── README.es.md
    └── README.ar.md
```

---

## 4. Instalación y requisitos de entorno

### 4.1 Requisitos base

- Python 3.10+
- Capacidad de búsqueda del agente (Brave / Tavily / Browser)
- Permiso de lectura/escritura en workspace

### 4.2 Comprobación rápida

```bash
python3 scripts/factcheck_engine.py --help
```

Si aparecen `extract|score|compose`, está listo.

---

## 5. CLI opcionales y categorías de cookies (importante)

Estas CLI son **opcionales**. El flujo principal funciona sin ellas.

- CLI de X: <https://github.com/jackwener/twitter-cli>
- CLI de Reddit: <https://github.com/jackwener/rdt-cli>

### 5.1 twitter-cli (modo cookie)

Categorías comunes:

- **Autenticación requerida**: `auth_token`, `ct0`
- **Apoyo de sesión**: `guest_id`, `kdt`
- **Campos opcionales**: `twid`, `lang`

Buenas prácticas:

- Guardar cookies con permisos restringidos.
- Nunca subir cookies a git.
- Rotar cookies de forma periódica.

### 5.2 rdt-cli (modo cookie)

Categorías comunes de cookie/sesión:

- **Sesión principal**: `reddit_session`
- **Dispositivo/seguimiento**: `loid`, `session_tracker`
- **Campos opcionales de autenticación**: `token_v2` (depende de versión)

Buenas prácticas:

- Usar cuenta de mínimo privilegio.
- Renovar cookies expiradas y evitar almacenamiento en texto plano en entornos compartidos.

---

## 6. Flujo de ejecución recomendado

### Paso A: Extraer afirmaciones

```bash
python3 scripts/factcheck_engine.py extract \
  --text "texto de entrada" \
  --output claims.json
```

### Paso B: Verificación en tres rondas (lado agente)

1. **Primero fuentes oficiales/primarias**.
2. **Corroboración independiente en medios principales**.
3. **Búsqueda de contraevidencia/desmentidos**.

Límite recomendado: 6 búsquedas por afirmación.

### Paso C: Decisión interna

```bash
python3 scripts/factcheck_engine.py score \
  --input evidence.json \
  --output scored.json
```

### Paso D: Componer respuesta al usuario

```bash
python3 scripts/factcheck_engine.py compose \
  --input scored.json \
  --output reply.txt
```

---

## 7. Contrato de campos en evidence.json (detallado)

Campos recomendados por afirmación:

- `claim`
- `type`
- `evidence.official_count`
- `evidence.mainstream_count`
- `evidence.independent_count`
- `evidence.factcheck_true`
- `evidence.factcheck_false`
- `evidence.authority_rebuttal`
- `evidence.outdated_presented_current`
- `evidence.source_chain_hops`
- `evidence.core_contradiction`
- `evidence.has_timestamp`
- `evidence.strong_social_debunk`
- `evidence.out_of_context`
- `evidence.headline_mismatch`
- `evidence.missing_data_citation`
- `evidence.fact_opinion_mixed`

---

## 8. Reglas duras de salida al usuario

- Nunca mostrar puntuación interna.
- Nunca exponer la lógica interna de puntuación.
- No separar en bloques de “suplemento” y “información correcta”; integrar en una narrativa única.
- Evitar viñetas salvo necesidad.
- Usar hipervínculos clicables para fuentes.
- Orden de presentación: falso → incierto → verdadero.
- Añadir siempre:

`⚠️ Esta verificación se basa en información públicamente disponible y no puede cubrir materiales privados o de pago.`

---

## 9. Manejo de casos límite

- **Prediction**: sin veredicto verdadero/falso; resumir pronósticos disponibles.
- **Opinion**: marcar como subjetivo y fuera de alcance de fact-check.
- **Satire**: marcar como fuente satírica/ficción.
- **Evidencia insuficiente**: responder “actualmente no verificable” de forma conservadora.

---

## 10. Riesgos y límites

1. La información pública nunca es completa.
2. Las noticias en desarrollo pueden cambiar rápidamente.
3. Las señales sociales son auxiliares, no evidencia principal.
4. Incluso fuentes oficiales pueden tener sesgo institucional; se requiere validación cruzada.

---

## 11. Documentación multilingüe

- Chino: `../README.md`
- Inglés: `README.en.md`
- Árabe: `README.ar.md`
