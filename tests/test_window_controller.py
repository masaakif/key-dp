from unittest.mock import patch
import pytest
from key_dp.window_controller import WindowController


@pytest.fixture
def mock_win32():
    with (
        patch("key_dp.window_controller.win32gui") as mock_gui,
        patch("key_dp.window_controller.win32con") as mock_con,
        patch("key_dp.window_controller.pyautogui") as mock_pyauto,
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
