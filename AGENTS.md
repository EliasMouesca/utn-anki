# AGENTS.md

## Propósito

Este repositorio genera mazos de Anki (`.apkg`) a partir de un CSV con un esquema fijo.
La decisión difícil de contenido ya viene resuelta afuera: seleccionar las preguntas y volcarlas al formato estándar.

El contrato principal que debe preservarse es:

```bash
./build_deck.py preguntas.csv -n "Preguntas de una materia"
```

Eso debe generar `preguntas.apkg` con nombre de mazo `Preguntas de una materia`.
Si no se pasa `-n` o `--deck-name`, el nombre del mazo debe derivarse del nombre del archivo CSV.

## Flujo actual

- `build_deck.py` es un wrapper mínimo ejecutable.
- `scripts/build_anki_deck_from_csv.py` implementa el CLI real.
- `src/utn_anki/csv_export.py` contiene la lógica de lectura del CSV y generación del `.apkg` usando `genanki`.

Punto de entrada esperado:

```bash
./build_deck.py preguntas.csv
./build_deck.py preguntas.csv -n "Preguntas de una materia"
./build_deck.py preguntas.csv --output salida/preguntas.apkg
```

## Formato CSV

`template.csv` define el formato base:

```csv
title,question,object,answer
```

Columnas soportadas:

- `title`: opcional como texto visible y además se convierte en tag.
- `question`: obligatoria.
- `object`: opcional; funciona como contexto adicional.
- `answer`: obligatoria.
- `tags`: opcional aunque no figure en `template.csv`; acepta separadores `,` o `;`.

Reglas de carga relevantes:

- El parser acepta encabezados con mayúsculas/minúsculas mezcladas.
- Filas completamente vacías se ignoran.
- Si falta `question` o `answer` en una fila no vacía, se lanza error.
- Si no hay cartas utilizables, se lanza error.

## Convenciones de salida

- Si no se pasa `--output`, la salida es `<csv_stem>.apkg` en la raíz del proyecto.
- Si ya existe ese `.apkg`, se mueve antes a `bkp/` con timestamp.
- El nombre del mazo por defecto se deriva del stem del CSV:
  - `preguntas_final.csv` -> `Preguntas Final`
  - `administracion-gerencial.csv` -> `Administracion Gerencial`

## Implementación actual de cartas

- Modelo Anki: `UTN CSV QA`
- Campos: `Title`, `Question`, `Object`, `Answer`
- Front: muestra `title`, `question` y opcionalmente `object`
- Back: repite el frente y agrega `answer`
- `question`, `object` y `answer` se exportan como texto escapado HTML, sin interpretación de markdown ni tipos especiales.
- Si `question`, `object` o `answer` contienen saltos de línea en el CSV, deben verse también en la carta.
  Esto hoy se logra desde el CSS del modelo con `white-space: pre-wrap` en esos bloques.

## Dependencias

- `genanki==0.13.1`

## Criterios para cambios futuros

- No romper el contrato CLI de `./build_deck.py`.
- Mantener `template.csv` como referencia mínima del formato esperado.
- Si se agregan nuevas columnas, hacerlo de forma backward compatible.
- Priorizar errores claros cuando el CSV no cumple el esquema.
