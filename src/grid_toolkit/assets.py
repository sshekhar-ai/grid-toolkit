from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path


class AssetDataError(Exception):
    """An asset record failed validation."""


@dataclass(frozen=True)
class Asset:
    asset_id: str
    kind: str
    voltage_kv: int


VALID_KINDS = {"substation", "feeder", "transformer"}


def parse_asset(line: str) -> Asset:
    parts = line.rstrip("\n").split(",")
    if len(parts) != 3:
        raise AssetDataError(f"expected 3 fields, got {len(parts)}: {line!r}")
    asset_id, kind, kv = (p.strip() for p in parts)
    if kind not in VALID_KINDS:
        raise AssetDataError(f"unknown kind {kind!r}")
    try:
        voltage = int(kv)
    except ValueError as e:
        raise AssetDataError(f"bad voltage {kv!r}") from e
    if voltage <= 0:
        raise AssetDataError("voltage must be positive")
    return Asset(asset_id, kind, voltage)


def read_assets(path: Path) -> Iterator[Asset]:
    with path.open(encoding="utf-8") as f:
        next(f, None)  # skip header (and handle empty files)
        for line in f:
            if line.strip():
                yield parse_asset(line)
