from __future__ import annotations

from .transaction_errors import TransactionError
from .transaction_core import CoreMixin
from .transaction_plans import PlanningMixin
from .transaction_apply import ApplyMixin
from .transaction_ops import OpsMixin


class PackageManager(CoreMixin, PlanningMixin, ApplyMixin, OpsMixin):
    """Metadata registry + source resolver + target installer."""
    pass


__all__ = ["PackageManager", "TransactionError"]
