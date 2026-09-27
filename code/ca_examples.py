"""Exact CA records and explicit codes for Section 5.3; Python standard library only."""
from itertools import product
from pathlib import Path
import json
import random

CELLS, COARSE_STEPS, BLOCK = 360, 40, 3


def step(row, rule):
    n = len(row)
    return [(rule >> (4 * row[(j - 1) % n] + 2 * row[j] + row[(j + 1) % n])) & 1
            for j in range(n)]


def evolve(initial, steps, rule):
    rows = [list(initial)]
    for _ in range(steps):
        rows.append(step(rows[-1], rule))
    return rows


def project(row, table):
    return [(table >> (4 * row[j] + 2 * row[j + 1] + row[j + 2])) & 1
            for j in range(0, len(row), BLOCK)]


def initial_state(seed):
    rng, row = random.Random(seed), []
    while len(row) < CELLS:
        row.extend([1] * rng.randint(3, 40))
        row.extend([0] * rng.randint(2, 20))
    return row[:CELLS]


def observations(initial, table):
    return [project(row, table) for row in evolve(initial, BLOCK * COARSE_STEPS, 146)[::BLOCK]]


def gamma(number):
    assert number >= 1
    raw = f"{number:b}"
    return "0" * (len(raw) - 1) + raw


def read_gamma(bits, offset=0):
    zeros = 0
    while bits[offset + zeros] == "0":
        zeros += 1
    stop = offset + 2 * zeros + 1
    return int(bits[offset + zeros:stop], 2), stop


def acquire(table, rule):
    return gamma(8) + f"{table:08b}" + gamma(8) + f"{rule:08b}"


def decode_acquisition(bits):
    result, offset = [], 0
    for _ in range(2):
        length, offset = read_gamma(bits, offset)
        assert length == 8
        result.append(int(bits[offset:offset + length], 2))
        offset += length
    assert offset == len(bits)
    return tuple(result)


def flatten(rows):
    return [bit for row in rows for bit in row]


def model_encode(rows, rule):
    predicted = flatten(evolve(rows[0], len(rows) - 1, rule))
    errors = [j for j, (a, b) in enumerate(zip(flatten(rows), predicted)) if a != b]
    initial = "".join(map(str, rows[0]))
    if not errors:
        return "0" + initial
    width = (len(predicted) - 1).bit_length()
    return "1" + initial + gamma(len(errors) + 1) + "".join(f"{j:0{width}b}" for j in errors)


def model_decode(bits, rule, cells=CELLS // BLOCK, steps=COARSE_STEPS):
    initial = list(map(int, bits[1:cells + 1]))
    predicted = flatten(evolve(initial, steps, rule))
    offset = cells + 1
    if bits[0] == "1":
        count, offset = read_gamma(bits, offset)
        width = (len(predicted) - 1).bit_length()
        for _ in range(count - 1):
            index = int(bits[offset:offset + width], 2)
            predicted[index] ^= 1
            offset += width
    assert offset == len(bits)
    return [predicted[j:j + cells] for j in range(0, len(predicted), cells)]


def baseline_encode(initial):
    return "0" + "".join(map(str, initial))


def baseline_decode(bits, table):
    if bits[0] == "0":
        return observations(list(map(int, bits[1:])), table)
    width = CELLS // BLOCK
    return [list(map(int, bits[j:j + width])) for j in range(1, len(bits), width)]


def fit_rule(rows):
    errors = [sum(a != b for row, following in zip(rows, rows[1:])
                  for a, b in zip(step(row, rule), following)) for rule in range(256)]
    best = min(range(256), key=lambda rule: (errors[rule], rule))
    first, conflicts = {}, 0
    for row, following in zip(rows, rows[1:]):
        for j, output in enumerate(following):
            key = (row[(j - 1) % len(row)], row[j], row[(j + 1) % len(row)])
            if key in first and first[key] != output:
                conflicts += 1
            first.setdefault(key, output)
    return best, errors, conflicts


def local_closure(table):
    groups = {key: set() for key in product((0, 1), repeat=3)}
    for bits in product((0, 1), repeat=9):
        key = tuple(project(bits, table))
        # Shrink the complete light cone: its final three cells require no boundary data.
        row = list(bits)
        for _ in range(3):
            row = [(146 >> (4 * row[j - 1] + 2 * row[j] + row[j + 1])) & 1
                   for j in range(1, len(row) - 1)]
        groups[key].add(project(row, table)[0])
    return {"".join(map(str, key)): sorted(values) for key, values in groups.items()}


def evaluate(rows, table, rule):
    acquired = acquire(table, rule)
    assert decode_acquisition(acquired) == (table, rule)
    code = model_encode(rows, rule)
    assert model_decode(code, rule) == rows
    predicted = evolve(rows[0], COARSE_STEPS, rule)
    errors = sum(a != b for a, b in zip(flatten(rows), flatten(predicted)))
    return {"acquisition_bits": len(acquired), "coordinate_and_flag_bits": 1 + len(rows[0]),
            "correction_bits": len(code) - 1 - len(rows[0]), "errors_in_movie": errors,
            "retained_code_bits": len(acquired) + len(code), "reuse_code_bits": len(code),
            "baseline_bits": 1 + CELLS,
            "construction_saving_bits": 1 + CELLS - len(acquired) - len(code),
            "reuse_saving_bits": 1 + CELLS - len(code),
            "final_row_errors": sum(a != b for a, b in zip(rows[-1], predicted[-1]))}


def verify():
    # Independent Boolean expression for rule 146.
    for left, center, right in product((0, 1), repeat=3):
        value = ((1 - center) & (left ^ right)) | (left & center & right)
        assert value == ((146 >> (4 * left + 2 * center + right)) & 1)
    train, test = initial_state(7), initial_state(23)
    report = {"cells": CELLS, "coarse_steps": COARSE_STEPS, "microsteps_per_coarse_step": BLOCK,
              "training_seed": 7, "test_seed": 23, "literal_coarse_bits": 4920,
              "construction_margin_bits": 128, "test_margin_bits": 128,
              "seeds_supplied_to_decoders": False, "cases": {}}
    for name, table in (("AND", 128), ("OR", 254)):
        rows = observations(train, table)
        rule, one_step_errors, conflicts = fit_rule(rows)
        construction = evaluate(rows, table, rule)
        later = observations(test, table)
        reuse = evaluate(later, table, rule)
        assert baseline_decode(baseline_encode(train), table) == rows
        assert baseline_decode(baseline_encode(test), table) == later
        # Check both code branches on a record with one changed observed bit.
        altered = [row[:] for row in rows]
        altered[-1][0] ^= 1
        assert model_decode(model_encode(altered, rule), rule) == altered
        assert baseline_decode("1" + "".join(map(str, flatten(altered))), table) == altered
        shortest_in_family = min(30 + len(model_encode(rows, r)) for r in range(256))
        report["cases"][name] = {"projection_table": table, "selected_rule": rule,
            "selection_criterion": "minimum one-step bit errors, lowest rule number on ties",
            "one_step_errors": one_step_errors[rule], "neighborhoods_observed": 4800,
            "conflicts_against_first_successor": conflicts, "local_successors": local_closure(table),
            "construction": construction, "test": reuse,
            "minimum_construction_bits_over_256_rules_with_declared_correction_code": shortest_in_family}
    a, o = report["cases"]["AND"], report["cases"]["OR"]
    assert (a["selected_rule"], a["conflicts_against_first_successor"]) == (128, 0)
    assert all(outputs == [int(key == "111")] for key, outputs in a["local_successors"].items())
    assert (a["construction"]["retained_code_bits"], a["test"]["reuse_code_bits"]) == (151, 121)
    assert a["construction"]["construction_saving_bits"] >= 128
    assert a["test"]["reuse_saving_bits"] >= 128
    assert (o["selected_rule"], o["conflicts_against_first_successor"]) == (182, 1476)
    assert o["construction"]["errors_in_movie"] == 2022
    assert o["construction"]["correction_bits"] == 26307
    assert o["construction"]["final_row_errors"] == 54
    assert o["construction"]["construction_saving_bits"] < 0
    assert o["test"]["reuse_saving_bits"] < 0
    assert any(len(outputs) == 2 for outputs in o["local_successors"].values())
    return report


if __name__ == "__main__":
    output = verify()
    result_dir = Path(__file__).resolve().parents[1] / "results"
    if not result_dir.is_dir():
        result_dir = Path(__file__).parent
    (result_dir / "ca_examples_results.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))
