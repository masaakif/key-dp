import time
import win32api
import win32con
import win32gui
import win32process

# 矢印キーからWindows仮想キーコードへのマッピング
KEY_MAPPING = {
    "left": win32con.VK_LEFT,
    "right": win32con.VK_RIGHT,
    "up": win32con.VK_UP,
    "down": win32con.VK_DOWN,
}


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

    def send_key_to_window(self, target_title: str, key_name: str):
        """特定のウィンドウを一瞬だけ最前面にしてキーを送り、元のウィンドウに即座に戻す"""
        # 現在アクティブなウィンドウを記憶
        current_hwnd = win32gui.GetForegroundWindow()

        # 対象のウィンドウを探す
        target_hwnd = self.get_window_handle(target_title)

        if not target_hwnd:
            print(f"ターゲットウィンドウが見つかりません: {target_title}")
            return

        vk_code = KEY_MAPPING.get(key_name.lower())
        if not vk_code:
            print(f"無効なキー名です: {key_name}")
            return

        # すでにアクティブなら、そのままキーを送信して終了
        if current_hwnd == target_hwnd:
            try:
                win32api.keybd_event(vk_code, 0, 0, 0)
                time.sleep(0.005)
                win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            except Exception as error:
                print(f"キー送信エラーが発生しました: {error}")
            return

        # 対象ウィンドウが最小化している場合は元に戻す
        if win32gui.IsIconic(target_hwnd):
            win32gui.ShowWindow(target_hwnd, win32con.SW_RESTORE)

        # フォーカス制御の制限を回避するため、スレッド入力をアタッチする
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
            # ターゲットウィンドウを最前面にする
            win32gui.SetForegroundWindow(target_hwnd)
            time.sleep(0.005)  # フォーカスが切り替わる最小限のウェイト

            # キーメッセージを送信
            win32api.keybd_event(vk_code, 0, 0, 0)
            time.sleep(0.005)
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.005)

            # 元のアクティブウィンドウにフォーカスを戻す
            if current_hwnd and win32gui.IsWindow(current_hwnd):
                win32gui.SetForegroundWindow(current_hwnd)

        except Exception as error:
            print(f"アクティブ化または送信中にエラーが発生しました: {error}")
        finally:
            # スレッド入力をデタッチする
            if attached:
                try:
                    win32api.AttachThreadInput(
                        current_thread_id, foreground_thread_id, False
                    )
                except Exception:
                    pass
