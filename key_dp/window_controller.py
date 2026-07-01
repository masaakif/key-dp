import time
import win32con
import win32gui

# 矢印キーからWindows仮想キーコードへのマッピング
KEY_MAPPING = {
    "left": win32con.VK_LEFT,
    "right": win32con.VK_RIGHT,
    "up": win32con.VK_UP,
    "down": win32con.VK_DOWN,
}


class WindowController:
    """Windows上のウィンドウ探索やバックグラウンドでのキー送信を行うクラス"""

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
        """特定のウィンドウへ、アクティブ化を行わずに直接キーメッセージを送信する"""
        # 対象のウィンドウを探す
        target_hwnd = self.get_window_handle(target_title)

        if not target_hwnd:
            print(f"ターゲットウィンドウが見つかりません: {target_title}")
            return

        vk_code = KEY_MAPPING.get(key_name.lower())
        if not vk_code:
            print(f"無効なキー名です: {key_name}")
            return

        # 拡張キー（矢印キーなど）用のフラグを含めたlParam値の設定
        # 24ビット目（1 << 24）は拡張キーフラグ
        # 30ビット目（1 << 30）は直前の状態フラグ（Upのときは1）
        # 31ビット目（1 << 31）は遷移状態フラグ（Upのときは1）
        l_param_down = 1 | (1 << 24)
        l_param_up = 1 | (1 << 24) | (1 << 30) | (1 << 31)

        try:
            # 押下（WM_KEYDOWN）を送信
            win32gui.PostMessage(
                target_hwnd, win32con.WM_KEYDOWN, vk_code, l_param_down
            )
            time.sleep(0.01)  # メッセージの処理順序を保証するためのわずかなウェイト
            # 離上（WM_KEYUP）を送信
            win32gui.PostMessage(target_hwnd, win32con.WM_KEYUP, vk_code, l_param_up)
        except Exception as error:
            print(f"キー送信エラーが発生しました: {error}")
