import time
import win32con
import win32gui
import keyboard
import pyautogui

# --- 設定 ---
# ターゲットとなるアプリのウィンドウタイトル（部分一致）
CHROME_TITLE = "Google Chrome"
NEEVIEW_TITLE = "NeeView"


class WindowController:
    """Windows上のウィンドウ探索やアクティブ化、キー送信を行うクラス"""

    @staticmethod
    def get_window_handle(title_part: str):
        """指定した文字列をタイトルに含むウィンドウのハンドルを取得する"""
        hwnd_list = []

        def enum_windows_callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title_part.lower() in title.lower():
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


class KeyRouter:
    """キー入力を監視し、設定に基づき適切なウィンドウへキーをルーティングするクラス"""

    def __init__(
        self, window_controller: WindowController, chrome_title: str, neeview_title: str
    ):
        self.window_controller = window_controller
        self.chrome_title = chrome_title
        self.neeview_title = neeview_title

    def on_arrow_key(self, event):
        """矢印キーが押されたときのハンドラ"""
        # キーが押された瞬間（down）だけ処理する
        if event.event_type != keyboard.KEY_DOWN:
            return

        key_name = event.name  # 'left', 'right', 'up', 'down'

        # Ctrlキーが同時に押されているか確認
        if keyboard.is_pressed("ctrl"):
            print(f"Ctrl + {key_name} -> Chromeへ送信")
            self.window_controller.send_key_to_window(
                self.chrome_title, key_name, ctrl_pressed=True
            )
        else:
            print(f"{key_name} -> NeeViewへ送信")
            self.window_controller.send_key_to_window(
                self.neeview_title, key_name, ctrl_pressed=False
            )

    def start(self):
        """キーのルーティング処理を開始し、Escキーが長押しされるまで待機する"""
        print("キーイベントのルーティングを開始しました...")
        print("・Ctrl + 矢印キー -> Chromeへ送信")
        print("・矢印キー単体     -> NeeViewへ送信")
        print("※ 終了するには Esc キーを長押ししてください。")

        # 矢印キー（up, down, left, right）のイベントを横取り(suppress=Trueで元のキー入力を無効化)
        keyboard.hook_key("left", self.on_arrow_key, suppress=True)
        keyboard.hook_key("right", self.on_arrow_key, suppress=True)
        keyboard.hook_key("up", self.on_arrow_key, suppress=True)
        keyboard.hook_key("down", self.on_arrow_key, suppress=True)

        # Escキーが押されるまでバックグラウンドで待機
        keyboard.wait("esc")

        # フックを解除して終了
        keyboard.unhook_all()
        print("アプリを終了しました。")


def main():
    controller = WindowController()
    router = KeyRouter(controller, CHROME_TITLE, NEEVIEW_TITLE)
    router.start()


if __name__ == "__main__":
    main()
