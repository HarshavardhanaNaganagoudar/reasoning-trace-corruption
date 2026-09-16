# Reasoning Trace Corruption

A small experiment using local LLMs to study how models respond when their reasoning is **prefilled with a convincing but incorrect reasoning trace**.

The model is given a problem and a corrupted "previous reasoning" trace, then asked to continue from where it supposedly left off.

## Hypothesis

Does the model:

* continue the corrupted reasoning?
* detect the error and correct it?
* silently recover the correct answer?

## Experiment

```text
Problem
   ↓
Corrupted reasoning trace
   ↓
"Continue from here"
   ↓
Model reasoning
   ↓
Final answer
```

Each run is saved separately so repeated trials can be compared.

## Example

```text
17 × 23
= 17 × (20 + 3)
= 340 + 50
= 390
```

The model is then asked to continue from this point.

Ground truth: `391`

## Setup

* Python
* Ollama
* Gemma 4 12B

Install:

```bash
pip install -r requirements.txt
```

Run:

```bash
python experiment.py
```

Change the number of repetitions in:

```python
RUNS = 5
```

## Output

```text
outputs/
├── run_01/
├── run_02/
├── run_03/
└── ...
```

Each run stores the model's reasoning, final answer, and correctness result.

## Goal

Measure how strongly a corrupted reasoning trajectory influences the model's subsequent reasoning.
