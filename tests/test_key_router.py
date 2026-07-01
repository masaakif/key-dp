from unittest.mock import MagicMock, patch
import pytest
from key_dp.key_router import KeyRouter


@pytest.fixture
def mock_keyboard():
    with patch("key_dp.key_router.keyboard") as mock_kb:
        yield mock_kb


def test_key_router_routing_without_ctrl(mock_keyboard):
    mock_kb = mock_keyboard
    mock_controller = MagicMock()
    router = KeyRouter(mock_controller, "Chrome", "NeeView")

    # Ctrlキーが押されていない状態
    mock_kb.is_pressed.return_value = False

    # イベントを模倣
    dummy_event = MagicMock()
    dummy_event.event_type = "down"  # keyboard.KEY_DOWN (通常 "down" となる文字列)
    dummy_event.name = "right"

    # keyboard.KEY_DOWN のモック定義
    mock_kb.KEY_DOWN = "down"

    router.on_arrow_key(dummy_event)

    # NeeViewにキーが送信されたことを確認
    mock_controller.send_key_to_window.assert_called_once_with("NeeView", "right")


def test_key_router_routing_with_ctrl(mock_keyboard):
    mock_kb = mock_keyboard
    mock_controller = MagicMock()
    router = KeyRouter(mock_controller, "Chrome", "NeeView")

    # Ctrlキーが押されている状態
    mock_kb.is_pressed.side_effect = lambda key: key == "ctrl"

    # イベントを模倣
    dummy_event = MagicMock()
    dummy_event.event_type = "down"
    dummy_event.name = "left"

    mock_kb.KEY_DOWN = "down"

    router.on_arrow_key(dummy_event)

    # Chromeに送信されたことを確認 (ctrl_pressedなし)
    mock_controller.send_key_to_window.assert_called_once_with("Chrome", "left")


def test_key_router_ignore_key_up(mock_keyboard):
    mock_kb = mock_keyboard
    mock_controller = MagicMock()
    router = KeyRouter(mock_controller, "Chrome", "NeeView")

    # イベントを模倣 (KEY_UP)
    dummy_event = MagicMock()
    dummy_event.event_type = "up"
    dummy_event.name = "left"

    mock_kb.KEY_DOWN = "down"

    router.on_arrow_key(dummy_event)

    # 送信されていないことを確認
    mock_controller.send_key_to_window.assert_not_called()
