import time
import win32con
import win32gui
import win32process
import keyboard
import pyautogui

# --- 設定 ---
# ターゲットとなるアプリのウィンドウタイトル（部分一致）
CHROME_TITLE = "Google Chrome"
NEEVIEW_TITLE = "NeeView"


def get_window_handle(title_part):
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


def send_key_to_window(target_title, key_name, ctrl_pressed=False):
    """特定のウィンドウを一時的に最前面にしてキーを送り、元のウィンドウに戻す"""
    # 現在アクティブなウィンドウを記憶
    current_hwnd = win32gui.GetForegroundWindow()

    # 対象のウィンドウを探す
    target_hwnd = get_window_handle(target_title)

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

    except Exception as e:
        print(f"エラーが発生しました: {e}")


def on_arrow_key(event):
    """矢印キーが押されたときのハンドラ"""
    # キーが押された瞬間（down）だけ処理する
    if event.event_type != keyboard.KEY_DOWN:
        return

    key_name = event.name  # 'left', 'right', 'up', 'down'

    # Ctrlキーが同時に押されているか確認
    if keyboard.is_pressed("ctrl"):
        print(f"Ctrl + {key_name} -> Chromeへ送信")
        send_key_to_window(CHROME_TITLE, key_name, ctrl_pressed=True)
    else:
        print(f"{key_name} -> NeeViewへ送信")
        send_key_to_window(NEEVIEW_TITLE, key_name, ctrl_pressed=False)


def main():
    print("キーイベントのルーティングを開始しました...")
    print("・Ctrl + 矢印キー -> Chromeへ送信")
    print("・矢印キー単体     -> NeeViewへ送信")
    print("※ 終了するには Esc キーを長押ししてください。")

    # 矢印キー（up, down, left, right）のイベントを横取り(suppress=Trueで元のキー入力を無効化)
    # これにより、現在アクティブな無関係なアプリに矢印が入力されるのを防ぎます
    keyboard.hook_key("left", on_arrow_key, suppress=True)
    keyboard.hook_key("right", on_arrow_key, suppress=True)
    keyboard.hook_key("up", on_arrow_key, suppress=True)
    keyboard.hook_key("down", on_arrow_key, suppress=True)

    # Escキーが押されるまでバックグラウンドで待機
    keyboard.wait("esc")

    # フックを解除して終了
    keyboard.unhook_all()
    print("アプリを終了しました。")


if __name__ == "__main__":
    main()