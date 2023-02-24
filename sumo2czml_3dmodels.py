import csv
import json
from datetime import datetime, timedelta
import math
import numpy as np
import random


def convert_to_czml_3Dmodel(input_file, output_file, start_date, current_time):
    with open(input_file, 'r') as input_csv:
        reader = csv.DictReader(input_csv)

        czml = [{
            "id": "document",
            "version": "1.0",
            "name": "SUMOTrafficSimulationOutput",
            "clock": {
                "interval": f"{start_date.isoformat()}Z/{start_date.isoformat()}Z",
                "currentTime": (start_date + timedelta(seconds=current_time)).isoformat() + "Z",
                "multiplier": 1,
            }
        }]
        vehicle_positions = {}
        max_timestep = 0.0
        for row in reader:
            vehicle_id = row['id']
            vehicle_type = row['type']
            if vehicle_type not in ['passenger', 'pedestrian']:
                continue  # skip if not passenger or pedestrian
            timestep = float(row['timestep'])
            if timestep > max_timestep:
                max_timestep = timestep
            if vehicle_id not in vehicle_positions:
                if vehicle_type == 'passenger':
                    # Use a random number between 1 and 16 to generate the link to the 3D model
                    # model_link = f"./3Dmodels/{random.randint(1, 16)}.gltf"
                    model_link = f"./3Dmodels/CesiumMilkTruck.glb"
                elif vehicle_type == 'pedestrian':
                    model_link = './3Dmodels/Cesium_Man.glb'
                else:
                    model_link = './3Dmodels/notavailable.glb'

                vehicle_positions[vehicle_id] = {
                    "id": vehicle_id,
                    "name": vehicle_id,
                    "description": "1",
                    "model": {
                        "gltf": model_link,
                    },
                    "position": {
                        "epoch": start_date.isoformat() + 'Z',
                        "cartographicDegrees": []
                    },
                    "orientation": {
                        "epoch": start_date.isoformat() + 'Z',
                        "unitQuaternion": []
                    }
                }

            # Set the z value based on the presence of the 'z' column in the CSV
            if 'z' in row:
                vehicle_positions[vehicle_id]['position']['cartographicDegrees'].extend(
                    [float(row['timestep']), float(row['x']), float(row['y']), float(row['z'])])
            else:
                vehicle_positions[vehicle_id]['position']['cartographicDegrees'].extend(
                    [float(row['timestep']), float(row['x']), float(row['y']), 0])

            # Set the orientation based on the corresponding longitude, latitude, slope (if available) and angle values in the CSV
            if 'slope' in row:
                q = get_orientation(float(row['y']), (float(row['x'])), 0, -(float(row['slope'])), (float(row['angle']))+180) #depends on orientation of 3d model in local (model) frame
                vehicle_positions[vehicle_id]['orientation']['unitQuaternion'].extend([float(row['timestep']), *q])
            else:
                q = get_orientation(float(row['y']), (float(row['x'])), 0, 0, (float(row['angle'])) + 180)  # depends on orientation of 3d model in local (model) frame
                vehicle_positions[vehicle_id]['orientation']['unitQuaternion'].extend([float(row['timestep']), *q])

        # Update the end time of the interval to the maximum timestep value
        end_date = start_date + timedelta(seconds=max_timestep)
        czml[0]['clock']['interval'] = f"{start_date.isoformat()}Z/{end_date.isoformat()}Z"

        czml.extend(vehicle_positions.values())

    with open(output_file, 'w') as output_czml:
        json.dump(czml, output_czml, indent=1)


def get_orientation(lat, lon, heading, pitch, roll):
    # Convert angles to radians
    heading = np.deg2rad(heading)
    pitch = np.deg2rad(pitch)
    roll = np.deg2rad(roll)

    lat = np.deg2rad(lat)
    lon = np.deg2rad(lon)

    # Compute rotation matrix
    sin_lat = math.sin(lat)
    cos_lat = math.cos(lat)
    sin_lon = math.sin(lon)
    cos_lon = math.cos(lon)

    R = np.array([[-sin_lat * cos_lon, -sin_lat * sin_lon, cos_lat],
                  [-sin_lon, cos_lon, 0],
                  [-cos_lat * cos_lon, -cos_lat * sin_lon, -sin_lat]])

    # Compute Euler angles from rotation matrix
    heading1, pitch1, roll1, heading2, pitch2, roll2 = rotationmatrix2eulerangles(R)

    # Convert to quaternions
    q_pos = euler2quaternion(heading1, pitch1, roll2)
    q_hpr = euler2quaternion(heading, pitch, roll)

    # Multiply quaternions
    quat = quaternion_multiply(q_hpr, q_pos)

    return quat


def rotationmatrix2eulerangles(R):
    r11 = R[0, 0]
    r12 = R[0, 1]
    r13 = R[0, 2]
    r21 = R[1, 0]
    r22 = R[1, 1]
    r23 = R[1, 2]
    r31 = R[2, 0]
    r32 = R[2, 1]
    r33 = R[2, 2]

    # Convert rotation matrix to Euler angles
    pitch1 = -np.arcsin(r13)
    pitch2 = math.pi - pitch1
    if np.abs(np.cos(pitch1)) < 1e-6:
        # Gimbal lock: pitch is close to +/-90 degrees
        roll1 = np.arctan2(-r21, r22)
        roll2 = np.arctan2(-r21, r22)
        heading1 = 0
        heading2 = 0
    else:
        cos_roll1 = r11 / np.cos(pitch1)
        sin_roll1 = r12 / np.cos(pitch1)
        roll1 = np.arctan2(sin_roll1, cos_roll1)
        cos_heading1 = r33 / np.cos(pitch1)
        sin_heading1 = r23 / np.cos(pitch1)
        heading1 = np.arctan2(sin_heading1, cos_heading1)

        cos_roll2 = r11 / np.cos(pitch2)
        sin_roll2 = r12 / np.cos(pitch2)
        roll2 = np.arctan2(sin_roll2, cos_roll2)
        cos_heading2 = r33 / np.cos(pitch2)
        sin_heading2 = r23 / np.cos(pitch2)
        heading2 = np.arctan2(sin_heading2, cos_heading2)

    # Return the Euler angles as individual variables
    return heading1, pitch1, roll1, heading2, pitch2, roll2


def euler2quaternion(h, p, r):
    # Convert Euler angles to quaternions
    cy_pos = math.cos(h * 0.5)
    sy_pos = math.sin(h * 0.5)
    cp_pos = math.cos(p * 0.5)
    sp_pos = math.sin(p * 0.5)
    cr_pos = math.cos(r * 0.5)
    sr_pos = math.sin(r * 0.5)

    q = np.empty((4,))
    q[0] = cy_pos * cp_pos * cr_pos + sy_pos * sp_pos * sr_pos
    q[1] = cy_pos * cp_pos * sr_pos - sy_pos * sp_pos * cr_pos
    q[2] = sy_pos * cp_pos * sr_pos + cy_pos * sp_pos * cr_pos
    q[3] = sy_pos * cp_pos * cr_pos - cy_pos * sp_pos * sr_pos

    return q


def quaternion_multiply(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    w = w1*w2 - x1*x2 - y1*y2 - z1*z2
    x = w1*x2 + x1*w2 + y1*z2 - z1*y2
    y = w1*y2 - x1*z2 + y1*w2 + z1*x2
    z = w1*z2 + z1*w2 + x1*y2 - y1*x2

    return np.array([w, x, y, z])

if __name__ == '__main__':
    start_date = datetime(2023, 6, 26, 12, 0, 0)
    current_time = 180
    convert_to_czml_3Dmodel('./input/sumo_fcd_sample.csv', './output/czml_3Dmodels_sample.czml', start_date, current_time)