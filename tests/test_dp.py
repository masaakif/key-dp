from unittest.mock import MagicMock, patch
import pytest
from dp import KeyRouter, WindowController


@pytest.fixture
def mock_win32():
    with (
        patch("dp.win32gui") as mock_gui,
        patch("dp.win32con") as mock_con,
        patch("dp.pyautogui") as mock_pyauto,
    ):
        yield mock_gui, mock_con, mock_pyauto


def test_get_window_handle_found(mock_win32):
    mock_gui, _, _ = mock_win32

    # enum_windows_callbackを模擬する
    def dummy_enum(callback, extra):
        # 2つのウィンドウハンドルがあるとする
        callback(100, None)
        callback(200, None)

    mock_gui.EnumWindows.side_effect = dummy_enum
    mock_gui.IsWindowVisible.side_effect = lambda hwnd: True

    # 100は "NeeView", 200は "Google Chrome" とする
    def dummy_get_text(hwnd):
        if hwnd == 100:
            return "NeeView v3.9"
        elif hwnd == 200:
            return "Google Chrome - New Tab"
        return ""

    mock_gui.GetWindowText.side_effect = dummy_get_text

    handle = WindowController.get_window_handle("NeeView")
    assert handle == 100

    handle_chrome = WindowController.get_window_handle("Chrome")
    assert handle_chrome == 200


def test_get_window_handle_not_found(mock_win32):
    mock_gui, _, _ = mock_win32

    def dummy_enum(callback, extra):
        callback(100, None)

    mock_gui.EnumWindows.side_effect = dummy_enum
    mock_gui.IsWindowVisible.side_effect = lambda hwnd: True
    mock_gui.GetWindowText.return_value = "Unrelated Window"

    handle = WindowController.get_window_handle("NeeView")
    assert handle is None


def test_send_key_to_active_window(mock_win32):
    mock_gui, _, mock_pyauto = mock_win32
    controller = WindowController()

    # 対象ウィンドウが既にアクティブな場合
    mock_gui.GetForegroundWindow.return_value = 100

    with patch.object(WindowController, "get_window_handle", return_value=100):
        controller.send_key_to_window("NeeView", "right", ctrl_pressed=False)
        mock_pyauto.press.assert_called_once_with("right")
        mock_pyauto.hotkey.assert_not_called()


def test_send_key_to_inactive_window(mock_win32):
    mock_gui, mock_con, mock_pyauto = mock_win32
    controller = WindowController()

    mock_gui.GetForegroundWindow.return_value = 200  # 現在のアクティブウィンドウ
    mock_gui.IsIconic.return_value = False
    mock_gui.IsWindow.return_value = True

    with patch.object(
        WindowController, "get_window_handle", return_value=100
    ) as mock_get_handle:
        controller.send_key_to_window("NeeView", "left", ctrl_pressed=False)
        mock_get_handle.assert_called_once_with("NeeView")
        mock_gui.SetForegroundWindow.assert_any_call(100)  # 対象を最前面に
        mock_pyauto.press.assert_called_once_with("left")
        mock_gui.SetForegroundWindow.assert_any_call(200)  # 元に戻す


def test_send_key_with_ctrl(mock_win32):
    mock_gui, _, mock_pyauto = mock_win32
    controller = WindowController()

    mock_gui.GetForegroundWindow.return_value = 100

    with patch.object(WindowController, "get_window_handle", return_value=100):
        controller.send_key_to_window("Google Chrome", "up", ctrl_pressed=True)
        mock_pyauto.hotkey.assert_called_once_with("ctrl", "up")
        mock_pyauto.press.assert_not_called()


@pytest.fixture
def mock_keyboard():
    with patch("dp.keyboard") as mock_kb:
        yield mock_kb


def test_key_router_routing_without_ctrl(mock_keyboard):
    mock_kb = mock_keyboard
    mock_controller = MagicMock()
    router = KeyRouter(mock_controller, "Chrome", "NeeView")

    # Ctrlキーが押されていない状態
    mock_kb.is_pressed.return_value = False

    # イベントを模倣
    dummy_event = MagicMock()
    dummy_event.event_type = "down"  # keyboard.KEY_DOWN (通常 "down" とする文字列)
    dummy_event.name = "right"

    # keyboard.KEY_DOWN のモック定義
    mock_kb.KEY_DOWN = "down"

    router.on_arrow_key(dummy_event)

    # NeeViewにキーが送信されたことを確認
    mock_controller.send_key_to_window.assert_called_once_with(
        "NeeView", "right", ctrl_pressed=False
    )


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

    # ChromeにCtrlキー付きで送信されたことを確認
    mock_controller.send_key_to_window.assert_called_once_with(
        "Chrome", "left", ctrl_pressed=True
    )


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
