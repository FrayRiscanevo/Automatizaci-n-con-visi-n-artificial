import cv2
import numpy as np
import socket
import time

# ---------------------------------------
# CÁMARA
# ---------------------------------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("No se pudo abrir la cámara")
    exit()

# Matriz de cámara (aprox)
fx = 800; fy = 800; cx = 320; cy = 240
camera_matrix = np.array([[fx, 0, cx],
                          [0, fy, cy],
                          [0,  0,  1]], dtype=np.float32)
dist_coeffs = np.zeros(5)

# ArUco
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
marker_length = 0.02  # 5 cm
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

# ---------------------------------------
# SOCKET A RAPID
# ---------------------------------------
HOST = "192.168.0.101"
PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
print("Conectado a RAPID\n")

# ---------------------------------------
# CONTROL TIEMPO
# ---------------------------------------
last_send = 0.0
send_interval = 0.3  # segundos

# ---------------------------------------
# PARÁMETROS DE CONTROL
# ---------------------------------------

# Distancia objetivo: 20 cm
d_obj = 0.20  # metros

# Escalas (ya viste que 100 te funcionaba bien)
Sdist = 100.0   # para distancia (eje X del robot)
Slat  = 100.0   # para lateral (eje Y del robot)
Salt  = 100.0   # para altura (eje Z del robot)

# Límite de rango para no mandar locuras (en mm)
MAX_VAL = 200.0  # ±200 mm

print("Controlando para que la distancia sea 20 cm,")
print("corrigiendo X(front), Y(lateral), Z(altura) respecto al robot.\n")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error leyendo frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = detector.detectMarkers(gray)

        if ids is not None:
            # Pose del primer marcador
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, marker_length, camera_matrix, dist_coeffs
            )

            tx, ty, tz = tvecs[0][0]   # metros
            dist = float(np.linalg.norm(tvecs[0][0]))

            # -----------------------------
            # MAPEOS CÁMARA -> ROBOT
            # -----------------------------
            # Cámara:
            #   tx: + derecha / - izquierda
            #   ty: + abajo / - arriba
            #   tz: + hacia el frente (distancia)
            #
            # RobotStudio:
            #   X_robot: frente
            #   Y_robot: lateral
            #   Z_robot: arriba
            #
            # Queremos:
            #   - Controlar distancia en X_robot usando tz
            #   - Centrar lateral en Y_robot usando tx
            #   - Centrar altura en Z_robot usando ty

            # Error de distancia respecto a 20 cm
            err_z_cam = tz - d_obj   # tz < d_obj  => error negativo (demasiado cerca)

            # X_robot (frente): si estoy lejos, positivo; si estoy muy cerca, negativo
            X_mm = err_z_cam * Sdist
            # Y_robot (lateral): si el marcador está a la derecha (tx>0),
            # queremos movernos hacia la derecha (o izquierda, según el signo).
            Y_mm = -tx * Slat
            # Z_robot (altura): si el marcador está arriba (ty<0),
            # queremos subir => Z_mm positivo, por eso el menos:
            Z_mm = -ty * Salt

            # Limitar rango para no salirnos
            X_mm = max(-MAX_VAL, min(MAX_VAL, X_mm))
            Y_mm = max(-MAX_VAL, min(MAX_VAL, Y_mm))
            Z_mm = max(-MAX_VAL, min(MAX_VAL, Z_mm))

            now = time.time()
            if now - last_send >= send_interval:
                msg = f"{X_mm:.1f},{Y_mm:.1f},{Z_mm:.1f}"
                sock.sendall(msg.encode("utf-8"))

                print("RAW (m):   tx={:.4f}, ty={:.4f}, tz={:.4f}, dist={:.4f}"
                      .format(tx, ty, tz, dist))
                print("ENVIADO a RAPID (mm): X={:.1f}, Y={:.1f}, Z={:.1f}\n"
                      .format(X_mm, Y_mm, Z_mm))

                last_send = now

            # Dibujo
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs,
                              rvecs[0][0], tvecs[0][0], 0.03)

            cv2.putText(frame,
                        f"tx:{tx:.3f} ty:{ty:.3f} tz:{tz:.3f} m",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)
            cv2.putText(frame,
                        f"dist:{dist:.3f} m (obj:0.20)",
                        (10, 55), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)

        else:
            cv2.putText(frame, "Sin marcador",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 0, 255), 2)

        cv2.imshow("Camara ArUco (control 20cm)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    sock.close()
    cap.release()
    cv2.destroyAllWindows()
    print("Socket cerrado, camara liberada.")