"""Central control of pseudorandom state used by the project."""

from __future__ import annotations

import os
import random

import numpy as np


DEFAULT_SEED = 474


def set_global_seed(seed: int = DEFAULT_SEED) -> None:
    """Seed every random-number generator currently used by the project."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
