import math


def adjust_uniform_single(values: list[float]) -> tuple[float, float]:
    n = len(values)
    adjusted = math.fsum(values) / n
    dev = math.sqrt(math.fsum([(v - adjusted)**2 for v in values]) / n)
    return adjusted, dev
