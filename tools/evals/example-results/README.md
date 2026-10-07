# Synthetic demonstration snapshot

These files are the results of the included deterministic demo assistant against all 40 cases in [demo-cases.jsonl](../datasets/demo-cases.jsonl). They are documentation examples, not results for a new product and not live LLM evaluations.

The snapshot was generated on 2026-10-07 with Python 3.12 and fresh environments installed from the bundled dependency pins: Ragas 0.4.3 (24 offline metrics) and DeepEval 4.2.8 (7 exact-match metrics). All 40 contract cases passed and all 8 negative controls were detected. No LLM judge or target API was called. Runtime timings describe that particular local execution, not product performance.

- [HTML report](report.html)
- [Full evaluation result](results.json)
- [Responses for replay](responses.json)
- [Ragas output](ragas.json)
- [DeepEval output](deepeval.json)

Generate your own result in a new `runs/` directory. Keep the included examples separate from project evidence.
