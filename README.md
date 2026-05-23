# UTN_anki

Base genérica para construir mazos de Anki a partir de un CSV.

Este proyecto fue hecho con ayuda de genAI.

## Estructura

- `build_deck.py`: wrapper ejecutable principal.
- `scripts/build_anki_deck_from_csv.py`: CLI real.
- `src/utn_anki/csv_export.py`: lógica de lectura del CSV y generación del `.apkg`.
- `template.csv`: formato mínimo de referencia para el CSV.
- `AGENTS.md`: contrato funcional y decisiones de implementación del repo.

## Uso rápido

```bash
./build_deck.py preguntas.csv
./build_deck.py preguntas.csv -n "Preguntas de una materia"
./build_deck.py preguntas.csv --output salida/preguntas.apkg
```

Si no se pasa `-n` o `--deck-name`, el nombre del mazo se deriva del nombre del archivo CSV.

Si no se pasa `--output`, la salida es `<csv_stem>.apkg` en la raíz del proyecto.

Si ese `.apkg` ya existe, antes de regenerarlo se mueve a `bkp/` con timestamp.

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

Reglas:

- El parser acepta encabezados con mayúsculas/minúsculas mezcladas.
- Filas completamente vacías se ignoran.
- Si falta `question` o `answer` en una fila no vacía, se lanza error.
- Si no hay cartas utilizables, se lanza error.

## Cartas generadas

- Modelo Anki: `UTN CSV QA`
- Campos: `Title`, `Question`, `Object`, `Answer`
- `question`, `object` y `answer` se exportan como texto escapado HTML.
- Los saltos de línea del CSV se preservan en la visualización de la carta.

## Dependencia

```bash
python3 -m pip install -r requirements.txt
```
