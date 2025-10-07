#movファイルから骨格推定した動画(aviファイル)とcsvファイルの作成を行うコード
import cv2
import mediapipe as mp
import numpy as np
import csv
from datetime import datetime

# === MediaPipe Pose 初期化 ===
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# === 動画ファイル読み込み ===
video_path = 'sample1.mov'  # 任意のファイル名に変更してください
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("動画ファイルを開けませんでした")
    exit()

# 動画情報
fps = int(cap.get(cv2.CAP_PROP_FPS))
frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
fourcc = cv2.VideoWriter_fourcc(*'XVID')

# 録画・保存関連
recording = True  # 自動で録画開始
video_writer = None
csv_file = None
csv_writer = None
frame_count = 0

# ランドマーク名一覧（33個）
landmark_names = [lm.name for lm in mp_pose.PoseLandmark]

# ファイル保存準備
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
video_filename = f"output_{timestamp}.avi"
csv_filename = f"landmarks_{timestamp}.csv"

video_writer = cv2.VideoWriter(video_filename, fourcc, fps, frame_size)
csv_file = open(csv_filename, mode='w', newline='')
csv_writer = csv.writer(csv_file)

# ヘッダー行作成
header = ["frame"]
for name in landmark_names:
    header += [f"{name}_x", f"{name}_y", f"{name}_z", f"{name}_v"]
csv_writer.writerow(header)

# === メインループ ===
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 背景黒画像
    black_bg = np.zeros_like(frame)

    # RGB に変換して MediaPipe 処理
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    if results.pose_landmarks:
        # 骨格描画
        skeleton_frame = black_bg.copy()
        mp.solutions.drawing_utils.draw_landmarks(
            skeleton_frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp.solutions.drawing_styles.get_default_pose_landmarks_style()
        )
        display_frame = skeleton_frame

        # CSVに書き出し
        row = [frame_count]
        for lm in results.pose_landmarks.landmark:
            row.extend([lm.x, lm.y, lm.z, lm.visibility])
        csv_writer.writerow(row)

    else:
        display_frame = black_bg

    # 動画保存
    if recording:
        video_writer.write(display_frame)

    # 表示（オプション）
    cv2.imshow("Pose Estimation (File)", display_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    frame_count += 1

# === 終了処理 ===
cap.release()
video_writer.release()
csv_file.close()
cv2.destroyAllWindows()
pose.close()
print("処理完了しました。")
