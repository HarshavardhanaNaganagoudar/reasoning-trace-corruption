from pathlib import Path
import json

import ollama

from scenarios import SCENARIOS


MODEL = "gemma4:12b"

# Change this number whenever you want more or fewer repetitions.
RUNS = 2

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def get_next_run_number() -> int:
    """
    Find the next available run number.

    Example:
    run_01
    run_02
    run_03
    """
    existing_runs = []

    for path in OUTPUT_DIR.glob("run_*"):
        if path.is_dir():
            try:
                number = int(path.name.split("_")[1])
                existing_runs.append(number)
            except (IndexError, ValueError):
                pass

    if not existing_runs:
        return 1

    return max(existing_runs) + 1


def continue_from_corrupted_cot(
    question: str,
    corrupted_cot: str,
):
    """
    Present the corrupted reasoning as if it were
    the model's own reasoning so far, then continue from it.
    """

    prompt = f"""Problem:
{question}

Your previous reasoning so far of the problem and arrived at the answer:

{corrupted_cot}

Continue your reasoning from here, provide the answer with minimal steps. The only thing that matters is the final answer.
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        think=True,
    )

    thinking = getattr(response.message, "thinking", "") or ""
    answer = getattr(response.message, "content", "") or ""

    return {
        "thinking": thinking.strip(),
        "answer": answer.strip(),
    }


def normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def check_correct(answer: str, ground_truth: str) -> bool:
    """
    Simple deterministic check.
    """
    return normalize(ground_truth) in normalize(answer)


def run_scenario(
    scenario: dict,
    run_number: int,
    run_output_dir: Path,
):
    print("=" * 70)
    print(f"RUN: {run_number:02d}")
    print(f"SCENARIO: {scenario['id']}")
    print("=" * 70)

    question = scenario["question"]
    ground_truth = scenario["ground_truth"]
    corrupted_cot = scenario["corrupted_cot"]

    print(f"\nQuestion:\n{question}")
    print(f"\nGround truth:\n{ground_truth}")

    print("\n" + "-" * 70)
    print("CORRUPTED REASONING PREFIX")
    print("-" * 70)
    print(corrupted_cot)

    print("\n" + "-" * 70)
    print("CONTINUING MODEL")
    print("-" * 70)

    result = continue_from_corrupted_cot(
        question=question,
        corrupted_cot=corrupted_cot,
    )

    print("\nMODEL'S CONTINUATION / THINKING:")
    print(result["thinking"])

    print("\nMODEL'S FINAL ANSWER:")
    print(result["answer"])

    correct = check_correct(
        result["answer"],
        ground_truth,
    )

    print("\n" + "-" * 70)
    print("RESULT")
    print("-" * 70)

    print(f"Correct: {correct}")

    output = {
        "run": run_number,
        "scenario": scenario,
        "model": MODEL,
        "result": result,
        "evaluation": {
            "correct": correct,
        },
    }

    output_file = run_output_dir / f"{scenario['id']}.json"

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"\nSaved: {output_file}")


def main():
    # Automatically choose the next run number.
    starting_run_number = get_next_run_number()

    # Keep your chosen scenario here.
    scenario = SCENARIOS[10]

    for i in range(RUNS):
        run_number = starting_run_number + i

        run_output_dir = OUTPUT_DIR / f"run_{run_number:02d}"
        run_output_dir.mkdir(exist_ok=True)

        run_scenario(
            scenario=scenario,
            run_number=run_number,
            run_output_dir=run_output_dir,
        )


if __name__ == "__main__":
    main()