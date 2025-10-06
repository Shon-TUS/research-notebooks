import struct
import numpy as np
import wave
from scipy.signal import chirp

def MakeChirpFile():
    sample_hz = 44100  # サンプリング周波数を設定
    Chirp_sec = 0.1  # チャープ音の長さを0.1秒に設定
    num_chirps = 2999  # 50回のチャープ音を生成
    ap = 0.1 # 音を流した後に反響音を取る余白の時間
    wv16_data = []

    for _ in range(num_chirps):
        t = np.linspace(0, Chirp_sec, int(Chirp_sec * sample_hz), endpoint=False)
        w = chirp(t, f0=0, f1=22050, t1=Chirp_sec, method='linear')  
        
        max_num = 32767.0 / max(w)
        wv16 = [int(x * max_num) for x in w]
        wv16_data.extend(wv16)
    for _ in range(int(ap*sample_hz)):
        wv16_data.append(0)
    bi_wv = struct.pack("h" * len(wv16_data), *wv16_data)

    Chirp_file = wave.open('ChirpSound_5m.wav', mode='wb')
    param = (1, 2, sample_hz, len(bi_wv), 'NONE', 'not compressed')
    Chirp_file.setparams(param)
    Chirp_file.writeframes(bi_wv)
    Chirp_file.close()
    print("MakeChirpFile")

if __name__ == '__main__':  
    MakeChirpFile()