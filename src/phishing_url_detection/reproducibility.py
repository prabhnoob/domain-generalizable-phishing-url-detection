from __future__ import annotations

import random

import numpy as np


DEFAULT_SEED = 474


def set_global_seed(seed: int = DEFAULT_SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
