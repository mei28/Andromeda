import cv2
import mediapipe as mp

# MediaPipe DrawingUtils と DrawingStyles を初期化
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles  # この行は必要

# mp_pose も POSE_CONNECTIONS や PoseLandmark の Enum にアクセスするために必要
mp_pose = mp.solutions.pose


def draw_pose_landmarks(image, pose_landmarks):
    """
    画像上にMediaPipeの骨格ランドマークを描画する関数

    Args:
        image (numpy.ndarray): 描画対象の画像 (BGR形式)
        pose_landmarks (mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList):
            MediaPipe Poseの推定結果に含まれるランドマークデータ (単一人物分)
    """
    if pose_landmarks:
        # 公式サンプルに倣い、connection_drawing_spec に DrawingSpec を直接渡す
        # ランドマーク点のスタイルは get_default_pose_landmarks_style() を使用

        # 接続線の描画スタイルを定義 (例: 緑色、太さ2)
        connection_drawing_spec = mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2)

        mp_drawing.draw_landmarks(
            image,
            pose_landmarks,
            mp_pose.POSE_CONNECTIONS,  # デフォルトスタイルを使用
        )
    return image


def get_landmark_coordinates(pose_landmarks, image_width, image_height):
    """
    MediaPipeの骨格ランドマークから座標データを抽出し、生のピクセル座標または正規化座標を返す関数

    Args:
        pose_landmarks (mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList):
            MediaPipe Poseの推定結果に含まれるランドマークデータ
        image_width (int): 元画像の幅
        image_height (int): 元画像の高さ

    Returns:
        dict: 各ランドmarkIDと対応する座標 (x, y, z, visibility) を格納した辞書
              x, y は正規化された値。
    """
    coordinates = {}

    if pose_landmarks:
        lm_iter = pose_landmarks.landmark if hasattr(pose_landmarks, "landmark") else pose_landmarks
        for id, lm in enumerate(lm_iter):
            coordinates[id] = {"x": lm.x, "y": lm.y, "z": lm.z, "visibility": lm.visibility}
    return coordinates


def get_landmark_header_row():
    """
    CSVファイル出力用のランドマークヘッダー行を生成する関数
    """
    header = ["frame_id"]
    for i in range(len(mp_pose.PoseLandmark)):
        header.extend([f"landmark_{i}_x", f"landmark_{i}_y", f"landmark_{i}_z", f"landmark_{i}_visibility"])
    return header
