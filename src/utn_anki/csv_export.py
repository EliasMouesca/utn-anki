from __future__ import annotations

import csv
import html
import re
from dataclasses import dataclass
from pathlib import Path

import genanki


ANKI_MODEL_ID = 80115514
ANKI_DECK_ID = 2145730821
MODEL_NAME = "UTN CSV QA"
SUPPORTED_COLUMNS = {"title", "question", "object", "answer", "tags"}

CARD_FRONT_TEMPLATE = """
<div class="card-shell">
  {{#Title}}<div class="title">{{Title}}</div>{{/Title}}
  <div class="question">{{Question}}</div>
  {{#Object}}<div class="object">{{Object}}</div>{{/Object}}
</div>
"""

CARD_BACK_TEMPLATE = """
<div class="card-shell">
  {{#Title}}<div class="title">{{Title}}</div>{{/Title}}
  <div class="question">{{Question}}</div>
  {{#Object}}<div class="object">{{Object}}</div>{{/Object}}
  <hr id="answer">
  <div class="answer-label">Respuesta</div>
  <div class="answer">{{Answer}}</div>
</div>
"""

CARD_CSS = """
.card {
  margin: 0;
  padding: 0;
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  text-align: left;
  color: #ffffff;
  background: #172033;
}
.card-shell {
  max-width: 760px;
  margin: 0 auto;
  padding: 28px 30px 34px;
}
.title {
  margin-bottom: 14px;
  font-size: 13px;
  line-height: 1.35;
  color: #9ca3af;
}
.question {
  white-space: pre-wrap;
  font-size: 31px;
  font-weight: 700;
  line-height: 1.2;
  color: #ffffff;
}
.object {
  margin-top: 18px;
  padding: 16px 18px;
  border-left: 4px solid #475569;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.08);
  white-space: pre-wrap;
  font-size: 22px;
  line-height: 1.45;
  color: #ffffff;
}
#answer {
  margin: 26px 0 18px;
  border: none;
  border-top: 1px solid #334155;
}
.answer-label {
  margin-bottom: 10px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #9ca3af;
}
.answer {
  white-space: pre-wrap;
  font-size: 25px;
  line-height: 1.45;
  color: #ffffff;
}
"""


@dataclass(frozen=True)
class CardRow:
    title: str
    question: str
    object_text: str
    answer: str
    tags: list[str]


def default_deck_name_from_csv(csv_path: Path) -> str:
    stem = re.sub(r"[-_]+", " ", csv_path.stem).strip()
    stem = re.sub(r"\s+", " ", stem)
    return stem.title() if stem else "Untitled Deck"


def build_deck_from_csv(csv_path: Path, output_path: Path, deck_name: str) -> Path:
    cards = load_cards_from_csv(csv_path)

    model = genanki.Model(
        ANKI_MODEL_ID,
        MODEL_NAME,
        fields=[
            {"name": "Title"},
            {"name": "Question"},
            {"name": "Object"},
            {"name": "Answer"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": CARD_FRONT_TEMPLATE,
                "afmt": CARD_BACK_TEMPLATE,
            }
        ],
        css=CARD_CSS,
    )

    deck = genanki.Deck(ANKI_DECK_ID, deck_name)
    for card in cards:
        note = genanki.Note(
            model=model,
            fields=[card.title, card.question, card.object_text, card.answer],
            tags=card.tags,
        )
        deck.add_note(note)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    genanki.Package(deck).write_to_file(str(output_path))
    return output_path


def load_cards_from_csv(csv_path: Path) -> list[CardRow]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV file has no header row.")

        normalized_fieldnames = {normalize_header(name): name for name in reader.fieldnames}
        missing = {"question", "answer"} - set(normalized_fieldnames)
        if missing:
            missing_list = ", ".join(sorted(missing))
            raise ValueError(f"CSV is missing required columns: {missing_list}")

        cards: list[CardRow] = []
        for row_number, raw_row in enumerate(reader, start=2):
            row = {normalize_header(key): normalize_cell(value) for key, value in raw_row.items() if key is not None}
            if is_empty_row(row):
                continue

            question = row.get("question", "")
            answer = row.get("answer", "")
            if not question or not answer:
                raise ValueError(
                    f"Row {row_number} must include non-empty 'question' and 'answer' values."
                )

            title = row.get("title", "")
            object_text = row.get("object", "")
            tags = collect_tags(row.get("tags", ""), title)
            cards.append(
                CardRow(
                    title=escape_field(title),
                    question=escape_field(question),
                    object_text=escape_field(object_text),
                    answer=escape_field(answer),
                    tags=tags,
                )
            )

    if not cards:
        raise ValueError("CSV did not contain any usable cards.")

    return cards


def normalize_header(value: str | None) -> str:
    return (value or "").strip().lower()


def normalize_cell(value: str | None) -> str:
    return (value or "").strip()


def is_empty_row(row: dict[str, str]) -> bool:
    relevant_values = [row.get(column, "") for column in SUPPORTED_COLUMNS]
    return not any(value.strip() for value in relevant_values)


def collect_tags(raw_tags: str, title: str) -> list[str]:
    tags: list[str] = []
    if title:
        title_tag = slugify_tag(title)
        if title_tag:
            tags.append(title_tag)

    for token in re.split(r"[;,]", raw_tags):
        tag = slugify_tag(token)
        if tag and tag not in tags:
            tags.append(tag)
    return tags


def slugify_tag(value: str) -> str:
    cleaned = re.sub(r"\s+", "_", value.strip())
    cleaned = re.sub(r"[^\w:_-]", "", cleaned, flags=re.UNICODE)
    return cleaned


def escape_field(value: str) -> str:
    return html.escape(value, quote=False)
