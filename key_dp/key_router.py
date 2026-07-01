import keyboard
from .window_controller import WindowController


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
