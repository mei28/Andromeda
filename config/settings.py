import json
import yaml
from pathlib import Path
import argparse


class Settings:
    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent.parent

        self.RAW_DATA_DIR = self.BASE_DIR / "data" / "raw"
        self.PROCESSED_DATA_DIR = self.BASE_DIR / "data" / "processed"
        self.OUTPUT_DIR = self.BASE_DIR / "output"
        self.CONFIG_PROFILES_DIR = self.BASE_DIR / "config" / "profiles"
        self.MODELS_DIR = self.BASE_DIR / "data" / "models"

        # デフォルト値を設定
        self.INPUT_VIDEO_FILENAME: str = "input_video.mp4"
        self.INPUT_VIDEO_PATH: Path = self.RAW_DATA_DIR / self.INPUT_VIDEO_FILENAME

        # --- MediaPipe PoseLandmarker 設定 ---
        self.POSE_MODEL_FILENAME: str = "pose_landmarker_lite.task"
        self.POSE_MODEL_PATH: Path = self.MODELS_DIR / self.POSE_MODEL_FILENAME

        self.POSE_MODEL_COMPLEXITY: str = "lite"

        self.POSE_RUNNING_MODE: str = "VIDEO"  # 'IMAGE' or 'VIDEO'

        # これらの設定はPoseLandmarkerOptionsの直接の引数ではないため、
        # 今は設定として残しつつ、PoseEstimatorで直接渡さないようにします。
        # 必要に応じて、running_modeやコールバックでのフィルタリングで対応します。
        self.POSE_MIN_DETECTION_CONFIDENCE: float = 0.5
        self.POSE_MIN_PRESENCE_CONFIDENCE: float = 0.5
        self.POSE_MIN_TRACKING_CONFIDENCE: float = 0.5

        self.DISPLAY_RESULTS: bool = True
        self.SAVE_PROCESSED_COORDINATES: bool = True
        self.PROCESSED_COORDS_FILENAME: str = "pose_coordinates.csv"
        self.PROCESSED_COORDS_PATH: Path = self.PROCESSED_DATA_DIR / self.PROCESSED_COORDS_FILENAME

        self.SAVE_OUTPUT_VIDEO: bool = False
        self.OUTPUT_VIDEO_FILENAME: str = "output_pose_video.mp4"
        self.OUTPUT_VIDEO_PATH: Path = self.OUTPUT_DIR / self.OUTPUT_VIDEO_FILENAME
        self.OUTPUT_VIDEO_FOURCC: str = "mp4v"

        # ディレクトリが存在しない場合に作成
        self.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.CONFIG_PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        self.MODELS_DIR.mkdir(parents=True, exist_ok=True)

    def load_from_profile(self, profile_name: str = "default"):
        profile_path_json = self.CONFIG_PROFILES_DIR / f"{profile_name}.json"
        profile_path_yaml = self.CONFIG_PROFILES_DIR / f"{profile_name}.yaml"

        if profile_path_json.exists():
            with open(profile_path_json, "r") as f:
                config_data = json.load(f)
        elif profile_path_yaml.exists():
            with open(profile_path_yaml, "r") as f:
                config_data = yaml.safe_load(f)
        else:
            print(f"Warning: Configuration profile '{profile_name}' not found. Using default settings.")
            return

        for key, value in config_data.items():
            if key.endswith("_PATH") and isinstance(value, str):
                setattr(self, key, Path(value))
            elif key.endswith("_DIR") and isinstance(value, str):
                setattr(self, key, Path(value))
            elif key == "INPUT_VIDEO_FILENAME":
                self.INPUT_VIDEO_FILENAME = value
                self.INPUT_VIDEO_PATH = self.RAW_DATA_DIR / self.INPUT_VIDEO_FILENAME
            elif key == "PROCESSED_COORDS_FILENAME":
                self.PROCESSED_COORDS_FILENAME = value
                self.PROCESSED_COORDS_PATH = self.PROCESSED_DATA_DIR / self.PROCESSED_COORDS_FILENAME
            elif key == "OUTPUT_VIDEO_FILENAME":
                self.OUTPUT_VIDEO_FILENAME = value
                self.OUTPUT_VIDEO_PATH = self.OUTPUT_DIR / self.OUTPUT_VIDEO_FILENAME
            elif key == "POSE_MODEL_FILENAME":
                self.POSE_MODEL_FILENAME = value
                self.POSE_MODEL_PATH = self.MODELS_DIR / self.POSE_MODEL_FILENAME
            else:
                setattr(self, key, value)

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description="Andromeda Pose Estimation Project")
        parser.add_argument(
            "--profile",
            type=str,
            default="default",
            help='Load settings from a named profile (e.g., "default", "low_res_fast").',
        )
        parser.add_argument(
            "--input_video", type=str, help=f"Path to the input video file relative to {self.RAW_DATA_DIR}"
        )
        parser.add_argument(
            "--pose_model",
            type=str,
            help=f'Filename of the MediaPipe PoseLandmarker model (e.g., "pose_landmarker_full.task"). Relative to {self.MODELS_DIR}',
        )

        parser.add_argument("--no_display", action="store_true", help="Do not display real-time results via GUI.")
        parser.add_argument("--no_save_coords", action="store_true", help="Do not save processed coordinates to CSV.")
        parser.add_argument(
            "--save_output_video", action="store_true", help="Save the processed video with pose landmarks."
        )

        args = parser.parse_args()

        self.load_from_profile(args.profile)

        if args.input_video:
            self.INPUT_VIDEO_FILENAME = Path(args.input_video).name
            self.INPUT_VIDEO_PATH = self.RAW_DATA_DIR / self.INPUT_VIDEO_FILENAME
        if args.pose_model:
            self.POSE_MODEL_FILENAME = Path(args.pose_model).name
            self.POSE_MODEL_PATH = self.MODELS_DIR / self.POSE_MODEL_FILENAME
        if args.no_display:
            self.DISPLAY_RESULTS = False
        if args.no_save_coords:
            self.SAVE_PROCESSED_COORDINATES = False
        if args.save_output_video:
            self.SAVE_OUTPUT_VIDEO = True


settings = Settings()
