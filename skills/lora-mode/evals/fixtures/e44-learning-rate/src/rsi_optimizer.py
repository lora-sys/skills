"""Tiny deterministic-seed training task for bounded learning-rate experiments."""

import random

DEFAULT_LR = 0.05
TRAIN_TARGETS = (0.7, 0.9, 1.0, 1.1, 1.3)
VALIDATION_TARGETS = (0.8, 1.0, 1.2)
STEPS = 8


def train(learning_rate: float, seed: int) -> float:
    rng = random.Random(seed)
    weight = 0.0
    for _ in range(STEPS):
        target = rng.choice(TRAIN_TARGETS)
        weight -= learning_rate * 2.0 * (weight - target)
    return weight


def validation_loss(weight: float) -> float:
    return sum((weight - target) ** 2 for target in VALIDATION_TARGETS) / len(VALIDATION_TARGETS)


def mean_validation_loss(learning_rate: float, seeds=(11, 23, 37, 41, 59)) -> float:
    return sum(validation_loss(train(learning_rate, seed)) for seed in seeds) / len(seeds)
