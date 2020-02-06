import pytest

from flatbot.notifications import Notifier
from flatbot.tracking.manager import Manager
from flatbot.tracking.tracker import Tracker, TrackerFactory


@pytest.fixture
def mock_tracker_factory(config, async_return, mocker, mock_storage, mock_scraper):
    def get_factory(tracker):
        factory = mocker.Mock(spec=TrackerFactory)
        factory.get.return_value = async_return(tracker)
        return factory
    return get_factory


@pytest.fixture
def mock_notifier(mocker):
    notifier = mocker.Mock(spec=Notifier)
    return notifier


@pytest.fixture
def mock_tracker(async_return, mocker):
    tracker = mocker.Mock(spec=Tracker)
    tracker.id = 1

    tracker.add.return_value = async_return(None)
    tracker.remove.return_value = async_return(None)
    tracker.cancel.return_value = async_return(None)
    tracker.active = False

    return tracker


async def test_manager(config, mock_tracker_factory, mock_tracker, mock_notifier):
    config = config('config_full.yml')
    factory = mock_tracker_factory(mock_tracker)
    manager = Manager(factory, mock_notifier, config)

    await manager.track('kuba', 'url')
    mock_tracker.add.assert_called_once_with('kuba')

    await manager.untrack('kuba', 'url')
    mock_tracker.remove.assert_called_once_with('kuba')
    mock_tracker.cancel.assert_called_once_with()


@pytest.mark.slow
def test_manager_db():
    # manager = Manager()
    pass
