import pytest
from base.models import Spread


@pytest.mark.django_db
def test_ratio(sample_spread):
    assert sample_spread.ratio == 100
    sample_spread.editable_ratio = 10
    assert sample_spread.ratio == 10
    sample_spread.editable_ratio = 0
    assert sample_spread.ratio == 100
    sample_spread.near_leg.asset_type = 'F'
    sample_spread.far_leg.basic_asset = '33'
    assert sample_spread.ratio == 1


@pytest.mark.django_db
def test_averages_default_is_zero(sample_spread: Spread):
    assert sample_spread.avg_exec_price == 0


@pytest.mark.django_db
def test_averages_with_reallife_values(sample_spread: Spread):
    sample_spread.stats.far_leg_executed = 10
    sample_spread.stats.near_leg_executed = 20
    sample_spread.stats.far_leg_avg_price = 100
    sample_spread.stats.near_leg_avg_price = 200
    assert sample_spread.avg_exec_price == -300
