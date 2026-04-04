from __future__ import annotations

from pathlib import Path
from typing import Any


class IRSPacketRenderer:
    """
    Contract-aligned renderer for building an IRS packet artifact.

    Goal right now:
    - prevent import failure
    - keep export pipeline stable
    - create a predictable output artifact
    - allow later upgrade to real PDF merge/render logic
    """

    def __init__(self, output_dir: str | Path | None = None, *args, **kwargs) -> None:
        # Flexible init so existing caller code does not break
        if output_dir is None:
            output_dir = kwargs.get("output_dir", "data/output")
        self.output_dir = Path(output_dir)

    def render(self, case: Any) -> Path:
        """
        Build a placeholder IRS packet file.
        This preserves the pipeline contract until full PDF packet assembly is added.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        case_id = getattr(case, "case_id", None)
        if case_id is None and isinstance(case, dict):
            case_id = case.get("case_id", "UNKNOWN_CASE")
        if not case_id:
            case_id = "UNKNOWN_CASE"

        out_path = self.output_dir / f"{case_id}_irs_packet.txt"

        federal_return = getattr(case, "federal_return", None)
        if federal_return is None and isinstance(case, dict):
            federal_return = case.get("federal_return", {})

        total_income = self._safe_get(federal_return, "total_income")
        agi = self._safe_get(federal_return, "agi")
        taxable_income = self._safe_get(federal_return, "taxable_income")
        total_tax = self._safe_get(federal_return, "total_tax")
        refund = self._safe_get(federal_return, "refund")
        balance_due = self._safe_get(federal_return, "balance_due")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(f"IRS Packet Placeholder\n")
            f.write(f"Case ID: {case_id}\n")
            f.write(f"Total Income: {total_income}\n")
            f.write(f"AGI: {agi}\n")
            f.write(f"Taxable Income: {taxable_income}\n")
            f.write(f"Total Tax: {total_tax}\n")
            f.write(f"Refund: {refund}\n")
            f.write(f"Balance Due: {balance_due}\n")

        return out_path

    @staticmethod
    def _safe_get(obj: Any, key: str, default: Any = 0) -> Any:
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)