import time
import win32api
import win32con
import win32gui
import win32process
import pyautogui


class WindowController:
    """Windows上のウィンドウ探索やアクティブ化、キー送信を行うクラス"""

    @staticmethod
    def get_window_handle(title_part: str):
        """指定した文字列をタイトルまたはクラス名に含むウィンドウのハンドルを取得する"""
        hwnd_list = []

        def enum_windows_callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                # タイトルまたはクラス名のいずれかに指定文字列が含まれているか判定
                if (title_part.lower() in title.lower()) or (
                    title_part.lower() in class_name.lower()
                ):
                    hwnd_list.append(hwnd)
            return True

        win32gui.EnumWindows(enum_windows_callback, None)
        return hwnd_list[0] if hwnd_list else None

    def send_key_to_window(
        self, target_title: str, key_name: str, ctrl_pressed: bool = False
    ):
        """特定のウィンドウを一時的に最前面にしてキーを送り、元のウィンドウに戻す"""
        # 現在アクティブなウィンドウを記憶
        current_hwnd = win32gui.GetForegroundWindow()

        # 対象のウィンドウを探す
        target_hwnd = self.get_window_handle(target_title)

        if not target_hwnd:
            print(f"ターゲットウィンドウが見つかりません: {target_title}")
            return

        # 対象ウィンドウがすでにアクティブならそのままキーを送る
        if current_hwnd == target_hwnd:
            if ctrl_pressed:
                pyautogui.hotkey("ctrl", key_name)
            else:
                pyautogui.press(key_name)
            return

        # 対象ウィンドウを最前面化（非最小化）
        if win32gui.IsIconic(target_hwnd):
            win32gui.ShowWindow(target_hwnd, win32con.SW_RESTORE)

        # 最前面化する際の制限（SetForegroundWindowの失敗）を回避するため、
        # 現在アクティブなスレッドの入力を結合する
        current_thread_id = win32api.GetCurrentThreadId()
        foreground_thread_id = (
            win32process.GetWindowThreadProcessId(current_hwnd)[0]
            if current_hwnd
            else 0
        )

        attached = False
        if foreground_thread_id and foreground_thread_id != current_thread_id:
            try:
                win32api.AttachThreadInput(
                    current_thread_id, foreground_thread_id, True
                )
                attached = True
            except Exception:
                pass

        try:
            # ウィンドウをアクティブにする
            win32gui.SetForegroundWindow(target_hwnd)
            time.sleep(0.01)  # フォーカス切り替えのわずかな遊び

            # キーを送信
            if ctrl_pressed:
                pyautogui.hotkey("ctrl", key_name)
            else:
                pyautogui.press(key_name)

            time.sleep(0.01)

            # 元のウィンドウにフォーカスを戻す
            if current_hwnd and win32gui.IsWindow(current_hwnd):
                win32gui.SetForegroundWindow(current_hwnd)

        except Exception as error:
            print(f"エラーが発生しました: {error}")
        finally:
            # 入力の結合を解除する
            if attached:
                try:
                    win32api.AttachThreadInput(
                        current_thread_id, foreground_thread_id, False
                    )
                except Exception:
                    pass
