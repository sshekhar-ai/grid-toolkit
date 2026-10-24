import dataclasses

import pytest

from grid_toolkit.assets import Asset, AssetDataError, parse_asset, read_assets


@pytest.fixture
def asset_file(tmp_path):
    p = tmp_path / "assets.csv"
    p.write_text("asset_id,kind,voltage_kv\nS1,substation,132\nF1,feeder,11\n", encoding="utf-8")
    return p


def test_reads_all_assets(asset_file):
    assert list(read_assets(asset_file)) == [
        Asset("S1", "substation", 132),
        Asset("F1", "feeder", 11),
    ]


def test_empty_file_yields_nothing(tmp_path):
    p = tmp_path / "empty.csv"
    p.write_text("", encoding="utf-8")
    assert list(read_assets(p)) == []


@pytest.mark.parametrize(
    "line",
    [
        "S1,substation",  # too few fields
        "S1,pylon,132",  # unknown kind
        "S1,substation,abc",  # not a number
        "S1,substation,-5",  # not positive
    ],
)
def test_bad_lines_raise(line):
    with pytest.raises(AssetDataError):
        parse_asset(line)


def test_blank_line_in_middle_is_skipped(tmp_path):
    p = tmp_path / "assets.csv"
    p.write_text("asset_id,kind,voltage_kv\nS1,substation,132\n\nF1,feeder,11\n", encoding="utf-8")
    assert list(read_assets(p)) == [
        Asset("S1", "substation", 132),
        Asset("F1", "feeder", 11),
    ]


def test_asset_is_immutable():
    asset = Asset("S1", "substation", 132)
    with pytest.raises(dataclasses.FrozenInstanceError):
        asset.voltage_kv = 33
