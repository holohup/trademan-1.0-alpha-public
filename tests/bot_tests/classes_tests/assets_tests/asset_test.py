import pytest
from tinkoff.invest import OrderExecutionReportStatus

from bot.tools.classes import Asset


@pytest.mark.parametrize(
    ('status', 'result'),
    (
        (OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_CANCELLED, False),
        (OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_FILL, False),
        (OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_NEW, True),
        (
            OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_PARTIALLYFILL,
            True,
        ),
    ),
)
def test_update_order_placed(sample_far_leg: Asset, mocker, status, result):
    sample_far_leg.order_placed = not result
    response = mocker.Mock()
    response.execution_report_status = status
    sample_far_leg._update_order_placed(response)
    assert sample_far_leg.order_placed is result
