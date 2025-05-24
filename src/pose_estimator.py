import cv2
import mediapipe as mp
import csv
from pathlib import Path 

# settings を直接インポート
from config.settings import settings
from src.utils import draw_pose_landmarks, get_landmark_coordinates, get_landmark_header_row

class PoseEstimator:
    """
    MediaPipe Pose を使用して動画から骨格を推定し、結果を処理するクラス
    """
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=settings.POSE_STATIC_IMAGE_MODE,
            model_complexity=settings.POSE_MODEL_COMPLEXITY,
            enable_segmentation=False,
            min_detection_confidence=settings.POSE_MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=settings.POSE_MIN_TRACKING_CONFIDENCE
        )
        self.output_csv_file = None # CSVファイルオブジェクト

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pose.close()
        if self.output_csv_file:
            self.output_csv_file.close()

    def _initialize_csv_writer(self):
        """CSVファイルにヘッダーを書き込み、ファイルオブジェクトを保持する"""
        if settings.SAVE_PROCESSED_COORDINATES:
            settings.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True) # ディレクトリ存在確認
            # pathlib.Path オブジェクトを open に直接渡す
            self.output_csv_file = open(settings.PROCESSED_COORDS_PATH, 'w', newline='')
            csv_writer = csv.writer(self.output_csv_file)
            csv_writer.writerow(get_landmark_header_row())
            return csv_writer
        return None

    def process_video(self, video_path: Path): # video_path を Path オブジェクトとして受け取る
        """
        指定された動画ファイルから骨格推定を行い、結果を処理するメインメソッド

        Args:
            video_path (pathlib.Path): 入力動画ファイルのパス
        """
        cap = cv2.VideoCapture(str(video_path)) # OpenCVは文字列パスを要求するため str() に変換
        if not cap.isOpened():
            raise IOError(f"動画ファイル '{video_path}' を開けませんでした。")

        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        out_video = None
        if settings.SAVE_OUTPUT_VIDEO:
            settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True) # ディレクトリ存在確認
            fourcc = cv2.VideoWriter_fourcc(*settings.OUTPUT_VIDEO_FOURCC)
            # pathlib.Path オブジェクトを str() に変換して渡す
            out_video = cv2.VideoWriter(str(settings.OUTPUT_VIDEO_PATH), fourcc, fps, (frame_width, frame_height))

        csv_writer = self._initialize_csv_writer()
        
        frame_count = 0
        print(f"動画 '{video_path.name}' の処理を開始します...") # .name でファイル名を取得

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            # print(f"フレーム {frame_count} を処理中...")

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False

            results = self.pose.process(image_rgb)

            image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
            image_rgb.flags.writeable = True

            if results.pose_landmarks:
                drawn_image = draw_pose_landmarks(image_bgr.copy(), results.pose_landmarks)
                
                if csv_writer:
                    coords = get_landmark_coordinates(results.pose_landmarks, frame_width, frame_height)
                    row_data = [str(frame_count)]
                    for i in range(len(self.mp_pose.PoseLandmark)):
                        lm_data = coords.get(i, {'x': None, 'y': None, 'z': None, 'visibility': None})
                        row_data.extend([
                            f'{lm_data["x"]:.6f}' if lm_data["x"] is not None else '',
                            f'{lm_data["y"]:.6f}' if lm_data["y"] is not None else '',
                            f'{lm_data["z"]:.6f}' if lm_data["z"] is not None else '',
                            f'{lm_data["visibility"]:.6f}' if lm_data["visibility"] is not None else ''
                        ])
                    csv_writer.writerow(row_data)
            else:
                drawn_image = image_bgr
                if csv_writer:
                    row_data = [str(frame_count)] + [''] * (len(self.mp_pose.PoseLandmark) * 4)
                    csv_writer.writerow(row_data)

            if settings.DISPLAY_RESULTS:
                cv2.imshow('MediaPipe Pose: Andromeda Project', drawn_image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("ユーザーによって中断されました。")
                    break

            if settings.SAVE_OUTPUT_VIDEO and out_video:
                out_video.write(drawn_image)

        print(f"動画の処理が完了しました。総フレーム数: {frame_count}")
        
        cap.release()
        if out_video:
            out_video.release()
        if settings.DISPLAY_RESULTS:
            cv2.destroyAllWindows()
