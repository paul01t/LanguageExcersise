# Language Exercise Game

A small Tkinter app for practising a language pair. It defaults to English → Norwegian
Bokmål, but the pair is configurable with `LANG_FROM`/`LANG_TO`, so it works with other
languages too (the bundled datasets and reference model are Norwegian-specific, though).
It asks an OpenAI-compatible chat-completions server (LM Studio by default) to generate
an exercise, shows it in a dark-themed UI, and checks your answer.

> **Note:** This is a fun side project made to experiment with model training — nothing
> serious or production-ready. AI-generated exercises and answers can be incorrect or
> malformed, so review the data before relying on it.

## Features

- **Levels 1–10** in the UI. (The generator prompt itself accepts levels 1–15.)
- **Four exercise types:** matching, single-word translation, translation, and
  fill-in-the-blank.
- **Level gating:** levels 1–3 offer only matching and single-word translation;
  levels 4–10 offer all four types.
- **Both directions:** each new exercise randomly uses `LANG_FROM → LANG_TO` or the reverse.
- **Matching rounds:** pick a translation for every word, then check the whole round for a score.
- **Answer checking:** type an answer and press Enter (or click *Check answer*); an
  optional hint is shown when the model supplies one.
- **Responsive UI:** exercises are generated on a background thread.

## How it works

| File | Responsibility |
|---|---|
| `exercise_game.py` | Tkinter UI, exercise display, and answer checking. |
| `exercise_generator.py` | Loads `.env`, builds a type-specific prompt, calls the model, strips markdown fences, and parses the returned JSON. |

`exercise_game.py` imports `LANG_FROM` and `LANG_TO` from `exercise_generator.py`, so the
language pair is read from `.env` at startup.

## Requirements

- Python **3.10+** (the code uses `X | None` type syntax).
- **Tkinter** — bundled with standard Windows and macOS Python installs; on Debian/Ubuntu
  install it with `sudo apt install python3-tk`.
- **LM Studio** (or another OpenAI-compatible chat-completions server) running locally.
- Python packages from `requirements.txt`:
  - `openai>=1.0.0,<4.0.0`
  - `python-dotenv>=1.0.0,<2.0.0`

## Setup

From the project root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Edit `.env` with your server and language settings:

```dotenv
BASE_URL=http://localhost:1234/v1
API_KEY=lm-studio
MODEL=local-model
LANG_FROM=English
LANG_TO=Norwegian
TEMPERATURE=0.5
```

| Variable | Default | Meaning |
|---|---|---|
| `BASE_URL` | `http://localhost:1234/v1` | OpenAI-compatible server endpoint. |
| `API_KEY` | `lm-studio` | Key sent to the server; LM Studio ignores it but the client requires one. |
| `MODEL` | `local-model` | Model identifier. LM Studio routes it to whichever model is loaded. |
| `LANG_FROM` | `English` | Source language for exercises. |
| `LANG_TO` | `Norwegian` | Target language for exercises. |
| `TEMPERATURE` | `0.5` | Sampling temperature. |

`.env` is local configuration and is ignored by Git (see `.gitignore`). Keep real API
credentials there and do not commit them. Before using the app, load a model in LM Studio
and start its local server.

## Run the game

```powershell
python exercise_game.py
```

The window opens at 1920 × 1080 (minimum 660 × 540). Choose a level and exercise type,
then click **New exercise**.

## Project structure

```text
.
├── exercise_game.py          # Tkinter game
├── exercise_generator.py     # Model client + exercise prompts
├── requirements.txt
├── .env.example
├── LICENSE
├── README.md
└── DataForModelTraining/
    ├── training_data.json
    ├── training_data1.json
    ├── training_data2.json
    ├── CleanDataSet.json
    ├── Fixed_Data.json
    ├── train_data.jsonl
    ├── convert.py
    ├── fixgrammar.py
    └── test.py
```

## Training data

Every JSON record has an `input` object and an `output` object:

- `input` — `level`, `language`, `exercise_type`, and `direction` (translations only).
- `output` — the expected exercise payload. Its shape depends on the exercise type:
  - **matching** → `pairs`
  - **translation** → `question`, `answer`, `word_pool` (the runtime prompt asks for
    `question`, `answer`, and `hint` instead)
  - **fill-in-the-blank** → `sentence_with_blank`, `answer`, `hint`

The bundled datasets contain translation, matching, and fill-in-the-blank records.
Single-word translation is generated at runtime but does not appear in the data files.

| File | Records | Role |
|---|---:|---|
| `DataForModelTraining/training_data.json` | 750 | Source file read by `convert.py`. |
| `DataForModelTraining/training_data1.json` | 500 | Source file read by `fixgrammar.py`. |
| `DataForModelTraining/training_data2.json` | 250 | Additional data; no current script reads it. |
| `DataForModelTraining/CleanDataSet.json` | 796 | Cleaned dataset (levels 1–15); not read by `convert.py`. |
| `DataForModelTraining/Fixed_Data.json` | 500 | Output created by `fixgrammar.py`. |
| `DataForModelTraining/train_data.jsonl` | 750 | JSONL output created by `convert.py`. |

### Data-preparation scripts

Both scripts use paths relative to their own directory, so run them from
`DataForModelTraining`.

**`fixgrammar.py`** reads `training_data1.json`, and for each translation exercise splits
`word_pool` entries into individual words and strips `. , ? !`, then writes
`Fixed_Data.json`.

**`convert.py`** reads `training_data.json` and writes one JSONL record per example. Each
record contains a `messages` array with a user prompt and an assistant response:

```json
{"messages": [
  {"role": "user", "content": "Generate a level 10 norwegian_bokmal exercise of type fill_in_blank. Direction: N/A."},
  {"role": "assistant", "content": "{\"sentence_with_blank\": \"Barna vil ikke ___ huset.\", \"answer\": \"finne\", \"hint\": \"find\"}"}
]}
```

The user prompt summarizes the level, language, exercise type, and direction (`N/A` when
no direction is present). The assistant content is the example's `output` serialized as
JSON.

To regenerate `train_data.jsonl`:

```powershell
Set-Location DataForModelTraining
python convert.py
```

To recreate `Fixed_Data.json`:

```powershell
Set-Location DataForModelTraining
python fixgrammar.py
```

> `convert.py` reads `training_data.json`, **not** `Fixed_Data.json`.

## Testing inference

`DataForModelTraining/test.py` sends a fixed set of matching, translation, and
fill-in-the-blank prompts to LM Studio, strips any markdown fences, and tries to parse
each response as JSON, printing `VALID JSON` or `INVALID JSON`.

It uses `temperature=0.4` and `max_tokens=300`. (A code comment says "LOWERED to 0.1",
but the argument actually passed is `0.4`.)

Start the LM Studio server first, then run:

```powershell
Set-Location DataForModelTraining
python test.py
```

`test.py` hardcodes `base_url="http://localhost:1234/v1"` and `model="local-model"`, so it
does not read `.env`.

## Model and training

The reference model used for this project's training and testing is
[`NbAiLab/nb-notram-llama-3.1-8b-instruct`](https://huggingface.co/NbAiLab/nb-notram-llama-3.1-8b-instruct).

There is **no training or fine-tuning script, training configuration, or model checkpoint
in this repository.** The repository prepares data (`fixgrammar.py`, `convert.py`) and
tests inference (`test.py`); fine-tuning must be done separately in a compatible training
tool. The fine-tuning method and hyperparameters are not documented here.

## License

Released under the [MIT License](LICENSE).
