# Optional evaluation frameworks

`framework_metrics.py` runs actual Ragas and DeepEval metrics over saved chatbot responses. The frameworks are optional: the core runner can operate without them, but a requested framework that cannot import produces an error and a nonzero exit. These metrics supplement the kit's contract, citation, tool, and guardrail checks; they do not replace them.

Verified integration targets: Python 3.12, Ragas 0.4.3, DeepEval 4.2.8 (2026-10-07). Use separate environments because their dependency trees differ. The short requirements files describe direct dependencies; `requirements-*.lock.txt` pin the resolved transitive dependencies from clean Python 3.12 environments. Install from the locks for the verified dependency set. No pre-existing runtime is required.

Run from the kit directory (`tools/evals` in the starter, or the directory containing `main.py` for a standalone copy):

```sh
sh setup-tools.sh
python3 main.py demo --out runs/framework-demo-01 --frameworks auto
```

The setup uses standard-library `venv` and `pip`, and is safe to repeat. It chooses `python3.12` when available, otherwise `python3` (>=3.12); override with `EVAL_SETUP_PYTHON`. Python 3.12 is the verified version for these optional framework locks. macOS/Linux manual equivalent:

```sh
python3.12 -m venv .venv-ragas
.venv-ragas/bin/python -m pip install -r integrations/requirements-ragas.lock.txt
python3.12 -m venv .venv-deepeval
.venv-deepeval/bin/python -m pip install -r integrations/requirements-deepeval.lock.txt
```

On Windows PowerShell, create the same environments with `py -3.12 -m venv .venv-ragas` and `py -3.12 -m venv .venv-deepeval`, then use `.venv-ragas\Scripts\python.exe` and `.venv-deepeval\Scripts\python.exe` for the two pip commands. The runner recognizes both layouts. Core portability tests run independently of these optional packages; optional Windows installs require platform-compatible wheels.

`--frameworks auto` only selects `EVAL_RAGAS_PYTHON` / `EVAL_DEEPEVAL_PYTHON` when explicitly set, otherwise `.venv-ragas` / `.venv-deepeval` inside this kit. Explicit relative interpreter paths use the caller's working directory. An invalid explicit interpreter is an error, never a reason to fall back to a different one. Home directories and unrelated environments are never searched. Keep the environments separate because the framework dependency trees differ.

To run one integration directly after generating a demo:

```sh
.venv-ragas/bin/python integrations/framework_metrics.py \
  --framework ragas --input runs/framework-demo-01/framework-input.json --output runs/framework-demo-01/ragas-direct.json
.venv-deepeval/bin/python integrations/framework_metrics.py \
  --framework deepeval --input runs/framework-demo-01/framework-input.json --output runs/framework-demo-01/deepeval-direct.json
```

To upgrade deliberately, change a direct requirements file, create a fresh Python 3.12 environment, install that file, run the integration tests/offline demo, and regenerate the corresponding lock with `python -m pip freeze`. Review the lock diff; do not replace measured compatibility pins just to make installation succeed.

## Input and output

Input is one JSON object with `cases` and `responses` arrays. Cases contain `id`, `category`, `question`, `expected_answer`, `contexts: [{id, text}]`, `expected`, and optional `tags`. Responses contain `case_id`, `answer`, `retrieved_contexts: [{id, text}]`, and optional `error`; other adapter fields are preserved by the caller but not used here. IDs must be unique and response IDs must identify known cases. Missing or failed responses are errors rather than passing scores.

The output contains `framework`, installed `version`, `mode` (`offline` or `judge`), `results`, and `errors`. Every case/metric has `score` (number or null), `status` (`scored`, `not_run`, `error`), and an optional `reason` or `threshold`. Judge mode additionally reports `judge_requests`. A metric threshold, where supplied, is the library's success threshold, not a cross-framework quality standard. Exit code 0 means the requested applicable operations completed; 1 means at least one error. A `not_run` record is never a passed metric. No aggregate score is manufactured from missing evaluations.

## Applicability and interpretation

| Framework metric | Runs when | Meaning and limitation |
| --- | --- | --- |
| Ragas `non_llm_context_recall` | RAG case with nonempty gold and retrieved context text | Fraction of gold contexts matched using normalized Levenshtein string similarity; Ragas 0.4.3 uses similarity strictly greater than 0.5. It does not judge factual correctness or semantic equivalence. |
| Ragas `non_llm_context_precision_with_reference` | Same as recall | Ranking-sensitive average precision over retrieved contexts, with similarity at least 0.5. This is not plain precision@k. |
| DeepEval `exact_match` | Case explicitly has `tags: ["exact-match"]` and a reference answer | Case-sensitive equality after trimming leading/trailing whitespace, with threshold 1. Suitable for canonical short answers; not open-ended prose. |
| Ragas `faithfulness` | Judge enabled; RAG case with answer and retrieved contexts | LLM decomposition and support checking against retrieved context. |
| Ragas `factual_correctness` | Judge enabled; nonempty answer and expected answer | LLM claim-based correctness against the reference, in F1 mode. |
| Ragas `llm_context_recall` | Judge enabled; RAG case with expected answer and retrieved contexts | Whether reference-answer claims are supported by retrieved contexts. |
| DeepEval `faithfulness` | Judge enabled; RAG case with answer and retrieved contexts | DeepEval claim/truth extraction and support checking using an explicit custom judge. |
| DeepEval `geval_correctness` | Judge enabled; nonempty answer and expected answer | GEval correctness rubric allowing paraphrases, with fixed evaluation steps. The custom judge has no log-probability weighting. |

A case is treated as RAG when its category contains `rag` (case-insensitive) or `expected.expected_context_ids` is nonempty. When that ID list is nonempty, only matching entries in `case.contexts` are gold references; supplied distractors are excluded. Without a list, all supplied contexts are reference material. Retrieved context order is preserved. Context IDs select gold text but are not used as a substitute for text similarity.

Empty context lists make Ragas context metrics `not_run`: its recall implementation raises on empty retrieval and cannot supply a meaningful framework score. The core kit must separately count retrieval failures, so an unavailable framework score cannot hide empty retrieval. Gold annotations must be complete and accurate; partial gold IDs reduce what these metrics measure.

Ragas's `SingleTurnSample`/`single_turn_ascore` API is a legacy API still available in 0.4.3. The pinned implementation uses it consistently, including a custom `BaseRagasLLM`; upgrading to Ragas 1.x requires migration. DeepEval is invoked directly through metric APIs without its hosted evaluation/reporting service. Both libraries' telemetry is disabled, and DeepEval `.env` and legacy keyfile loading are disabled before import.

## Explicit optional LLM judge

Judge mode makes real requests. It is never enabled automatically. Provide all three settings in the invoking process environment:

- `EVAL_JUDGE_API_KEY`: credential for the intended judge endpoint.
- `EVAL_JUDGE_BASE_URL`: OpenAI-compatible API root, such as `https://judge.example/v1`; the runner appends `/chat/completions`.
- `EVAL_JUDGE_MODEL`: explicit model identifier.

Use a shell/session secret mechanism; do not put credentials into a case file, command argument, or checked-in file. The preflight reports missing setting names only and never prints values. Existing `OPENAI_API_KEY` or provider defaults are not used.

```sh
.venv-ragas/bin/python integrations/framework_metrics.py \
  --framework ragas --input runs/framework-demo-01/framework-input.json --output runs/framework-demo-01/ragas-judge.json \
  --with-judge --max-cases 4 --max-requests 12 --timeout 20
```

The same flags apply to DeepEval. Defaults cap each subprocess at four applicable judge cases and twelve total HTTP requests. Offline metrics still run for every case. Later cases/metrics are marked `not_run` when limits are reached; a metric exhausting the budget midway is an error with a null score. Different framework subprocesses each have their own cap. Each HTTP operation has a 20-second timeout (configurable 1–60); callers should also impose a subprocess deadline for an overall wall-clock bound.

Endpoints must use HTTPS, except HTTP on `localhost` or a literal loopback IP. Userinfo, query strings, fragments, environment proxies, and redirects are rejected/disabled. There is no provider fallback or transport retry. HTTP errors (including 401), invalid responses, and connection failures disable further judge requests for that invocation. Errors contain a short safe diagnostic, never raw response bodies, prompts, headers, or credentials. Raw judge explanations are not persisted. Requests ask for JSON, use temperature 0 and a 2048-token output limit; endpoints/models must support these OpenAI-compatible options. Unsupported options become visible errors rather than silent model substitutions.

Judge scores remain probabilistic and sensitive to language, prompt injection in evaluated content, and reference quality. The system prompt instructs the judge to treat case content as data, but this is not a security guarantee. Review representative failures and calibrate score thresholds with human judgments before using them as release gates. No live provider result is claimed by the offline smoke verification.

## API references

- [Ragas context recall](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_recall/) and [context precision](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_precision/).
- [DeepEval exact match](https://deepeval.com/docs/metrics-exact-match) and [custom evaluation models](https://deepeval.com/guides/guides-using-custom-llms).

The installed pinned source was inspected for constructor signatures, empty-context behavior, whitespace handling, telemetry controls, and custom-model return types; stable online documentation can describe newer collection APIs.
