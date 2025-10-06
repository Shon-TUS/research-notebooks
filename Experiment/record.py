import os
import time
from datetime import datetime
import csv
import sounddevice as sd
import soundfile as sf
import cv2
import concurrent.futures

# --- 設定 ---
fs = 44100
sd.default.samplerate = fs
channels = [8, 1]
sd.default.channels = channels
dev = [13, 13]
sd.default.device = dev
sd.default.dtype = 'float64'
sd.default.latency = 'low'

RECORD_DURATION_SEC = 300
VIDEO_FPS = 30
RECORD_NUM = 1
CHANNEL = 8
CAMERA_DEVICE_NUM = 2

executor = concurrent.futures.ThreadPoolExecutor(1)

SUBJECT_NAME = "Subject1"
ACTIVE_WAV_FOLDER = "data"
SAVE_VIDEO_FOLDER = "videos"
WRITE_CSV_FILE = "TrainSet.csv"

os.makedirs(ACTIVE_WAV_FOLDER, exist_ok=True)
os.makedirs(SAVE_VIDEO_FOLDER, exist_ok=True)

READWAV_soundfile = 'ChirpSound_5m.wav'
READWAV_sounddata, READWAV_samplerate = sf.read(READWAV_soundfile)

# --- 動画キャプチャ（fpsベースで制御） ---
def capture_video(filename, duration_sec=RECORD_DURATION_SEC, fps=VIDEO_FPS):
    cap = cv2.VideoCapture(CAMERA_DEVICE_NUM, cv2.CAP_DSHOW)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(filename, fourcc, fps, (w, h))

    frame_interval = 1.0 / fps
    total_frames = int(duration_sec * fps)

    print(f"[INFO] video start: {duration_sec}秒, {total_frames} frames expected")
    start_time = time.time()

    for i in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            print(f"[WARN] frame {i} capture failed")
            break
        video.write(frame)
        elapsed = time.time() - start_time
        remaining = frame_interval * (i + 1) - elapsed
        if remaining > 0:
            time.sleep(remaining)

    cap.release()
    video.release()
    print(f"[INFO] video stop, actual duration: {time.time() - start_time:.2f}秒")

# --- メイン処理 ---
if __name__ == '__main__':
    cnt = 0
    print(f"設定:録音{RECORD_DURATION_SEC}秒, 動画FPS={VIDEO_FPS}")
    print("\nEnterキーを押すたびに録音・録画が1回行われます。")

    try:
        while cnt < RECORD_NUM:
            input(f"\n[{cnt+1}/{RECORD_NUM}] Enterキーで録音を開始...")

            timestamp = datetime.today().strftime("%Y%m%d_%H%M%S")
            base_name = f"{timestamp}_{cnt}_USR{SUBJECT_NAME}"
            video_filename = f"{SAVE_VIDEO_FOLDER}/{base_name}.mov"

            # 録音・録画の同時実行
            future = executor.submit(capture_video, video_filename)
            myrecording = sd.playrec(READWAV_sounddata, samplerate=READWAV_samplerate, channels=CHANNEL)
            print("rec-start")
            sd.wait()
            future.result()
            print("rec-end")

            # 音声保存
            files = []
            for ch_index in range(CHANNEL):
                filename = f"{ACTIVE_WAV_FOLDER}/{base_name}_C{ch_index}.wav"
                sf.write(filename, myrecording[:, ch_index], READWAV_samplerate)
                files.append(filename)

            # CSVへ記録
            with open(WRITE_CSV_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(files + [video_filename])

            cnt += 1

        print("サンプリング完了")

    except KeyboardInterrupt:
        print("\n中断されました")




"""
memo

import os
import time
from datetime import datetime
import csv
import sounddevice as sd
import soundfile as sf
import cv2
import concurrent.futures
#import wave
#import struct
#import numpy as np
#import pandas as pd
#from scipy.signal import chirp, spectrogram


# sounddevice の初期設定
fs = 44100
sd.default.samplerate = fs #サンプリングレート
channels = [2, 1] 
sd.default.channels = channels # [マイク, スピーカー]
dev = [13,13] 
sd.default.device = dev # [Input, Output] (ASIO)
sd.default.dtype = 'float64'
sd.default.latency = 'low' # 遅延少なめ

# 録音・録画設定
RATE = fs # サンプリングレート
RECORD_DURATION_SEC = 5.3  # 5,3秒録画、.wavと合わせる。
VIDEO_FPS = 30 # 動画フレームレート 30 or 60
RECORD_NUM = 2  #録音回数
CHANNEL = 2   # マイクの数
CAMERA_DEVICE_NUM = 2 # camera device番号
cap = cv2.VideoCapture(CAMERA_DEVICE_NUM, cv2.CAP_DSHOW) #######################################
#cap = cv2.VideoCapture(CAMERA_DEVICE_NUM)
executor=concurrent.futures.ThreadPoolExecutor(1) # 同期に必要

# --- Single Subject ---
SUBJECT_NAME="Subject1" # 被験者番号
ACTIVE_WAV_FOLDER = "data" # 音データ保存先
#SAVE_IMAGE_FOLDER = "images" # 画像保存先 使わないかも
SAVE_VIDEO_FOLDER = "videos" # 動画保存先
WRITE_CSV_FILE = "TrainSet.csv" # マイクデータ、画像、動画のパスを書き込む。骨格座標も加える可能性あり。
os.makedirs(ACTIVE_WAV_FOLDER, exist_ok=True)
#os.makedirs(SAVE_IMAGE_FOLDER, exist_ok=True)
os.makedirs(SAVE_VIDEO_FOLDER, exist_ok=True)
# ここにTrainSet.csvを作るコード書きたい

# --- 音声ファイル読み込み ---
READWAV_soundfile = 'ChirpSound.wav' # 読み込む音源ファイル
READWAV_sounddata, READWAV_samplerate = sf.read(READWAV_soundfile)


def capture_video(filename, duration_sec=RECORD_DURATION_SEC, fps=VIDEO_FPS):

    # --- 初期設定 ---
    cap = cv2.VideoCapture(CAMERA_DEVICE_NUM, cv2.CAP_DSHOW) # カメラ取得  ####################
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) # カメラの幅
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) # カメラの高さ
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 動画保存形式

    video = cv2.VideoWriter(filename, fourcc, fps, (w, h))

    print(f"[INFO] video start: {duration_sec}秒")
    start_time = time.time()
    while (time.time() - start_time) < duration_sec:
        ret, frame = cap.read() # 1 frame 読み込み
        video.write(frame) # 1 frame 保存

    cap.release()
    video.release()
    #cv2.destroyAllWindows() #cv2.imshow()を使うときに使用
    print("[INFO] video stop")


# --- 実行 ---
if __name__ == '__main__': #ラベルはいらない

    cnt = 0 
    print(f"設定:録音{RECORD_DURATION_SEC}秒, 動画FPS={VIDEO_FPS}")
    print("\nEnterキーを押すたびに録音・録画が1回行われます。")

    try: # Enter
        while cnt < RECORD_NUM:
            input(f"\n[{cnt+1}/{RECORD_NUM}] Enterキーで録音を開始...")

            timestamp = datetime.today().strftime("%Y%m%d_%H%M%S")
            base_name = f"{timestamp}_{cnt}_USR{SUBJECT_NAME}"
            video_filename = f"{SAVE_VIDEO_FOLDER}/{base_name}.mov"

            # --- 録音・録画 同時実行 ---
            future = executor.submit(capture_video,video_filename)
            myrecording = sd.playrec(READWAV_sounddata, samplerate=READWAV_samplerate, channels=CHANNEL)
            print("rec-start")
            #capture_video(video_filename) # これいらない
            sd.wait() # 録音終了待ち
            future.result() # 録画終了待ち
            print("rec-end")

            # --- 音声保存 ---
            files = []
            for ch_index in range(CHANNEL):
                filename = f"{ACTIVE_WAV_FOLDER}/{base_name}_C{ch_index}.wav"
                sf.write(filename, myrecording[:, ch_index], READWAV_samplerate)
                files.append(filename)

            # --- CSVへ記録 ---
            with open(WRITE_CSV_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                #writer.writerow(files + [image_filename, video_filename])
                writer.writerow(files + [video_filename])

            cnt += 1

        print("サンプリング完了")

    except KeyboardInterrupt: # Ctrl+C
        print("\n中断されました")
        cap.release()


"""