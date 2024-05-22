from dataclasses import dataclass


@dataclass(frozen=True)
class Mensa:
    """Data class for a Mensa object."""

    mensaId: str
