#!/usr/bin/env python
"""
EV Infotainment System - ADAS Dashboard
Main application with UI rendering and vehicle control.
"""

import random
import numpy as np
import cv2
import carla
import pygame
import time
import math
import platform
from adas_config import (DETECTION_SKIP_FRAMES, TARGET_FPS, WARNING_CLEAR_TIME, 
                         audio_alerts, log_file)
from adas_utils import (detect_blindspot_frame, check_proximity, 
                        follow_vehicle_spectator, spawn_npc_traffic)

# Windows-specific imports
if platform.system() == 'Windows':
    import ctypes

def draw_camera_panel(frame_left, frame_right, frame_front=None, frame_rear=None):
    """Display 4 camera feeds in a separate window."""
    tile_w, tile_h = 320, 240
    title_h = 40
    gap = 10
    H = title_h + (tile_h + 22) * 2 + gap
    W = tile_w * 2 + gap * 3
    panel = np.zeros((H, W, 3), dtype=np.uint8)
    
    # Title bar
    cv2.rectangle(panel, (0, 0), (W, title_h), (35, 35, 35), -1)
    cv2.putText(panel, "Camera Feeds", (20, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (240, 240, 240), 2, cv2.LINE_AA)
    
    # 4 camera tiles in 2x2 grid
    cam_positions = [(gap, title_h + 22), (tile_w + gap * 2, title_h + 22),
                     (gap, title_h + 22 + tile_h + gap + 22), (tile_w + gap * 2, title_h + 22 + tile_h + gap + 22)]
    cam_frames = [("Left Mirror", frame_left), ("Right Mirror", frame_right),
                  ("Front Camera", frame_front), ("Rear Camera", frame_rear)]
    
    for (title, frame), (tx, ty) in zip(cam_frames, cam_positions):
        cv2.rectangle(panel, (tx - 2, ty - 22), (tx + tile_w + 2, ty - 2), (35, 35, 35), -1)
        cv2.putText(panel, title, (tx + 8, ty - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1, cv2.LINE_AA)
        if frame is not None:
            fr = cv2.resize(frame, (tile_w, tile_h), interpolation=cv2.INTER_NEAREST)
        else:
            fr = np.zeros((tile_h, tile_w, 3), dtype=np.uint8)
            cv2.putText(fr, "No Feed", (88, 128), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2, cv2.LINE_AA)
        panel[ty:ty+tile_h, tx:tx+tile_w] = fr
    
    cv2.imshow("Camera Feeds", panel)

def draw_dashboard(left_state, right_state, lane_state, prox_alert,
                   hud_speed_kph=0.0, hud_throttle=0.0, hud_brake=0.0,
                   hud_steer=0.0, hud_reverse=False):
    """Main ADAS dashboard with vehicle schematic and controls."""
    H, W = 820, 600
    hud = np.zeros((H, W, 3), dtype=np.uint8)
    cv2.rectangle(hud, (0, 0), (W, 60), (35, 35, 35), -1)
    cv2.putText(hud, "ADAS Dashboard", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (240, 240, 240), 2, cv2.LINE_AA)
    header_text = "WARNING!" if (left_state == "warn" or right_state == "warn" or lane_state or prox_alert == "warn") \
                  else ("CAUTION" if (left_state == "near" or right_state == "near" or prox_alert == "near") else "ALL CLEAR")
    header_color = (0, 0, 255) if header_text == "WARNING!" else ((0, 215, 255) if header_text == "CAUTION" else (0, 200, 0))
    cv2.putText(hud, header_text, (W - 240, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, header_color, 3, cv2.LINE_AA)
    block_x, block_y, block_w, block_h = 20, 80, 560, 460
    cv2.rectangle(hud, (block_x, block_y), (block_x + block_w, block_y + block_h), (45, 45, 45), -1)
    body_top = block_y + 100
    body_h = block_h - 200
    body_w = int(body_h * 0.45)
    cx = block_x + block_w // 2
    car_x1, car_y1 = cx - body_w // 2, body_top
    car_x2, car_y2 = cx + body_w // 2, body_top + body_h
    car_body_color = (180, 180, 180)
    cv2.ellipse(hud, (cx, car_y1 + 20), (body_w // 2, 20), 0, 180, 360, car_body_color, -1)
    cv2.rectangle(hud, (car_x1, car_y1 + 20), (car_x2, car_y2 - 20), car_body_color, -1)
    cv2.ellipse(hud, (cx, car_y2 - 20), (body_w // 2, 20), 0, 0, 180, car_body_color, -1)
    cv2.ellipse(hud, (cx, car_y1 + 20), (body_w // 2, 20), 0, 180, 360, (120, 120, 120), 2)
    cv2.line(hud, (car_x1, car_y1 + 20), (car_x1, car_y2 - 20), (120, 120, 120), 2)
    cv2.line(hud, (car_x2, car_y1 + 20), (car_x2, car_y2 - 20), (120, 120, 120), 2)
    cv2.ellipse(hud, (cx, car_y2 - 20), (body_w // 2, 20), 0, 0, 180, (120, 120, 120), 2)
    windshield_y = car_y1 + 25
    windshield_h = 40
    cv2.rectangle(hud, (car_x1 + 5, windshield_y), (car_x2 - 5, windshield_y + windshield_h), (80, 120, 180), -1)
    rear_window_y = car_y2 - 45
    rear_window_h = 25
    cv2.rectangle(hud, (car_x1 + 5, rear_window_y), (car_x2 - 5, rear_window_y + rear_window_h), (80, 120, 180), -1)
    cabin_y = windshield_y + windshield_h
    cabin_h = rear_window_y - cabin_y
    cv2.rectangle(hud, (car_x1 + 8, cabin_y), (car_x2 - 8, cabin_y + cabin_h), (150, 150, 150), -1)
    mirror_w, mirror_h = 8, 18
    mirror_offset_y = car_y1 + 60
    cv2.rectangle(hud, (car_x1 - mirror_w - 3, mirror_offset_y), (car_x1 - 3, mirror_offset_y + mirror_h), (140, 140, 140), -1)
    cv2.rectangle(hud, (car_x1 - mirror_w - 3, mirror_offset_y), (car_x1 - 3, mirror_offset_y + mirror_h), (100, 100, 100), 1)
    cv2.rectangle(hud, (car_x2 + 3, mirror_offset_y), (car_x2 + mirror_w + 3, mirror_offset_y + mirror_h), (140, 140, 140), -1)
    cv2.rectangle(hud, (car_x2 + 3, mirror_offset_y), (car_x2 + mirror_w + 3, mirror_offset_y + mirror_h), (100, 100, 100), 1)
    wheel_w, wheel_h = 10, 35
    wheel_color = (40, 40, 40)
    cv2.rectangle(hud, (car_x1 - wheel_w, car_y1 + 35), (car_x1, car_y1 + 35 + wheel_h), wheel_color, -1)
    cv2.rectangle(hud, (car_x2, car_y1 + 35), (car_x2 + wheel_w, car_y1 + 35 + wheel_h), wheel_color, -1)
    cv2.rectangle(hud, (car_x1 - wheel_w, car_y2 - 70), (car_x1, car_y2 - 70 + wheel_h), wheel_color, -1)
    cv2.rectangle(hud, (car_x2, car_y2 - 70), (car_x2 + wheel_w, car_y2 - 70 + wheel_h), wheel_color, -1)
    cv2.putText(hud, "T", (cx - 6, car_y1 + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(hud, "Model 3", (cx - 32, car_y2 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA)
    arrow_start_y = car_y1 + 100
    arrow_end_y = car_y1 + 40
    cv2.arrowedLine(hud, (cx, arrow_start_y), (cx, arrow_end_y), (255, 200, 0), 3, tipLength=0.3)
    def col_for(state):
        return (0, 0, 255) if state == "warn" else ((0, 215, 255) if state == "near" else (80, 80, 80))
    left_col = col_for(left_state)
    right_col = col_for(right_state)
    cv2.rectangle(hud, (car_x1 - 80, car_y1 + 50), (car_x1 - 15, car_y2 - 50), left_col, -1)
    cv2.putText(hud, "LEFT", (car_x1 - 70, cx - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.rectangle(hud, (car_x2 + 15, car_y1 + 50), (car_x2 + 80, car_y2 - 50), right_col, -1)
    cv2.putText(hud, "RIGHT", (car_x2 + 20, cx - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.arrowedLine(hud, (cx, car_y1 - 10), (cx, car_y1 - 40), (220, 220, 220), 2, tipLength=0.4)
    cv2.putText(hud, "FRONT", (cx - 38, car_y1 - 48), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 2, cv2.LINE_AA)
    cv2.arrowedLine(hud, (cx, car_y2 + 10), (cx, car_y2 + 40), (220, 220, 220), 2, tipLength=0.4)
    cv2.putText(hud, "REAR", (cx - 28, car_y2 + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 2, cv2.LINE_AA)
    if lane_state and (int(time.time() * 2) % 2 == 0):
        cv2.putText(hud, "LANE DEPARTURE", (cx - 130, car_y1 + body_h // 2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3, cv2.LINE_AA)
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
    
    # Controls panel below status
    panel_x, panel_y, panel_w, panel_h = 20, strip_y + 90, 560, 180
    cv2.rectangle(hud, (panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h), (35, 35, 35), -1)
    cv2.putText(hud, "Vehicle Controls", (panel_x + 16, panel_y + 32), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (240,240,240), 2, cv2.LINE_AA)
    cv2.putText(hud, "W: Throttle | S: Brake | A/D: Steer | SPACE: Reverse | ESC: Exit",
                (panel_x + 16, panel_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (200,200,200), 1, cv2.LINE_AA)
    cv2.putText(hud, f"Speed: {hud_speed_kph:5.1f} km/h", (panel_x + 16, panel_y + 92),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (180, 220, 255), 2, cv2.LINE_AA)
    def bar(x, y, width, frac, color, label):
        cv2.rectangle(hud, (x, y), (x + width, y + 18), (60, 60, 60), -1, cv2.LINE_AA)
        wfill = int(max(0, min(width, width * frac)))
        cv2.rectangle(hud, (x, y), (x + wfill, y + 18), color, -1, cv2.LINE_AA)
        cv2.putText(hud, label, (x + width + 10, y + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (200,200,200), 1, cv2.LINE_AA)
    bar(panel_x + 16, panel_y + 110, 180, hud_throttle, (120, 220, 120), "Throttle")
    bar(panel_x + 16, panel_y + 136, 180, hud_brake, (220, 120, 120), "Brake")
    bar(panel_x + 16, panel_y + 162, 180, (hud_steer + 1) / 2.0, (120, 180, 240), "Steer")
    rev_text = "Reverse: ON" if hud_reverse else "Reverse: OFF"
    rev_col  = (0, 165, 255) if hud_reverse else (180, 180, 180)
    cv2.putText(hud, rev_text, (panel_x + 320, panel_y + 92), cv2.FONT_HERSHEY_SIMPLEX, 0.7, rev_col, 2, cv2.LINE_AA)
    status_color = (0,0,255) if (left_state=="warn" or right_state=="warn" or lane_state) else \
                   ((0,215,255) if (left_state=="near" or right_state=="near" or prox_alert=="near") else (120,220,120))
    cv2.circle(hud, (panel_x + panel_w - 22, panel_y + 24), 10, status_color, -1, cv2.LINE_AA)
    cv2.imshow("ADAS HUD", hud)

def manual_control(vehicle, world, left_state, right_state, lane_state, prox_state,
                   shared_left, shared_right, shared_front, shared_rear):
    screen = pygame.display.set_mode((1, 1), pygame.HIDDEN)
    pygame.display.set_caption("Vehicle Control")
    clock = pygame.time.Clock()
    is_windows = platform.system() == 'Windows'
    if is_windows:
        VK_W, VK_A, VK_S, VK_D = 0x57, 0x41, 0x53, 0x44
        VK_ESC, VK_SPACE = 0x1B, 0x20
        GetAsyncKeyState = ctypes.windll.user32.GetAsyncKeyState
    else:
        print("Warning: Non-Windows system detected. Keyboard controls may not work properly.")
    reverse_mode = False
    prev_space_down = False
    frame_counter = 0
    detection_interval = DETECTION_SKIP_FRAMES
    while True:
        control = carla.VehicleControl()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        if is_windows:
            w_down = (GetAsyncKeyState(VK_W) & 0x8000) != 0
            a_down = (GetAsyncKeyState(VK_A) & 0x8000) != 0
            s_down = (GetAsyncKeyState(VK_S) & 0x8000) != 0
            d_down = (GetAsyncKeyState(VK_D) & 0x8000) != 0
            esc_down = (GetAsyncKeyState(VK_ESC) & 0x8000) != 0
            space_down = (GetAsyncKeyState(VK_SPACE) & 0x8000) != 0
        else:
            keys = pygame.key.get_pressed()
            w_down = keys[pygame.K_w]
            a_down = keys[pygame.K_a]
            s_down = keys[pygame.K_s]
            d_down = keys[pygame.K_d]
            esc_down = keys[pygame.K_ESCAPE]
            space_down = keys[pygame.K_SPACE]
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
        try:
            vehicle.apply_control(control)
            world.tick()
        except RuntimeError as e:
            print(f"Runtime error during simulation tick: {e}")
            return
        follow_vehicle_spectator(world, vehicle)
        prox_alert = check_proximity(world, vehicle, prox_state)
        frame_left  = shared_left["frame"]
        frame_right = shared_right["frame"]
        frame_front = shared_front["frame"]
        frame_rear  = shared_rear["frame"]
        frame_counter += 1
        if frame_counter >= detection_interval:
            frame_counter = 0
            if frame_left is not None:
                detect_blindspot_frame(frame_left, left_state, "left")
            if frame_right is not None:
                detect_blindspot_frame(frame_right, right_state, "right")
        if lane_state["active"]:
            if time.time() - lane_state.get("last_detection", 0) > WARNING_CLEAR_TIME:
                lane_state["active"] = False
        vel = vehicle.get_velocity()
        speed_mps = math.sqrt(vel.x**2 + vel.y**2 + vel.z**2)
        speed_kph = speed_mps * 3.6
        
        # Draw separate windows
        draw_dashboard(left_state["level"], right_state["level"],
            lane_state["active"], prox_alert,
            hud_speed_kph=speed_kph,
            hud_throttle=control.throttle,
            hud_brake=control.brake,
            hud_steer=control.steer,
            hud_reverse=reverse_mode)
        
        draw_camera_panel(frame_left, frame_right, frame_front, frame_rear)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            print("ESC pressed, exiting...")
            return
        # Check if either window was closed (X button clicked)
        if cv2.getWindowProperty("ADAS HUD", cv2.WND_PROP_VISIBLE) < 1 or \
           cv2.getWindowProperty("Camera Feeds", cv2.WND_PROP_VISIBLE) < 1:
            print("Window closed, exiting...")
            return
        clock.tick(TARGET_FPS)

def main():
    print("=" * 60)
    print("EV Infotainment System - ADAS Dashboard")
    print("=" * 60)
    print()
    actor_list = []
    camera_left = camera_right = lane_sensor = None
    camera_front = camera_rear = None
    lane_state = {"active": False, "last_detection": 0}
    shared_left, shared_right = {"frame": None}, {"frame": None}
    shared_front, shared_rear = {"frame": None}, {"frame": None}
    left_state, right_state = {"level": "clear", "last_detection": 0}, {"level": "clear", "last_detection": 0}
    prox_state = {"level": "clear", "last_detection": 0}
    try:
        print("Connecting to CARLA simulator...")
        client = carla.Client('localhost', 2000)
        client.set_timeout(10.0)
        max_retries = 3
        retry_delay = 5
        for attempt in range(max_retries):
            try:
                world = client.get_world()
                print(f"✓ Connected to CARLA simulator (Map: {world.get_map().name})")
                break
            except RuntimeError as e:
                if attempt < max_retries - 1:
                    print(f"⚠ Connection attempt {attempt + 1} failed. Retrying in {retry_delay} seconds...")
                    print(f"   Make sure CarlaUE4.exe is running!")
                    time.sleep(retry_delay)
                else:
                    print("✗ Failed to connect to CARLA simulator.")
                    print("\nPlease ensure:")
                    print("  1. CARLA is running: cd CARLA_0.9.15\\WindowsNoEditor && .\\CarlaUE4.exe")
                    print("  2. CARLA has fully loaded (you should see the simulator window)")
                    print("  3. CARLA is listening on port 2000 (default)")
                    raise
        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 0.05
        world.apply_settings(settings)
        bp_lib = world.get_blueprint_library()
        try:
            vehicle_bp = bp_lib.find('vehicle.tesla.model3')
            print("✓ Using Tesla Model 3 as ego vehicle")
        except:
            vehicle_bp = bp_lib.find('vehicle.audi.a2')
            print("✓ Using Audi A2 as ego vehicle (Tesla not available)")
        transform = random.choice(world.get_map().get_spawn_points())
        vehicle = world.spawn_actor(vehicle_bp, transform)
        vehicle.set_autopilot(False)
        actor_list.append(vehicle)
        print(f"✓ Spawned ego vehicle: {vehicle.type_id}")
        lane_bp = bp_lib.find('sensor.other.lane_invasion')
        lane_sensor = world.spawn_actor(lane_bp, carla.Transform(), attach_to=vehicle)
        actor_list.append(lane_sensor)
        def on_lane_invasion(event):
            was_clear = not lane_state.get("active", False)
            lane_state.update({"active": True, "last_detection": time.time()})
            if was_clear and audio_alerts["lane"]:
                audio_alerts["lane"].play()
        lane_sensor.listen(on_lane_invasion)
        cam_bp = bp_lib.find('sensor.camera.rgb')
        cam_bp.set_attribute('image_size_x', '320')
        cam_bp.set_attribute('image_size_y', '240')
        cam_bp.set_attribute('fov', '100')
        cam_left = carla.Transform(carla.Location(x=-1.0, y=-1.2, z=1.6), carla.Rotation(yaw=-90.0))
        cam_right = carla.Transform(carla.Location(x=-1.0, y=1.2, z=1.6), carla.Rotation(yaw=90.0))
        cam_front = carla.Transform(carla.Location(x=1.5, y=0.0, z=1.6), carla.Rotation(yaw=0.0))
        cam_rear = carla.Transform(carla.Location(x=-1.5, y=0.0, z=1.6), carla.Rotation(yaw=180.0))
        camera_left = world.spawn_actor(cam_bp, cam_left, attach_to=vehicle)
        camera_right = world.spawn_actor(cam_bp, cam_right, attach_to=vehicle)
        camera_front = world.spawn_actor(cam_bp, cam_front, attach_to=vehicle)
        camera_rear = world.spawn_actor(cam_bp, cam_rear, attach_to=vehicle)
        actor_list += [camera_left, camera_right, camera_front, camera_rear]
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
        npcs = spawn_npc_traffic(world, client, 20)
        actor_list.extend(npcs)
        manual_control(vehicle, world, left_state, right_state, lane_state, prox_state,
                       shared_left, shared_right, shared_front, shared_rear)
    finally:
        print("Cleaning up...")
        for actor in actor_list:
            try: 
                actor.destroy()
            except Exception as e:
                print(f"Warning: Failed to destroy actor: {e}")
        for sensor in [camera_left, camera_right, camera_front, camera_rear, lane_sensor]:
            if sensor:
                try:
                    sensor.stop()
                except Exception as e:
                    print(f"Warning: Failed to stop sensor: {e}")
        try:
            log_file.close()
        except Exception as e:
            print(f"Warning: Failed to close log file: {e}")
        cv2.destroyAllWindows()
        pygame.quit()
        print("Cleanup complete.")

if __name__ == '__main__':
    main()
