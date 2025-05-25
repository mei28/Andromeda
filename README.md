# Andromeda – MediaPipe Pose Estimation Pipeline

日本語 / English

---

## 概要 (Overview)

Andromeda は **MediaPipe Tasks (0.10.x)** の Pose Landmarker を用いて、動画内の人体ランドマークを検出し、

* ランドマークをリアルタイムで描画 (OpenCV ウィンドウ)
* 各フレームの 33 点 × (x, y, z, visibility) を CSV へ保存
* （オプション）ランドマーク付きの動画を書き出し

を行う Python プロジェクトです。

```
project/
├─ config/           # 設定ファイル置き場
│  └─ settings.py    # 既定値と CLI の定義
├─ data/
│  ├─ raw/           # 入力動画 (.mp4 など)
│  ├─ processed/     # 出力 CSV
│  └─ models/        # .task モデル
├─ output/           # 出力動画 (オプション)
├─ src/              # 実装
└─ main.py           # エントリポイント
```

---

## インストール (Installation)

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt   # 例: mediapipe==0.10.* opencv-python
```

モデルを取得し `data/models/` へ配置します。

```bash
wget -P data/models \
  https://storage.googleapis.com/mediapipe-models/pose_landmarker/lite/float32/1/pose_landmarker_lite.task
```

---

## 実行方法 (How to Run)

```bash
# 最低限 – data/raw/ に video.mp4 がある場合
python main.py --input_video video.mp4

# 指定モデルでランドマーク付き動画も保存
python main.py \
  --input_video p1.mp4 \
  --pose_model pose_landmarker_full.task \
  --save_output_video

# GUI 非表示 & CSV のみ取得
python main.py --input_video p1.mp4 --no_display
```

### コマンドライン引数 (CLI Options)

| 引数                    | 型 / 既定値        | 説明                                             |
| --------------------- | -------------- | ---------------------------------------------- |
| `--profile`           | str, `default` | `config/profiles/<name>.json`/`.yaml` を読み込み上書き |
| `--input_video`       | str            | `data/raw/` 配下の動画ファイル名                         |
| `--pose_model`        | str            | `data/models/` 配下の `.task` モデル名                |
| `--no_display`        | flag           | OpenCV ウィンドウを開かない                              |
| `--no_save_coords`    | flag           | CSV を書き出さない                                    |
| `--save_output_video` | flag           | ランドマーク描画済み動画を `output/` に保存                    |

---

## 設定パラメータ一覧 (Config Reference)

| 変数名                             | 既定値                         | 説明                          |
| ------------------------------- | --------------------------- | --------------------------- |
| `INPUT_VIDEO_FILENAME`          | `input_video.mp4`           | デフォルト入力動画名                  |
| `POSE_MODEL_FILENAME`           | `pose_landmarker_lite.task` | 使用モデル                       |
| `POSE_MODEL_COMPLEXITY`         | `lite`                      | 表示用のメモ値 *(Tasks 版には影響しません)* |
| `POSE_RUNNING_MODE`             | `VIDEO`                     | `IMAGE` / `VIDEO`           |
| `POSE_MIN_DETECTION_CONFIDENCE` | `0.5`                       | 検出信頼度しきい値                   |
| `POSE_MIN_PRESENCE_CONFIDENCE`  | `0.5`                       | プレゼンスしきい値                   |
| `POSE_MIN_TRACKING_CONFIDENCE`  | `0.5`                       | トラッキングしきい値                  |
| `DISPLAY_RESULTS`               | `True`                      | ウィンドウ表示                     |
| `SAVE_PROCESSED_COORDINATES`    | `True`                      | CSV 保存                      |
| `PROCESSED_COORDS_FILENAME`     | `pose_coordinates.csv`      | 出力 CSV 名                    |
| `SAVE_OUTPUT_VIDEO`             | `False`                     | 出力動画を保存するか                  |
| `OUTPUT_VIDEO_FILENAME`         | `output_pose_video.mp4`     | 出力動画名                       |
| `OUTPUT_VIDEO_FOURCC`           | `mp4v`                      | 動画コーデック                     |

> **プロファイル機能**: `config/profiles/low_res_fast.yaml` などを作成すると、
> `--profile low_res_fast` で読み込まれ、任意のパラメータを一括変更できます。

---

## CSV フォーマット (Pose CSV)

```
frame_id, landmark_0_x, landmark_0_y, landmark_0_z, landmark_0_visibility, … , landmark_32_visibility
```

* 1 行 = 1 フレーム
* x, y は 0‑1 正規化、z は腰原点スケール、visibility は \[0,1]

---

## よくある質問 (FAQ)

* **FPS が低い**: `--no_display` で GUI を切る / Lite モデルを使う。
* **ランドマークが途切れる**: 照明を明るくするか Full モデルを使う。
* **Windows で OpenCV ウィンドウが固まる**: `cv2.waitKey(1)` 部を `waitKey(5)` などに調整。

---

Happy Hacking! 🎉
