from unittest.mock import patch
import pytest
from key_dp.window_controller import WindowController


@pytest.fixture
def mock_win32():
    with (
        patch("key_dp.window_controller.win32gui") as mock_gui,
        patch("key_dp.window_controller.win32con") as mock_con,
        patch("key_dp.window_controller.pyautogui") as mock_pyauto,
        patch("key_dp.window_controller.win32api") as mock_api,
        patch("key_dp.window_controller.win32process") as mock_process,
    ):
        yield mock_gui, mock_con, mock_pyauto, mock_api, mock_process


def test_get_window_handle_found(mock_win32):
    mock_gui, _, _, _, _ = mock_win32

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
    mock_gui, _, _, _, _ = mock_win32

    def dummy_enum(callback, extra):
        callback(100, None)

    mock_gui.EnumWindows.side_effect = dummy_enum
    mock_gui.IsWindowVisible.side_effect = lambda hwnd: True
    mock_gui.GetWindowText.return_value = "Unrelated Window"
    mock_gui.GetClassName.return_value = "Unrelated Class"

    handle = WindowController.get_window_handle("NeeView")
    assert handle is None


def test_send_key_to_active_window(mock_win32):
    mock_gui, _, mock_pyauto, _, _ = mock_win32
    controller = WindowController()

    # 対象ウィンドウが既にアクティブな場合
    mock_gui.GetForegroundWindow.return_value = 100

    with patch.object(WindowController, "get_window_handle", return_value=100):
        controller.send_key_to_window("NeeView", "right", ctrl_pressed=False)
        mock_pyauto.press.assert_called_once_with("right")
        mock_pyauto.hotkey.assert_not_called()


def test_send_key_to_inactive_window(mock_win32):
    mock_gui, mock_con, mock_pyauto, mock_api, mock_process = mock_win32
    controller = WindowController()

    mock_gui.GetForegroundWindow.return_value = 200  # 現在のアクティブウィンドウ
    mock_gui.IsIconic.return_value = False
    mock_gui.IsWindow.return_value = True

    # スレッドアタッチが呼ばれることを期待
    mock_api.GetCurrentThreadId.return_value = 1111
    mock_process.GetWindowThreadProcessId.return_value = (2222, 3333)

    with patch.object(
        WindowController, "get_window_handle", return_value=100
    ) as mock_get_handle:
        controller.send_key_to_window("NeeView", "left", ctrl_pressed=False)
        mock_get_handle.assert_called_once_with("NeeView")

        # 最前面化する処理が呼ばれたことをアサート
        mock_gui.SetForegroundWindow.assert_any_call(100)
        mock_pyauto.press.assert_called_once_with("left")
        mock_gui.SetForegroundWindow.assert_any_call(200)

        # アタッチおよび解除が正常に呼び出されたか検証
        mock_api.AttachThreadInput.assert_any_call(1111, 2222, True)
        mock_api.AttachThreadInput.assert_any_call(1111, 2222, False)


def test_send_key_with_ctrl(mock_win32):
    mock_gui, _, mock_pyauto, _, _ = mock_win32
    controller = WindowController()

    mock_gui.GetForegroundWindow.return_value = 100

    with patch.object(WindowController, "get_window_handle", return_value=100):
        controller.send_key_to_window("Google Chrome", "up", ctrl_pressed=True)
        mock_pyauto.hotkey.assert_called_once_with("ctrl", "up")
        mock_pyauto.press.assert_not_called()
