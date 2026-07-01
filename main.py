from key_dp.key_router import KeyRouter
from key_dp.window_controller import WindowController

# --- 設定 ---
# ターゲットとなるアプリのウィンドウタイトル（部分一致）
CHROME_TITLE = "Google Chrome"
NEEVIEW_TITLE = "NeeView"


def main():
    controller = WindowController()
    router = KeyRouter(controller, CHROME_TITLE, NEEVIEW_TITLE)
    router.start()


if __name__ == "__main__":
    main()
