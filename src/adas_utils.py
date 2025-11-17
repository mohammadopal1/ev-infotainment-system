#!/usr/bin/env python
"""
ADAS Utility Functions
Detection, proximity checking, and helper functions.
"""

import random
import numpy as np
import cv2
import carla
import time
import datetime
from adas_config import model, writer, audio_alerts, VEHICLE_KEYWORDS, WARNING_CLEAR_TIME

def detect_blindspot_frame(array, state, side="left"):
    """Run YOLOv5 on an already-decoded numpy image; update state & CSV with timestamp."""
    if array is None:
        return
    h, w = array.shape[:2]
    scale = 0.5
    small_array = cv2.resize(array, (int(w * scale), int(h * scale)))
    rgb = cv2.cvtColor(small_array, cv2.COLOR_BGR2RGB)
    results = model(rgb, size=160)
    alert_level = "clear"
    current_time = time.time()
    if len(results.xyxy) > 0 and results.xyxy[0] is not None:
        detections = results.xyxy[0].cpu().numpy()
        names = model.names
        for det in detections:
            x1, y1, x2, y2, conf, cls_id = det
            label = names[int(cls_id)].lower()
            if any(k in label for k in VEHICLE_KEYWORDS):
                sh, sw = small_array.shape[:2]
                box_center_x = (x1 + x2) / 2
                box_height = y2 - y1
                if side == "left":
                    if 0.05 * sw < box_center_x < 0.35 * sw:
                        alert_level = "near"
                        if box_height > 0.25 * sh: alert_level = "warn"
                else:
                    if 0.65 * sw < box_center_x < 0.95 * sw:
                        alert_level = "near"
                        if box_height > 0.25 * sh: alert_level = "warn"
                writer.writerow([datetime.datetime.now(), label, float(conf),
                                 side, alert_level, "", "", ""])
    previous_level = state.get("level", "clear")
    if alert_level != "clear":
        state["level"] = alert_level
        state["last_detection"] = current_time
        if alert_level == "warn" and previous_level == "clear" and audio_alerts["blindspot"]:
            audio_alerts["blindspot"].play()
    else:
        if current_time - state.get("last_detection", 0) > WARNING_CLEAR_TIME:
            state["level"] = "clear"

def check_proximity(world, vehicle, prox_state):
    """Check proximity to other vehicles with time-based warning clearing."""
    ego_loc = vehicle.get_location()
    ego_vel = vehicle.get_velocity().length()
    min_dist = 9999
    rel_speed = 0
    alert = "clear"
    current_time = time.time()
    for actor in world.get_actors().filter("vehicle.*"):
        if actor.id == vehicle.id: continue
        dist = ego_loc.distance(actor.get_location())
        if dist < min_dist:
            min_dist = dist
            rel_speed = actor.get_velocity().length() - ego_vel
    if min_dist < 8:
        alert = "warn"
    elif min_dist < 15:
        alert = "near"
    if min_dist < 9999:
        writer.writerow([datetime.datetime.now(), "vehicle_ahead", "", "", "",
                         "", f"{min_dist:.1f}", f"{rel_speed:.1f}"])
    previous_level = prox_state.get("level", "clear")
    if alert != "clear":
        prox_state["level"] = alert
        prox_state["last_detection"] = current_time
        if alert == "warn" and previous_level == "clear" and audio_alerts["proximity"]:
            audio_alerts["proximity"].play()
    else:
        if current_time - prox_state.get("last_detection", 0) > WARNING_CLEAR_TIME:
            prox_state["level"] = "clear"
    return prox_state["level"]

def follow_vehicle_spectator(world, vehicle):
    spectator = world.get_spectator()
    transform = vehicle.get_transform()
    offset = carla.Location(x=-8, z=4)
    new_location = transform.transform(offset)
    spectator.set_transform(carla.Transform(new_location, transform.rotation))

def spawn_npc_traffic(world, client, num_vehicles=20):
    tm_port = 8000
    tm = client.get_trafficmanager(tm_port)
    tm.set_global_distance_to_leading_vehicle(1.5)
    tm.set_synchronous_mode(True)
    tm.global_percentage_speed_difference(30)
    bp_lib = world.get_blueprint_library()
    spawn_points = list(world.get_map().get_spawn_points())
    random.shuffle(spawn_points)
    vehicles = []
    for i in range(num_vehicles):
        bp = random.choice(bp_lib.filter('vehicle.*'))
        transform = random.choice(spawn_points)
        actor = world.try_spawn_actor(bp, transform)
        if actor:
            actor.set_autopilot(True, tm_port)
            vehicles.append(actor)
            tm.vehicle_percentage_speed_difference(actor, random.randint(10, 40))
    return vehicles
