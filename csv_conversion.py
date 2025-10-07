import numpy as np
import pandas as pd

HUMANOID_LABELS = [
    "Hips", "Spine", "Spine1", "Neck", "Head",
    "LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand",
    "RightShoulder", "RightArm", "RightForeArm", "RightHand",
    "LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase",
    "RightUpLeg", "RightLeg", "RightFoot", "RightToeBase"
]

MP = {
    "nose":0,
    "left_shoulder":11, "right_shoulder":12,
    "left_elbow":13, "right_elbow":14,
    "left_wrist":15, "right_wrist":16,
    "left_hip":23, "right_hip":24,
    "left_knee":25, "right_knee":26,
    "left_ankle":27, "right_ankle":28,
    "left_foot_index":31, "right_foot_index":32
}

def mediapipe_to_humanoid(mp_points):
    mp_points = np.array(mp_points).reshape(33, 3)
    hips = (mp_points[MP["left_hip"]] + mp_points[MP["right_hip"]]) / 2
    neck = (mp_points[MP["left_shoulder"]] + mp_points[MP["right_shoulder"]]) / 2
    spine = (hips + neck) / 2
    spine1 = (spine + neck) / 2
    head = mp_points[MP["nose"]]

    humanoid = np.array([
        hips, spine, spine1, neck, head,
        mp_points[MP["left_shoulder"]],
        (mp_points[MP["left_shoulder"]] + mp_points[MP["left_elbow"]]) / 2,
        mp_points[MP["left_elbow"]], mp_points[MP["left_wrist"]],
        mp_points[MP["right_shoulder"]],
        (mp_points[MP["right_shoulder"]] + mp_points[MP["right_elbow"]]) / 2,
        mp_points[MP["right_elbow"]], mp_points[MP["right_wrist"]],
        mp_points[MP["left_hip"]], mp_points[MP["left_knee"]],
        mp_points[MP["left_ankle"]], mp_points[MP["left_foot_index"]],
        mp_points[MP["right_hip"]], mp_points[MP["right_knee"]],
        mp_points[MP["right_ankle"]], mp_points[MP["right_foot_index"]]
    ])
    return humanoid

# CSV読み込み
df = pd.read_csv("position_001.csv")

humanoid_data = []
for _, row in df.iterrows():
    values = row.values

    # 最初の列(frame_idなど)を除去
    coords = values[1:]

    # x,y,zのみ抽出 → 各点4列なら [x,y,z,visibility]
    xyz_only = []
    for i in range(33):
        xyz_only.extend(coords[i*4 : i*4+3])

    mp_points = np.array(xyz_only).reshape(33, 3)
    humanoid_points = mediapipe_to_humanoid(mp_points)
    humanoid_data.append(humanoid_points.flatten())

humanoid_df = pd.DataFrame(humanoid_data, columns=[
    f"{label}_{axis}" for label in HUMANOID_LABELS for axis in ["x","y","z"]
])
humanoid_df.to_csv("humanoid_positions.csv", index=False)
print("変換完了: humanoid_positions.csv")
