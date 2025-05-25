import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import csv
from pathlib import Path

# MediaPipe ImageFormat を安全にインポートする
try:
    from mediapipe import ImageFormat
except ImportError:
    try:
        from mediapipe.framework.formats import image_format_pb2 as mp_image_format

        ImageFormat = mp_image_format.ImageFormat
    except ImportError:
        print("Warning: Could not import MediaPipe ImageFormat. Attempting to create mp.Image without explicit format.")
        ImageFormat = None

from config.settings import settings
from src.utils import draw_pose_landmarks, get_landmark_coordinates, get_landmark_header_row


class PoseEstimator:
    """
    MediaPipe PoseLandmarker を使用して動画から骨格を推定し、結果を処理するクラス
    """

    def __init__(self):
        base_options = python.BaseOptions(model_asset_path=str(settings.POSE_MODEL_PATH))

        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode[settings.POSE_RUNNING_MODE],
        )

        self.landmarker = vision.PoseLandmarker.create_from_options(options)
        self.output_csv_file = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.landmarker.close()
        if self.output_csv_file:
            self.output_csv_file.close()

    def _initialize_csv_writer(self):
        if settings.SAVE_PROCESSED_COORDINATES:
            settings.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
            self.output_csv_file = open(settings.PROCESSED_COORDS_PATH, "w", newline="")
            csv_writer = csv.writer(self.output_csv_file)
            csv_writer.writerow(get_landmark_header_row())
            return csv_writer
        return None

    def process_video(self, video_path: Path):
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise IOError(f"動画ファイル '{video_path}' を開けませんでした。")

        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        # --- ここが修正点 ---
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # CAP_PROP_HEIGHT を CAP_PROP_FRAME_HEIGHT に変更
        # --------------------
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        out_video = None
        if settings.SAVE_OUTPUT_VIDEO:
            settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            fourcc = cv2.VideoWriter_fourcc(*settings.OUTPUT_VIDEO_FOURCC)
            out_video = cv2.VideoWriter(str(settings.OUTPUT_VIDEO_PATH), fourcc, fps, (frame_width, frame_height))

        csv_writer = self._initialize_csv_writer()

        frame_timestamp_ms = 0
        print(f"動画 '{video_path.name}' の処理を開始します...")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if ImageFormat:
                mp_image = mp.Image(image_format=ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                mp_image = mp.Image(data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            detection_result = self.landmarker.detect_for_video(mp_image, frame_timestamp_ms)

            drawn_image = frame.copy()

            if detection_result.pose_landmarks:
                first_person_landmarks = detection_result.pose_landmarks[0]

                # ★ 0.10 系: container.NormalizedLandmark → proto.NormalizedLandmark ★
                from mediapipe.framework.formats import landmark_pb2
                from mediapipe.tasks.python.components.containers import landmark as container_lm

                def to_proto(container: container_lm.NormalizedLandmark):
                    return landmark_pb2.NormalizedLandmark(
                        x=container.x,
                        y=container.y,
                        z=container.z,
                        visibility=getattr(container, "visibility", 0.0),
                        presence=getattr(container, "presence", 0.0),
                    )

                if isinstance(first_person_landmarks, list):
                    first_person_landmarks = landmark_pb2.NormalizedLandmarkList(
                        landmark=[to_proto(lm) for lm in first_person_landmarks]
                    )

                drawn_image = draw_pose_landmarks(drawn_image, first_person_landmarks)

                if csv_writer:
                    coords = get_landmark_coordinates(first_person_landmarks, frame_width, frame_height)
                    row_data = [str(frame_timestamp_ms)]
                    for i in range(len(mp.solutions.pose.PoseLandmark)):
                        lm_data = coords.get(i, {"x": None, "y": None, "z": None, "visibility": None})
                        row_data.extend(
                            [
                                f"{lm_data['x']:.6f}" if lm_data["x"] is not None else "",
                                f"{lm_data['y']:.6f}" if lm_data["y"] is not None else "",
                                f"{lm_data['z']:.6f}" if lm_data["z"] is not None else "",
                                f"{lm_data['visibility']:.6f}" if lm_data["visibility"] is not None else "",
                            ]
                        )
                    csv_writer.writerow(row_data)
            else:
                if csv_writer:
                    row_data = [str(frame_timestamp_ms)] + [""] * (len(mp.solutions.pose.PoseLandmark) * 4)
                    csv_writer.writerow(row_data)

            if settings.DISPLAY_RESULTS:
                cv2.imshow("MediaPipe Pose: Andromeda Project", drawn_image)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    print("ユーザーによって中断されました。")
                    break

            if settings.SAVE_OUTPUT_VIDEO and out_video:
                out_video.write(drawn_image)

            frame_timestamp_ms += int(1000 / fps)

        print(f"動画の処理が完了しました。総フレーム数: {frame_timestamp_ms / (1000 / fps)}")

        cap.release()
        if out_video:
            out_video.release()
        if settings.DISPLAY_RESULTS:
            cv2.destroyAllWindows()
