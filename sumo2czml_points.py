import csv
import json
from datetime import datetime, timedelta


def convert_to_czml(input_file, output_file, start_date, current_time):
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
        cartographic_degrees = []
        max_timestep = 0.0
        for row in reader:
            vehicle_id = row['id']
            vehicle_type = row['type']
            timestep = float(row['timestep'])
            if timestep > max_timestep:
                max_timestep = timestep
            if vehicle_id not in vehicle_positions:
                vehicle_positions[vehicle_id] = {
                    "id": vehicle_id,
                    "name": vehicle_id,
                    "description": "1",
                    "point": {
                        "color": get_vehicle_color(vehicle_type),
                        "pixelSize": 10,
                        "outlineWidth": 2,
                    },
                    "position": {
                        "epoch": start_date.isoformat() + 'Z',
                        "cartographicDegrees": []
                    }

                }

            # Set the z value based on the presence of the 'z' column in the CSV
            if 'z' in row:
                vehicle_positions[vehicle_id]['position']['cartographicDegrees'].extend(
                    [float(row['timestep']), float(row['x']), float(row['y']), float(row['z'])])
            else:
                vehicle_positions[vehicle_id]['position']['cartographicDegrees'].extend(
                    [float(row['timestep']), float(row['x']), float(row['y']), 0])

        # Update the end time of the interval to the maximum timestep value
        end_date = start_date + timedelta(seconds=max_timestep)
        czml[0]['clock']['interval'] = f"{start_date.isoformat()}Z/{end_date.isoformat()}Z"

        czml.extend(vehicle_positions.values())

    with open(output_file, 'w') as output_czml:
        json.dump(czml, output_czml, indent=1)


def get_vehicle_color(vehicle_type):
    if vehicle_type == 'passenger':
        return {"rgba": [0, 0, 255, 255]} #blue
    elif vehicle_type == 'bicycle':
        return {"rgba": [255, 255, 0, 255]} #yellow
    elif vehicle_type == 'pedestrian':
        return {"rgba": [0, 128, 0, 255]} #green
    elif vehicle_type == 'person':
        return {"rgba": [34, 139, 34, 255]} #forestgreen
    elif vehicle_type == 'truck':
        return {"rgba": [255, 0, 0, 255]} #red
    elif vehicle_type == 'trailer':
        return {"rgba": [255, 128, 114, 255]}  #salmon
    elif vehicle_type == 'bus':
        return {"rgba": [148, 0, 211, 255]} #darkviolet
    elif vehicle_type == 'coach':
        return {"rgba": [75, 0, 130, 255]} #indigo
    elif vehicle_type == 'moped':
        return {"rgba": [255, 140, 0, 255]}  #darkorange
    elif vehicle_type == 'motorcycle':
        return {"rgba": [128, 0, 0, 255]}  #maroon
    elif vehicle_type == 'taxi':
        return {"rgba": [255, 215, 0, 255]}  #goldenrod
    elif vehicle_type == 'emergency':
        return {"rgba": [220, 20, 60, 255]}  #crimson
    elif vehicle_type == 'delivery':
        return {"rgba": [0, 255, 255, 255]}  #aqua
    elif vehicle_type == 'tram':
        return {"rgba": [106, 90, 205, 255]} #slateblue
    elif vehicle_type == 'rail_urban':
        return {"rgba": [65, 105, 225, 255]}  #royalblue
    elif vehicle_type == 'rail_electric':
        return {"rgba": [144, 238, 144, 255]}  #lightgreen
    elif vehicle_type == 'rail':
        return {"rgba": [0, 0, 139, 255]}  #darkblue
    elif vehicle_type == 'evehicle':
        return {"rgba": [128,128, 0, 255]}  #olive
    elif vehicle_type == 'e-scooter':
        return {"rgba": [152, 251, 152, 255]}  #palegreen
    elif vehicle_type == 'ship':
        return {"rgba": [0, 0, 0, 255]}  #black
    else:
        return {"rgba": [255, 255, 255, 255]} #white


if __name__ == '__main__':
    start_date= datetime(2023, 6, 26, 12, 0, 0)
    current_time=180
    convert_to_czml('./input/sumo_fcd_sample.csv', './output/czml_points_sample.czml', start_date, current_time)