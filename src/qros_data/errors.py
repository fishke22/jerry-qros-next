from __future__ import annotations


class FailClosedError(RuntimeError):
    """Raised when required evidence is unknown or inconsistent."""


class DataQualityError(FailClosedError):
    def __init__(self, reasons: list[str]):
        self.reasons = tuple(reasons)
        super().__init__("; ".join(self.reasons))
