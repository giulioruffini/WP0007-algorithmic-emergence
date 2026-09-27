"""Charged source for the proposed glider example; all lengths count this file."""


def project(state):
    return state[0]


def step(cells):
    counts = {}
    for x, y in cells:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    p = (x + dx, y + dy)
                    counts[p] = counts.get(p, 0) + 1
    return {p for p, k in counts.items() if k == 3 or (k == 2 and p in cells)}


def rotate(point, direction):
    x, y = point
    for _ in range(direction):
        x, y = -y, x
    return x, y


PHASES = [{(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)}]
for _ in range(3):
    PHASES.append(step(PHASES[-1]))


def trajectory(n, count, x, y, phase, direction):
    vx, vy = rotate((1, 1), direction)
    frames = []
    for t in range(count):
        q, p = divmod(t + phase, 4)
        shape = [rotate(cell, direction) for cell in PHASES[p]]
        frames.append({((a + x + q * vx) % n, (b + y + q * vy) % n)
                       for a, b in shape})
    return frames


def literal(frames, n):
    return "".join("1" if (x, y) in frame else "0"
                   for frame in frames for x in range(n) for y in range(n))


def encode(frames, n):
    width = (n - 1).bit_length()
    if len(frames[0]) == 5:
        ax, ay = min(frames[0])
        for direction in range(4):
            for phase in range(4):
                for cell in sorted(PHASES[phase]):
                    bx, by = rotate(cell, direction)
                    x, y = (ax - bx) % n, (ay - by) % n
                    if trajectory(n, len(frames), x, y, phase, direction) == frames:
                        return ("0" + format(x, f"0{width}b")
                                + format(y, f"0{width}b")
                                + format(phase, "02b") + format(direction, "02b"))
    return "1" + literal(frames, n)


def decode(bits, n, count):
    width = (n - 1).bit_length()
    if bits[0] == "0":
        x = int(bits[1:1 + width], 2)
        y = int(bits[1 + width:1 + 2 * width], 2)
        phase = int(bits[1 + 2 * width:3 + 2 * width], 2)
        direction = int(bits[3 + 2 * width:5 + 2 * width], 2)
        return trajectory(n, count, x, y, phase, direction)
    raw = bits[1:]
    return [{(x, y) for x in range(n) for y in range(n)
             if raw[t * n * n + x * n + y] == "1"} for t in range(count)]
