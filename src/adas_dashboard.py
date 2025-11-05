#!/usr/bin/env python
"""
EV Infotainment System - ADAS Dashboard
Advanced Driver Assistance System with real-time blind-spot detection,
lane departure warning, and proximity alerts.

Requires CARLA Simulator 0.9.15
"""

import random
import numpy as np
import cv2
import carla
import torch
import pygame
import time
import csv
import datetime
import math
import ctypes
import os
import sys

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

# Create directories if they don't exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# =========================
# YOLOv5 (pretrained)
# =========================
model = torch.hub.load('ultralytics/yolov5:v7.0', 'yolov5n',
                       pretrained=True, trust_repo=True)
model.conf = 0.25
model.iou = 0.45
VEHICLE_KEYWORDS = ("car", "truck", "bus")

# =========================
# CSV logging
# =========================
log_filename = os.path.join(LOGS_DIR, f"detections_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
log_file = open(log_filename, "w", newline="")
writer = csv.writer(log_file)
writer.writerow(["time", "vehicle_detected", "confidence", "side",
                 "alert_level", "lane_departure", "distance_m", "rel_speed_mps"])
print(f"Logging to: {log_filename}")

# =========================
# Pygame (UI + sound)
# =========================
pygame.init()
try:
    pygame.mixer.init()
    beep_path = os.path.join(ASSETS_DIR, "beep.wav")
    if os.path.exists(beep_path):
        beep_sound = pygame.mixer.Sound(beep_path)
        print(f"Audio alerts enabled: {beep_path}")
    else:
        beep_sound = None
        print("Audio alerts disabled (beep.wav not found in assets/)")
except Exception as e:
    beep_sound = None
    print(f"Audio initialization failed: {e}")


# =========================
# Dashboard (single HUD compositor)
# =========================
def draw_dashboard(left_state, right_state, lane_state, prox_alert,
                   frame_left, frame_right, frame_front=None, frame_rear=None,
                   hud_speed_kph=0.0, hud_throttle=0.0, hud_brake=0.0,
                   hud_steer=0.0, hud_reverse=False):
    """Compose a single ADAS HUD (dashboard + 4 camera tiles + control HUD) in one cv2 window."""
    H, W = 900, 1280
    hud = np.zeros((H, W, 3), dtype=np.uint8)

    # ---- Title Bar ----
    cv2.rectangle(hud, (0, 0), (W, 60), (35, 35, 35), -1)
    cv2.putText(hud, "ADAS Dashboard", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (240, 240, 240), 2, cv2.LINE_AA)

    header_text = "WARNING!" if (left_state == "warn" or right_state == "warn" or lane_state or prox_alert == "warn") \
                  else ("CAUTION" if (left_state == "near" or right_state == "near" or prox_alert == "near") else "ALL CLEAR")
    header_color = (0, 0, 255) if header_text == "WARNING!" else ((0, 215, 255) if header_text == "CAUTION" else (0, 200, 0))
    cv2.putText(hud, header_text, (W - 240, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, header_color, 3, cv2.LINE_AA)

    # ---- Ego schematic block ----
    block_x, block_y, block_w, block_h = 20, 80, 560, 520
    cv2.rectangle(hud, (block_x, block_y), (block_x + block_w, block_y + block_h), (45, 45, 45), -1)

    # Car body
    body_top = block_y + 40
    body_h = block_h - 80
    body_w = int(body_h * 0.7)
    cx = block_x + block_w // 2
    car_x1, car_y1 = cx - body_w // 2, body_top
    car_x2, car_y2 = cx + body_w // 2, body_top + body_h
    cv2.rectangle(hud, (car_x1, car_y1), (car_x2, car_y2), (180, 180, 180), -1)

    # Blind spot bars
    def col_for(state):
        return (0, 0, 255) if state == "warn" else ((0, 215, 255) if state == "near" else (80, 80, 80))
    left_col = col_for(left_state)
    right_col = col_for(right_state)
    cv2.rectangle(hud, (car_x1 - 50, car_y1 + 10), (car_x1 - 15, car_y2 - 10), left_col, -1)
    cv2.rectangle(hud, (car_x2 + 15, car_y1 + 10), (car_x2 + 50, car_y2 - 10), right_col, -1)

    # Front / Rear arrows
    cv2.arrowedLine(hud, (cx, car_y1 - 10), (cx, car_y1 - 40), (220, 220, 220), 2, tipLength=0.4)
    cv2.putText(hud, "FRONT", (cx - 38, car_y1 - 48), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 2, cv2.LINE_AA)
    cv2.arrowedLine(hud, (cx, car_y2 + 10), (cx, car_y2 + 40), (220, 220, 220), 2, tipLength=0.4)
    cv2.putText(hud, "REAR", (cx - 28, car_y2 + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 2, cv2.LINE_AA)

    # Lane departure blink
    if lane_state and (int(time.time() * 2) % 2 == 0):
        cv2.putText(hud, "LANE DEPARTURE", (cx - 130, car_y1 + body_h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3, cv2.LINE_AA)

    # Status strip
    strip_y = block_y + block_h + 10
    cv2.rectangle(hud, (block_x, strip_y), (block_x + block_w, strip_y + 80), (30, 30, 30), -1)
    def put_kv(label, value, x, y, color=(200,200,200)):
        cv2.putText(hud, f"{label}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180,180,180), 2, cv2.LINE_AA)
        cv2.putText(hud, f"{value}", (x + 120, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)

    put_kv("Left",  left_state.upper(), block_x + 20,  strip_y + 30,
           (0,0,255) if left_state=="warn" else ((0,215,255) if left_state=="near" else (200,200,200)))
    put_kv("Right", right_state.upper(), block_x + 20,  strip_y + 60,
           (0,0,255) if right_state=="warn" else ((0,215,255) if right_state=="near" else (200,200,200)))
    put_kv("Prox",  prox_alert.upper(), block_x + 290, strip_y + 30,
           (0,0,255) if prox_alert=="warn" else ((0,215,255) if prox_alert=="near" else (200,200,200)))
    put_kv("Lane",  "ACTIVE" if lane_state else "OK", block_x + 290, strip_y + 60,
           (0,0,255) if lane_state else (200,200,200))

    # ---- 4 camera tiles (Right column) ----
    tile_w, tile_h = 320, 240
    cam_x = 600
    cam_positions = [(cam_x, 80), (cam_x + tile_w + 10, 80),
                     (cam_x, 80 + tile_h + 10), (cam_x + tile_w + 10, 80 + tile_h + 10)]
    cam_frames = [("Left Mirror", frame_left), ("Right Mirror", frame_right),
                  ("Front Camera", frame_front), ("Rear Camera", frame_rear)]
    for (title, frame), (tx, ty) in zip(cam_frames, cam_positions):
        cv2.rectangle(hud, (tx - 2, ty - 22), (tx + tile_w + 2, ty - 2), (35, 35, 35), -1)
        cv2.putText(hud, title, (tx + 8, ty - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220,220,220), 1, cv2.LINE_AA)
        if frame is not None:
            fr = cv2.resize(frame, (tile_w, tile_h))
        else:
            fr = np.zeros((tile_h, tile_w, 3), dtype=np.uint8)
            cv2.putText(fr, "No Feed", (88, 128), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 2, cv2.LINE_AA)
        hud[ty:ty+tile_h, tx:tx+tile_w] = fr

    # ---- Controls HUD (bottom-right) ----
    panel_x, panel_y, panel_w, panel_h = 600, 80 + 2*(tile_h + 10) + 10, 670, 180
    cv2.rectangle(hud, (panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h), (35, 35, 35), -1)
    cv2.putText(hud, "Controls", (panel_x + 16, panel_y + 32), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (240,240,240), 2, cv2.LINE_AA)
    cv2.putText(hud, "W: Throttle | S: Brake | A/D: Steer | SPACE: Reverse | ESC: Exit",
                (panel_x + 16, panel_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200,200,200), 1, cv2.LINE_AA)

    # Live speed
    cv2.putText(hud, f"Speed: {hud_speed_kph:5.1f} km/h", (panel_x + 16, panel_y + 92),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (180, 220, 255), 2, cv2.LINE_AA)

    # Bars
    def bar(x, y, width, frac, color):
        cv2.rectangle(hud, (x, y), (x + width, y + 18), (60, 60, 60), -1, cv2.LINE_AA)
        wfill = int(max(0, min(width, width * frac)))
        cv2.rectangle(hud, (x, y), (x + wfill, y + 18), color, -1, cv2.LINE_AA)
    bar(panel_x + 16, panel_y + 110, 220, hud_throttle, (120, 220, 120))
    bar(panel_x + 16, panel_y + 138, 220, hud_brake,    (220, 120, 120))
    bar(panel_x + 16, panel_y + 166, 220, (hud_steer + 1) / 2.0, (120, 180, 240))
    cv2.putText(hud, "Throttle", (panel_x + 246, panel_y + 125), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200,200,200), 1, cv2.LINE_AA)
    cv2.putText(hud, "Brake",    (panel_x + 246, panel_y + 153), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200,200,200), 1, cv2.LINE_AA)
    cv2.putText(hud, "Steer",    (panel_x + 246, panel_y + 181), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200,200,200), 1, cv2.LINE_AA)

    # Reverse indicator
    rev_text = "Reverse: ON" if hud_reverse else "Reverse: OFF"
    rev_col  = (0, 165, 255) if hud_reverse else (180, 180, 180)
    cv2.putText(hud, rev_text, (panel_x + 420, panel_y + 125), cv2.FONT_HERSHEY_SIMPLEX, 0.7, rev_col, 2, cv2.LINE_AA)

    # Small status dot (mirrors alert severity)
    status_color = (0,0,255) if (left_state=="warn" or right_state=="warn" or lane_state) else \
                   ((0,215,255) if (left_state=="near" or right_state=="near" or prox_alert=="near") else (120,220,120))
    cv2.circle(hud, (panel_x + panel_w - 28, panel_y + 28), 10, status_color, -1, cv2.LINE_AA)

    # ---- single window ----
    cv2.imshow("ADAS HUD", hud)


# =========================
# Camera processing
# =========================
def process_image(image, state, side="left"):
    """YOLO detection + return frame + alert state."""
    array = np.frombuffer(image.raw_data, dtype=np.uint8)
    array = np.reshape(array, (image.height, image.width, 4))[:, :, :3].copy()

    rgb = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
    results = model(rgb)

    alert_level = "clear"
    if len(results.xyxy) > 0 and results.xyxy[0] is not None:
        detections = results.xyxy[0].cpu().numpy()
        names = model.names
        for det in detections:
            x1, y1, x2, y2, conf, cls_id = det
            label = names[int(cls_id)].lower()

            if any(k in label for k in VEHICLE_KEYWORDS):
                h, w, _ = array.shape
                box_center_x = (x1 + x2) / 2
                box_height = y2 - y1

                if side == "left":
                    if 0.05 * w < box_center_x < 0.35 * w:
                        alert_level = "near"
                        if box_height > 0.25 * h: alert_level = "warn"
                else:
                    if 0.65 * w < box_center_x < 0.95 * w:
                        alert_level = "near"
                        if box_height > 0.25 * h: alert_level = "warn"

                writer.writerow([datetime.datetime.now(), label, float(conf),
                                 side, alert_level, "", "", ""])

    state["level"] = alert_level
    if alert_level == "warn" and beep_sound: beep_sound.play()
    return array

# --- NEW: lightweight detection on numpy frame (used in main loop) ---
def detect_blindspot_frame(array, state, side="left"):
    """Run YOLOv5 on an already-decoded numpy image; update state & CSV."""
    if array is None:
        return
    rgb = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
    results = model(rgb)

    alert_level = "clear"
    if len(results.xyxy) > 0 and results.xyxy[0] is not None:
        detections = results.xyxy[0].cpu().numpy()
        names = model.names
        for det in detections:
            x1, y1, x2, y2, conf, cls_id = det
            label = names[int(cls_id)].lower()

            if any(k in label for k in VEHICLE_KEYWORDS):
                h, w, _ = array.shape
                box_center_x = (x1 + x2) / 2
                box_height = y2 - y1

                if side == "left":
                    if 0.05 * w < box_center_x < 0.35 * w:
                        alert_level = "near"
                        if box_height > 0.25 * h: alert_level = "warn"
                else:
                    if 0.65 * w < box_center_x < 0.95 * w:
                        alert_level = "near"
                        if box_height > 0.25 * h: alert_level = "warn"

                writer.writerow([datetime.datetime.now(), label, float(conf),
                                 side, alert_level, "", "", ""])

    state["level"] = alert_level
    if alert_level == "warn" and beep_sound:
        beep_sound.play()


# =========================
# Proximity
# =========================
def check_proximity(world, vehicle):
    ego_loc = vehicle.get_location()
    ego_vel = vehicle.get_velocity().length()

    min_dist = 9999
    rel_speed = 0
    alert = "clear"

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

    return alert


# =========================
# Helpers
# =========================
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


# =========================
# Manual drive
# =========================
def manual_control(vehicle, world, left_state, right_state, lane_state,
                   shared_left, shared_right, shared_front, shared_rear):
    # Hidden pygame window (we only use it for quit events; keys are read globally)
    screen = pygame.display.set_mode((1, 1), pygame.HIDDEN)
    pygame.display.set_caption("Vehicle Control")
    clock = pygame.time.Clock()

    # Windows virtual key codes
    VK_W, VK_A, VK_S, VK_D = 0x57, 0x41, 0x53, 0x44
    VK_ESC, VK_SPACE = 0x1B, 0x20
    GetAsyncKeyState = ctypes.windll.user32.GetAsyncKeyState

    reverse_mode = False
    prev_space_down = False

    while True:
        control = carla.VehicleControl()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        w_down = (GetAsyncKeyState(VK_W) & 0x8000) != 0
        a_down = (GetAsyncKeyState(VK_A) & 0x8000) != 0
        s_down = (GetAsyncKeyState(VK_S) & 0x8000) != 0
        d_down = (GetAsyncKeyState(VK_D) & 0x8000) != 0
        esc_down = (GetAsyncKeyState(VK_ESC) & 0x8000) != 0
        space_down = (GetAsyncKeyState(VK_SPACE) & 0x8000) != 0

        if esc_down:
            return

        if space_down and not prev_space_down:
            reverse_mode = not reverse_mode
        prev_space_down = space_down

        if w_down:
            control.throttle = 1.0
        if s_down:
            control.brake = 1.0
        if a_down:
            control.steer = -0.5
        if d_down:
            control.steer = 0.5

        control.reverse = reverse_mode

        vehicle.apply_control(control)
        world.tick()

        follow_vehicle_spectator(world, vehicle)
        prox_alert = check_proximity(world, vehicle)

        frame_left  = shared_left["frame"]
        frame_right = shared_right["frame"]
        frame_front = shared_front["frame"]
        frame_rear  = shared_rear["frame"]

        # Run blind-spot detection here (lightweight callbacks -> smooth mirrors)
        if frame_left is not None:
            detect_blindspot_frame(frame_left, left_state, "left")
        if frame_right is not None:
            detect_blindspot_frame(frame_right, right_state, "right")

        vel = vehicle.get_velocity()
        speed_mps = math.sqrt(vel.x**2 + vel.y**2 + vel.z**2)
        speed_kph = speed_mps * 3.6

        draw_dashboard(left_state["level"], right_state["level"],
            lane_state["active"], prox_alert,
            frame_left, frame_right, frame_front, frame_rear,
            hud_speed_kph=speed_kph,
            hud_throttle=control.throttle,
            hud_brake=control.brake,
            hud_steer=control.steer,
            hud_reverse=reverse_mode)

        cv2.waitKey(1)
        clock.tick(60)


# =========================
# Main
# =========================
def main():
    actor_list = []
    camera_left = camera_right = lane_sensor = None
    camera_front = camera_rear = None
    lane_state = {"active": False}
    shared_left, shared_right = {"frame": None}, {"frame": None}
    shared_front, shared_rear = {"frame": None}, {"frame": None}
    left_state, right_state = {"level": "clear"}, {"level": "clear"}

    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(10.0)
        world = client.get_world()

        # Synchronous mode
        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 0.05
        world.apply_settings(settings)

        bp_lib = world.get_blueprint_library()
        vehicle_bp = random.choice(bp_lib.filter('vehicle.*'))
        transform = random.choice(world.get_map().get_spawn_points())
        vehicle = world.spawn_actor(vehicle_bp, transform)
        vehicle.set_autopilot(False)
        actor_list.append(vehicle)

        # Lane invasion sensor
        lane_bp = bp_lib.find('sensor.other.lane_invasion')
        lane_sensor = world.spawn_actor(lane_bp, carla.Transform(), attach_to=vehicle)
        actor_list.append(lane_sensor)
        lane_sensor.listen(lambda e: lane_state.update({"active": True}))

        # Cameras
        cam_bp = bp_lib.find('sensor.camera.rgb')
        cam_bp.set_attribute('image_size_x', '320')
        cam_bp.set_attribute('image_size_y', '240')
        cam_bp.set_attribute('fov', '100')

        cam_left = carla.Transform(carla.Location(x=-1.0, y=-1.2, z=1.6),
                                   carla.Rotation(yaw=-90.0))
        cam_right = carla.Transform(carla.Location(x=-1.0, y=1.2, z=1.6),
                                    carla.Rotation(yaw=90.0))
        cam_front = carla.Transform(carla.Location(x=1.5, y=0.0, z=1.6),
                                    carla.Rotation(yaw=0.0))
        cam_rear = carla.Transform(carla.Location(x=-1.5, y=0.0, z=1.6),
                                   carla.Rotation(yaw=180.0))

        camera_left = world.spawn_actor(cam_bp, cam_left, attach_to=vehicle)
        camera_right = world.spawn_actor(cam_bp, cam_right, attach_to=vehicle)
        camera_front = world.spawn_actor(cam_bp, cam_front, attach_to=vehicle)
        camera_rear = world.spawn_actor(cam_bp, cam_rear, attach_to=vehicle)
        actor_list += [camera_left, camera_right, camera_front, camera_rear]

        # ---- Lightweight listeners (NO inference in callbacks) ----
        camera_left.listen(lambda img: shared_left.update({
            "frame": np.reshape(np.frombuffer(img.raw_data, dtype=np.uint8),
                                (img.height, img.width, 4))[:, :, :3].copy()
        }))
        camera_right.listen(lambda img: shared_right.update({
            "frame": np.reshape(np.frombuffer(img.raw_data, dtype=np.uint8),
                                (img.height, img.width, 4))[:, :, :3].copy()
        }))

        def _to_array(image):
            arr = np.frombuffer(image.raw_data, dtype=np.uint8)
            return np.reshape(arr, (image.height, image.width, 4))[:, :, :3].copy()
        camera_front.listen(lambda img: shared_front.update({"frame": _to_array(img)}))
        camera_rear.listen(lambda img: shared_rear.update({"frame": _to_array(img)}))

        # Spawn NPCs
        npcs = spawn_npc_traffic(world, client, 20)
        actor_list.extend(npcs)

        manual_control(vehicle, world, left_state, right_state, lane_state,
                       shared_left, shared_right, shared_front, shared_rear)

    finally:
        print("Cleaning up...")
        for actor in actor_list:
            try: actor.destroy()
            except: pass
        if camera_left: camera_left.stop()
        if camera_right: camera_right.stop()
        if camera_front: camera_front.stop()
        if camera_rear: camera_rear.stop()
        if lane_sensor: lane_sensor.stop()
        log_file.close()
        cv2.destroyAllWindows()
        pygame.quit()


if __name__ == '__main__':
    main()
