"""Reproduce and assert every number in the two worked-example coding tables."""
from pathlib import Path
import json
import subprocess
import sys

if not __debug__:
    raise RuntimeError("Run without -O: the numerical assertions must remain enabled.")
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "code"))
import ca_examples

raw = subprocess.check_output([sys.executable, str(ROOT / "code/check_example_b.py")], text=True)
glider = json.loads(raw)
ca = ca_examples.verify()
for name, actual in (("example_b_results", glider), ("ca_examples_results", ca)):
    expected = json.loads((ROOT / "results" / (name + ".json")).read_text())
    assert actual == expected, name + " differs from the recorded values"

runs, tests = glider["sparse_construction_runs_for_margin"], glider["sparse_test_runs_for_margin"]
cost, coords, base = glider["acquisition_bits"], glider["construction_coordinate_bits"], glider["sparse_initial_state_baseline_bits"]
glider_table = {
    "construction_runs": runs, "test_runs": tests,
    "acquisition": [cost, 0], "coordinates": [runs * coords, tests * coords],
    "corrections": [0, 0], "complete_code": [cost + runs * coords, tests * coords],
    "baseline": [runs * base, tests * base],
    "saving": [runs * (base - coords) - cost, tests * (base - coords)], "margin": [128, 128]}
ca_table = {}
for name in ("AND", "OR"):
    record = ca["cases"][name]
    first, later = record["construction"], record["test"]
    ca_table[name] = {"rule": record["selected_rule"],
        "acquisition": first["acquisition_bits"], "coordinates": first["coordinate_and_flag_bits"],
        "construction_corrections": first["correction_bits"],
        "complete_construction": first["retained_code_bits"], "baseline": first["baseline_bits"],
        "construction_saving": first["construction_saving_bits"],
        "test_corrections": later["correction_bits"], "complete_test": later["reuse_code_bits"],
        "test_saving": later["reuse_saving_bits"]}
tables = {"glider": glider_table, "cellular_automaton": ca_table}
assert tables == json.loads((ROOT / "results/paper_tables.json").read_text()), "A printed table entry changed"
print(json.dumps({"all_checks_passed": True, "paper_tables": tables}, indent=2))
