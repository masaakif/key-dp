from unittest.mock import patch
import pytest
from key_dp.window_controller import WindowController


@pytest.fixture
def mock_win32():
    with (
        patch("key_dp.window_controller.win32gui") as mock_gui,
        patch("key_dp.window_controller.win32con") as mock_con,
    ):
        yield mock_gui, mock_con


def test_get_window_handle_found(mock_win32):
    mock_gui, _ = mock_win32

    # enum_windows_callbackを模擬する
    def dummy_enum(callback, extra):
        callback(100, None)
        callback(200, None)

    mock_gui.EnumWindows.side_effect = dummy_enum
    mock_gui.IsWindowVisible.side_effect = lambda hwnd: True

    # 100はタイトルに "NeeView" なし (クラス名のみ "HwndWrapper[NeeView;;...]")
    # 200はタイトルに "Google Chrome" あり
    def dummy_get_text(hwnd):
        if hwnd == 100:
            return "Comic_File_Name.zip"
        elif hwnd == 200:
            return "Google Chrome - New Tab"
        return ""

    def dummy_get_class(hwnd):
        if hwnd == 100:
            return "HwndWrapper[NeeView;;abc]"
        elif hwnd == 200:
            return "Chrome_WidgetWin_1"
        return ""

    mock_gui.GetWindowText.side_effect = dummy_get_text
    mock_gui.GetClassName.side_effect = dummy_get_class

    # クラス名での部分一致
    handle = WindowController.get_window_handle("NeeView")
    assert handle == 100

    # タイトル名での部分一致
    handle_chrome = WindowController.get_window_handle("Chrome")
    assert handle_chrome == 200


def test_get_window_handle_not_found(mock_win32):
    mock_gui, _ = mock_win32

    def dummy_enum(callback, extra):
        callback(100, None)

    mock_gui.EnumWindows.side_effect = dummy_enum
    mock_gui.IsWindowVisible.side_effect = lambda hwnd: True
    mock_gui.GetWindowText.return_value = "Unrelated Window"
    mock_gui.GetClassName.return_value = "Unrelated Class"

    handle = WindowController.get_window_handle("NeeView")
    assert handle is None


def test_send_key_background(mock_win32):
    mock_gui, mock_con = mock_win32
    controller = WindowController()

    mock_con.VK_LEFT = 0x25
    mock_con.WM_KEYDOWN = 0x0100
    mock_con.WM_KEYUP = 0x0101

    with patch.object(WindowController, "get_window_handle", return_value=100):
        controller.send_key_to_window("NeeView", "left")

        # win32gui.PostMessage が WM_KEYDOWN と WM_KEYUP を伴って正しく呼び出されたか検証
        mock_gui.PostMessage.assert_any_call(100, 0x0100, 0x25, 1 | (1 << 24))
        mock_gui.PostMessage.assert_any_call(
            100, 0x0101, 0x25, 1 | (1 << 24) | (1 << 30) | (1 << 31)
        )
