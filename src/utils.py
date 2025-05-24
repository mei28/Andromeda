import cv2
import mediapipe as mp

# MediaPipe DrawingUtils の初期化
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose  # POSE_CONNECTIONS にアクセスするため


def draw_pose_landmarks(image, pose_landmarks):
    """
    画像上にMediaPipeの骨格ランドマークを描画する関数

    Args:
        image (numpy.ndarray): 描画対象の画像 (BGR形式)
        pose_landmarks (mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList):
            MediaPipe Poseの推定結果に含まれるランドマークデータ
    """
    if pose_landmarks:
        mp_drawing.draw_landmarks(
            image,
            pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_styles=mp_drawing_styles.get_default_pose_landmarks_style(),
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
        dict: 各ランドマークIDと対応する座標 (x, y, z, visibility) を格納した辞書
              x, y は正規化された値。
    """
    coordinates = {}
    if pose_landmarks:
        for id, lm in enumerate(pose_landmarks.landmark):
            # x, y は正規化された座標 (0.0 から 1.0)
            # z は検出された深度（MediaPipe独自のスケール）
            # visibility はそのランドマークが画像内でどれだけ見えるかを示すスコア
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
