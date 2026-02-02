import cv2
import threading
import time
import mediapipe as mp
import numpy as np
import logging
from reachy_mini.utils import create_head_pose

logger = logging.getLogger("HeadMirroring")

class HeadMirroringController:
    """PERFECT: Ultra-smooth head tracking."""
    
    def __init__(self, reachy_mini):
        self.mini = reachy_mini
        self.running = False
        self.thread = None
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1, min_detection_confidence=0.6,
            min_tracking_confidence=0.6, refine_landmarks=False)
        
        # PERFECT smoothing
        self.smoothing = 0.25
        self.prev_pitch = self.prev_yaw = self.prev_roll = 0
        self.pitch_offset = self.yaw_offset = self.roll_offset = 0
        self.calibrated = False
        
        self.face_3d_model = np.array([
            (0.0, 0.0, 0.0), (0.0, -330.0, -65.0),
            (-225.0, 170.0, -135.0), (225.0, 170.0, -135.0),
            (-150.0, -150.0, -125.0), (150.0, -150.0, -125.0)], dtype=np.float64)
        self.key_landmarks = [1, 152, 263, 33, 291, 61]

    def start_mirroring(self, camera_index=0):
        if self.running: return
        self.running = True
        self.calibrated = False
        self.thread = threading.Thread(target=self._mirror_loop, args=(camera_index,), daemon=True)
        self.thread.start()
        logger.info("Mirroring started")

    def stop_mirroring(self):
        self.running = False
        if self.thread: self.thread.join(timeout=1.0)
        logger.info("Mirroring stopped")

    def _mirror_loop(self, camera_index):
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            logger.error("Camera failed")
            self.running = False
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
        cap.set(cv2.CAP_PROP_FPS, 30)

        frame_count = 0
        while self.running and cap.isOpened():
            frame_count += 1
            success, image = cap.read()
            if not success:
                time.sleep(0.01)
                continue

            # Process every 2nd frame
            if frame_count % 2 != 0:
                time.sleep(0.005)
                continue

            image = cv2.flip(image, 1)
            img_h, img_w = image.shape[:2]
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            results = self.face_mesh.process(image_rgb)
            
            if results.multi_face_landmarks:
                pose = self.calculate_head_pose(results.multi_face_landmarks[0], img_w, img_h)
                if not self.calibrated:
                    self.pitch_offset, self.yaw_offset, self.roll_offset = pose['pitch'], pose['yaw'], pose['roll']
                    self.calibrated = True
                self.mirror_to_reachy(pose)
            time.sleep(0.01)
        cap.release()

    def calculate_head_pose(self, face_landmarks, img_w, img_h):
        """Fast pose calc."""
        face_2d = np.array([[int(face_landmarks.landmark[i].x * img_w), 
                            int(face_landmarks.landmark[i].y * img_h)] 
                           for i in self.key_landmarks], dtype=np.float64)
        focal = img_w
        cam_matrix = np.array([[focal, 0, img_w/2], [0, focal, img_h/2], [0, 0, 1]])
        success, rot_vec, _ = cv2.solvePnP(self.face_3d_model, face_2d, cam_matrix, 
                                           np.zeros((4, 1)), flags=cv2.SOLVEPNP_ITERATIVE)
        if not success:
            return {'pitch': 0, 'yaw': 0, 'roll': 0}
        rmat, _ = cv2.Rodrigues(rot_vec)
        euler = cv2.decomposeProjectionMatrix(np.hstack((rmat, rot_vec)))[6]
        return {'pitch': float(euler[0,0]), 'yaw': float(euler[1,0]), 'roll': float(euler[2,0])}

    def mirror_to_reachy(self, pose):
        """PERFECT sync."""
        raw_pitch = pose['pitch'] - self.pitch_offset
        raw_yaw = pose['yaw'] - self.yaw_offset
        raw_roll = pose['roll'] - self.roll_offset

        pitch = self.prev_pitch * self.smoothing + raw_pitch * (1 - self.smoothing)
        yaw = self.prev_yaw * self.smoothing + raw_yaw * (1 - self.smoothing)
        roll = self.prev_roll * self.smoothing + raw_roll * (1 - self.smoothing)
        self.prev_pitch, self.prev_yaw, self.prev_roll = pitch, yaw, roll

        final_pitch = np.clip(-pitch, -20, 20)
        final_yaw = np.clip(yaw, -40, 40)
        final_roll = np.clip(roll, -30, 30)
        
        if abs(final_pitch) < 1.5: final_pitch = 0
        if abs(final_yaw) < 1.5: final_yaw = 0
        if abs(final_roll) < 1.5: final_roll = 0

        try:
            head_pos = create_head_pose(0, 0, 0, final_roll, final_pitch, final_yaw, mm=True, degrees=True)
            self.mini.goto_target(head_pos, duration=0.1)
        except Exception as e:
            logger.debug(f"Error: {e}")