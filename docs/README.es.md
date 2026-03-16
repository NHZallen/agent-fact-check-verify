# Agent Fact Check Verify

Versión: **1.0.0**  
Autor: **Allen Niu**  
Licencia: **MIT**

Esta es una habilidad rigurosa de verificación para agentes de IA. Divide el texto de entrada en afirmaciones verificables, combina fuentes oficiales, medios principales, sitios de fact-check y señales sociales (X/Reddit), aplica un modelo interno de 100 puntos basado en reglas, y devuelve conclusiones neutrales e integradas sin exponer detalles de puntuación al usuario final.

## Índice

- [1. Objetivo y principios de diseño](#1-objetivo-y-principios-de-diseño)
- [2. Alcance](#2-alcance)
- [3. Requisitos no funcionales](#3-requisitos-no-funcionales)
- [4. Estructura del proyecto](#4-estructura-del-proyecto)
- [5. Instalación](#5-instalación)
- [6. Herramientas CLI opcionales y categorías de cookies](#6-herramientas-cli-opcionales-y-categorías-de-cookies)
- [7. Flujo de trabajo](#7-flujo-de-trabajo)
- [8. Formatos de entrada y salida](#8-formatos-de-entrada-y-salida)
- [9. Política de decisión (sin mostrar puntuación al usuario)](#9-política-de-decisión-sin-mostrar-puntuación-al-usuario)
- [10. Reglas de estilo de respuesta](#10-reglas-de-estilo-de-respuesta)
- [11. Limitaciones y riesgos](#11-limitaciones-y-riesgos)
- [12. Documentación multilingüe](#12-documentación-multilingüe)

## 1. Objetivo y principios de diseño

Esta habilidad se centra en verificación de verdad y trazabilidad de evidencia. No produce encuadres emocionales ni persuasión política.

Principios de diseño:

1. **Reproducible**: la misma evidencia produce la misma decisión.
2. **Trazable**: cada conclusión enlaza a fuentes.
3. **Neutral**: el texto para usuario mantiene neutralidad.
4. **Simple externamente**: no se expone la puntuación interna.
5. **Costo acotado**: presupuesto fijo de búsqueda por afirmación (máximo recomendado: 6).

## 2. Alcance

- Extracción de afirmaciones desde texto largo.
- Clasificación de afirmaciones: statistical / causal / attribution / event / prediction / opinion / satire.
- Verificación multifuente: oficial, mainstream, contraevidencia, señales sociales.
- Puntuación interna: sistema determinista de 100 puntos (solo interno).
- Respuesta al usuario: conclusión integrada sin mostrar puntuación.

## 3. Requisitos no funcionales

- Idioma por defecto para usuario: chino.
- Orden de respuesta: falso primero, luego incierto, luego verdadero.
- Evitar viñetas salvo necesidad.
- Siempre añadir este descargo:

`⚠️ Esta verificación se basa en información públicamente disponible y no puede cubrir materiales privados o de pago.`

## 4. Estructura del proyecto

```text
agent-fact-check-verify/
├── SKILL.md
├── LICENSE
├── README.md
├── scripts/
│   └── factcheck_engine.py
├── references/
│   ├── scoring-rubric.md
│   └── source-policy.md
└── docs/
    ├── README.en.md
    ├── README.es.md
    └── README.ar.md
```

## 5. Instalación

### 5.1 Requisitos del sistema

- Python 3.10+
- Cadena de herramientas del agente con búsqueda web (Brave / Tavily / Browser)

### 5.2 Permisos

- Acceso de lectura/escritura al workspace
- Capacidad de invocar herramientas de búsqueda

### 5.3 Validación básica

```bash
python3 scripts/factcheck_engine.py --help
```

## 6. Herramientas CLI opcionales y categorías de cookies

Estas dos CLI son **opcionales**, no obligatorias. Si no están disponibles, se usa búsqueda web normal.

- Búsqueda en X: <https://github.com/jackwener/twitter-cli>
- Búsqueda en Reddit: <https://github.com/jackwener/rdt-cli>

### 6.1 Categorías comunes de cookies para twitter-cli

Los campos reales dependen de la versión de la CLI. Categorías comunes:

- Requeridas: `auth_token`, `ct0`
- Auxiliares comunes: `guest_id`, `kdt`
- Posibles: `twid`, `lang`

Recomendaciones:

- Guardar cookies solo en entorno local seguro.
- Nunca subir cookies al control de versiones.

### 6.2 Categorías comunes de cookie/sesión para rdt-cli

Los campos reales dependen de la versión de la CLI. Categorías comunes:

- Sesión: `reddit_session`
- Dispositivo/seguimiento: `loid`, `session_tracker`
- Otros posibles: `token_v2` o cookie de autenticación equivalente

Recomendaciones:

- Preferir flujo OAuth oficial si está soportado.
- Si se requiere login por cookie, usar cuenta de mínimo privilegio y rotar periódicamente.

## 7. Flujo de trabajo

### 7.1 Extraer afirmaciones

```bash
python3 scripts/factcheck_engine.py extract \
  --text "texto de entrada" \
  --output claims.json
```

### 7.2 Verificación externa (ejecutada por el agente)

Tres rondas recomendadas:

1. Fuentes oficiales y primarias
2. Cruce con medios principales
3. Contraevidencia y desmentidos

Luego consolidar evidencia en JSON y ejecutar scoring.

### 7.3 Puntuación interna

```bash
python3 scripts/factcheck_engine.py score \
  --input evidence.json \
  --output scored.json
```

### 7.4 Componer respuesta al usuario

```bash
python3 scripts/factcheck_engine.py compose \
  --input scored.json \
  --output reply.txt
```

## 8. Formatos de entrada y salida

### 8.1 Entrada de score (evidence.json)

Cada afirmación puede incluir:

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

### 8.2 Entrada de compose (scored.json)

- `band` desde score: `true|false|uncertain|prediction|opinion|satire`
- `findings`, `correct_info`, `sources` pueden ser enriquecidos por el agente

## 9. Política de decisión (sin mostrar puntuación al usuario)

- `true`: decir verificado como verdadero y ampliar con contexto preciso.
- `false`: decir que no coincide y integrar la información correcta.
- `uncertain`: indicar que actualmente no es verificable.
- `prediction`: sin juicio de verdad; mostrar fuentes de predicción disponibles.
- `opinion`: marcar como opinión, fuera del alcance de fact-check.
- `satire`: marcar como fuente satírica/ficción.

## 10. Reglas de estilo de respuesta

- No mostrar puntuación interna.
- No separar en bloques “suplemento” o “información correcta”; integrar de forma natural.
- Evitar viñetas salvo necesidad.
- Mostrar falsos primero, luego inciertos, luego verdaderos.
- Usar hipervínculos clicables para fuentes.

## 11. Limitaciones y riesgos

- Materiales de pago/privados no son visibles.
- Noticias en desarrollo pueden cambiar en minutos.
- Señales sociales no son evidencia primaria.
- Algunos datos oficiales pueden tener sesgo institucional y requieren validación cruzada.

## 12. Documentación multilingüe

- Chino: `README.md`
- Inglés: `docs/README.en.md`
- Árabe: `docs/README.ar.md`
