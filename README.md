# UTN_anki

Base genérica para construir mazos de Anki a partir de un CSV.

## Estructura

- `cards.csv`: ejemplo funcional con el formato correcto.
- `cards_template.csv`: template vacío para arrancar otro mazo.
- `Preguntas AG - Hoja 1.csv`: ejemplo real heredado de `AG_anki`.
- `AGENTS.md`: conocimiento copiado de Administración Gerencial.
- `src/utn_anki/csv_export.py`: lógica de exportación desde CSV.
- `scripts/build_anki_deck_from_csv.py`: script principal de exportación.
- `build_deck.py`: wrapper corto para reconstruir el mazo.
- `resources/media/`: imágenes opcionales reutilizables.

## Uso rápido

```bash
python3 build_deck.py
```

Por defecto toma `cards.csv` y genera `cards.apkg`.

Si el `.apkg` ya existe, antes de regenerarlo se mueve a `bkp/` con timestamp.

También podés pasar cualquier CSV con el mismo esquema:

```bash
python3 build_deck.py /ruta/cartas.csv
python3 build_deck.py /ruta/cartas.csv --deck-name "Mi mazo"
python3 build_deck.py /ruta/cartas.csv --output /ruta/mi_mazo.apkg
```

## Formato CSV

Columnas mínimas:

- `title`
- `question`
- `object`
- `answer`

Opcional:

- `tags`

Reglas:

- `question` y `answer` son obligatorios.
- `object` es opcional y se muestra como contexto adicional.
- `tags` acepta valores separados por `,` o `;`.
- El exportador no interpreta tipos especiales: simplemente muestra `question`, `object` y `answer` tal como estén escritos en el CSV.

## Dependencia

```bash
python3 -m pip install genanki
```
