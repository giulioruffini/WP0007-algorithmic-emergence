"""Independent finite checks and explicit implementation costs; run with Python 3."""

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import example_b_codec as model


def life_torus(cells, n):
    neighbors = Counter(((x + dx) % n, (y + dy) % n)
                        for x, y in cells for dx in (-1, 0, 1)
                        for dy in (-1, 0, 1) if dx or dy)
    return {p for p, k in neighbors.items() if k == 3 or (k == 2 and p in cells)}


def simulate(seed, n, count):
    frames = [seed]
    for _ in range(count - 1):
        frames.append(life_torus(frames[-1], n))
    return frames


def simulation_encode(frames, n):
    if frames == simulate(frames[0], n, len(frames)):
        return "0" + "".join("1" if (x, y) in frames[0] else "0"
                             for x in range(n) for y in range(n))
    return "1" + "".join("1" if (x, y) in frame else "0"
                         for frame in frames for x in range(n) for y in range(n))


def simulation_decode(bits, n, count):
    raw = bits[1:]
    frames = [{(x, y) for x in range(n) for y in range(n)
               if raw[t * n * n + x * n + y] == "1"}
              for t in range(1 if bits[0] == "0" else count)]
    return simulate(frames[0], n, count) if bits[0] == "0" else frames


cases = 0
for n in (8, 9, 16, 31, 32):
    for phase in range(4):
        for direction in range(4):
            for x, y in ((0, 0), (n - 1, n - 1), (n // 2, n - 2)):
                frames = model.trajectory(n, 4 * n + 9, x, y, phase, direction)
                assert frames == simulate(frames[0], n, len(frames))
                code = model.encode(frames, n)
                assert len(code) == 2 * (n - 1).bit_length() + 5
                assert model.decode(code, n, len(frames)) == frames
                cases += 1

n, count, residual_bits = 256, 32, 4096
training = model.trajectory(n, count, 9, 17, 0, 0)
test = model.trajectory(n, count, 113, 251, 3, 2)
assert training == simulate(training[0], n, count)
assert test == simulate(test[0], n, count)
train_code, test_code = model.encode(training, n), model.encode(test, n)
assert model.decode(train_code, n, count) == training
assert model.decode(test_code, n, count) == test
assert model.project((training[0], "0" * residual_bits)) == training[0]

escape = simulate({(0, 0), (1, 0), (2, 0)}, n, count)
escape_code = model.encode(escape, n)
assert escape_code[0] == "1"
assert model.decode(escape_code, n, count) == escape
assert len(escape_code) == 1 + n * n * count

for frames in (training, test, escape):
    baseline_code = simulation_encode(frames, n)
    assert len(baseline_code) == 1 + n * n
    assert simulation_decode(baseline_code, n, count) == frames
broken = [set(frame) for frame in training]
broken[-1].add((n // 2, n // 2))
baseline_escape = simulation_encode(broken, n)
assert baseline_escape[0] == "1"
assert len(baseline_escape) == 1 + n * n * count
assert simulation_decode(baseline_escape, n, count) == broken
assert model.decode(model.encode(broken, n), n, count) == broken

source = Path(model.__file__).read_bytes()
source_bytes = len(source)
length_header = 2 * ((source_bytes + 1).bit_length() - 1) + 1
acquisition = 8 * source_bytes + length_header
literal_baseline = n * n * count
simulation_baseline = 1 + n * n
complete = acquisition + len(train_code)
comp_margin = test_margin = 128
assert complete <= simulation_baseline - comp_margin
assert complete <= literal_baseline - comp_margin
assert len(test_code) <= simulation_baseline - test_margin
assert len(test_code) <= literal_baseline - test_margin

# A preinstalled sparse initial-state code changes the acquisition comparison.
live_cells = len(training[0])
count_header = 2 * ((live_cells + 1).bit_length() - 1) + 1
sparse_initial_bits = 1 + count_header + live_cells * 2 * (n - 1).bit_length()
assert sparse_initial_bits == 86
assert complete > sparse_initial_bits

# Both codes apply separately to runs; their counts and boundaries are shared.
sparse_saving_per_run = sparse_initial_bits - len(train_code)
repayment_runs = (acquisition + sparse_saving_per_run - 1) // sparse_saving_per_run
construction_runs = (acquisition + comp_margin + sparse_saving_per_run - 1) // sparse_saving_per_run
test_runs = (test_margin + sparse_saving_per_run - 1) // sparse_saving_per_run
assert (sparse_saving_per_run, repayment_runs, construction_runs, test_runs) == (65, 292, 294, 2)
assert (repayment_runs - 1) * sparse_saving_per_run < acquisition <= repayment_runs * sparse_saving_per_run
assert (construction_runs - 1) * sparse_saving_per_run - acquisition < comp_margin
assert construction_runs * sparse_saving_per_run - acquisition >= comp_margin
assert (test_runs - 1) * sparse_saving_per_run < test_margin <= test_runs * sparse_saving_per_run

# In a continuing run the shared final state supplies the next block's seed.
continuation = simulate(life_torus(training[-1], n), n, count)
continuation_code = model.encode(continuation, n)
assert model.decode(continuation_code, n, count) == continuation
assert len(continuation_code) == 21
shared_state_simulation_bits = 1
assert len(continuation_code) > shared_state_simulation_bits

result = {
    "torus_checks": cases,
    "n_side": n, "frames_per_block": count,
    "codec_source_bytes": source_bytes,
    "codec_sha256": sha256(source).hexdigest(),
    "self_delimiting_length_header_bits": length_header,
    "acquisition_bits": acquisition,
    "construction_coordinate_bits": len(train_code),
    "complete_retained_construction_bits": complete,
    "literal_baseline_bits": literal_baseline,
    "simulation_restart_baseline_bits": simulation_baseline,
    "sparse_initial_state_baseline_bits": sparse_initial_bits,
    "construction_saving_vs_sparse_bits": sparse_initial_bits - complete,
    "sparse_saving_per_restarted_run_bits": sparse_saving_per_run,
    "sparse_repayment_runs": repayment_runs,
    "sparse_saving_at_repayment_bits": repayment_runs * sparse_saving_per_run - acquisition,
    "sparse_construction_runs_for_margin": construction_runs,
    "sparse_construction_saving_at_margin_bits": construction_runs * sparse_saving_per_run - acquisition,
    "sparse_test_runs_for_margin": test_runs,
    "sparse_test_saving_at_margin_bits": test_runs * sparse_saving_per_run,
    "simulation_continuation_baseline_bits": shared_state_simulation_bits,
    "continuation_coordinate_bits": len(continuation_code),
    "continuation_saving_vs_simulation_bits": shared_state_simulation_bits - len(continuation_code),
    "construction_saving_vs_literal_bits": literal_baseline - complete,
    "construction_saving_vs_simulation_bits": simulation_baseline - complete,
    "test_coordinate_bits": len(test_code),
    "test_saving_vs_literal_bits": literal_baseline - len(test_code),
    "test_saving_vs_simulation_bits": simulation_baseline - len(test_code),
    "declared_comp_margin_bits": comp_margin,
    "declared_test_margin_bits": test_margin,
    "omitted_register_literal_bits": residual_bits,
    "full_reconstructed_construction_bits": complete + residual_bits,
    "full_original_literal_bits": (n * n + residual_bits) * count,
    "escape_bits": len(escape_code),
    "kolmogorov_complexity_estimated": False,
}
print(json.dumps(result, indent=2, sort_keys=True))
