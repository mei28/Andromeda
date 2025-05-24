from config.settings import settings 
from src.pose_estimator import PoseEstimator

def main():
    """
    Andromedaプロジェクトのメイン処理を開始する関数
    """
    # コマンドライン引数をパースし、設定をロード・上書き
    settings.parse_arguments() # これが設定のロードと引数のパースを行います

    print("\n--- Andromedaプロジェクトを開始します ---")
    print(f"入力動画パス: {settings.INPUT_VIDEO_PATH}")
    print(f"出力座標パス: {settings.PROCESSED_COORDS_PATH}")
    print(f"モデルの複雑さ: {settings.POSE_MODEL_COMPLEXITY}")
    print(f"GUI表示: {settings.DISPLAY_RESULTS}")
    print(f"座標保存: {settings.SAVE_PROCESSED_COORDINATES}")
    print(f"動画保存: {settings.SAVE_OUTPUT_VIDEO}")
    print("---------------------------------------")

    # 入力動画ファイルが存在するか確認
    if not settings.INPUT_VIDEO_PATH.exists():
        print(f"エラー: 入力動画ファイル '{settings.INPUT_VIDEO_PATH}' が見つかりません。")
        print(f"動画ファイルを '{settings.RAW_DATA_DIR}' フォルダに配置してください。")
        return

    try:
        with PoseEstimator() as estimator:
            estimator.process_video(settings.INPUT_VIDEO_PATH) # Path オブジェクトを渡す
        
        print("\n--- 処理結果 ---")
        if settings.SAVE_PROCESSED_COORDINATES:
            print(f"骨格座標データは '{settings.PROCESSED_COORDS_PATH}' に保存されました。")
        if settings.SAVE_OUTPUT_VIDEO:
            print(f"処理結果の動画は '{settings.OUTPUT_VIDEO_PATH}' に保存されました。")
        if not settings.DISPLAY_RESULTS:
            print("GUI表示は無効化されています。")
        
        print("Andromedaプロジェクトが正常に終了しました。")

    except IOError as e:
        print(f"エラーが発生しました: {e}")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")

if __name__ == '__main__':
    main()
