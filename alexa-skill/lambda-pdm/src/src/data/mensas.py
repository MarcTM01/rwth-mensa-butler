"""Defines a data-class for a mensa object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Mensa:
    """Data class for a Mensa object."""

    mensa_id: str
