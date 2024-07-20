import cv2
import socket
import struct
import os
import numpy as np
import threading
from utils.get_log import GetLogger
from utils.config import *

class VideoClient:
    def __init__(self, server_ip, server_port, save_dir):
        self.server_ip = server_ip
        self.server_port = server_port
        self.save_dir = save_dir
        self.stop_signal = threading.Event()
        self.cap = cv2.VideoCapture(0)
        self.logger = GetLogger.get_logger()

        if not self.cap.isOpened():
            self.logger.error("Failed to open camera")
            raise ValueError("Failed to open camera")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, FPS)
        self.logger.info("VideoClient initialized with server IP: %s, port: %d, save directory: %s",
                         server_ip,
                         server_port, save_dir)

    def send_video(self, client_socket):
        self.logger.info("Started sending video")
        while not self.stop_signal.is_set():
            ret, frame = self.cap.read()
            if not ret:
                self.logger.warning("Failed to read frame from camera")
                break

            frame = cv2.resize(frame, (WIDTH, HEIGHT))
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
            frame_data = buffer.tobytes()

            try:
                client_socket.sendall(struct.pack("I", len(frame_data)) + frame_data)
            except BrokenPipeError:
                self.logger.error("BrokenPipeError encountered while sending frame data")
                break

            cv2.imshow("Client Camera", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                self.stop_signal.set()
                self.logger.info("ESC key pressed, stopping video send")
                break

        self.cap.release()
        client_socket.sendall(struct.pack("I", 0))
        self.logger.info("Video sending stopped and end signal sent")

    def receive_video(self, client_socket):
        self.logger.info("Started receiving video")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(os.path.join(self.save_dir, 'processed_output.mp4'), fourcc, 20.0, (WIDTH, HEIGHT))

        while not self.stop_signal.is_set():
            frame_size_data = client_socket.recv(4)
            if not frame_size_data:
                self.logger.warning("No frame size data received")
                break

            frame_size = struct.unpack("I", frame_size_data)[0]
            if frame_size == 0:
                self.stop_signal.set()
                self.logger.info("Received end signal from server")
                break

            frame_data = b''
            while len(frame_data) < frame_size:
                packet = client_socket.recv(frame_size - len(frame_data))
                if not packet:
                    self.stop_signal.set()
                    self.logger.warning("Incomplete frame data received")
                    break
                frame_data += packet

            if frame_data:
                processed_frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
                if processed_frame is not None:
                    out.write(processed_frame)
                    cv2.imshow("Processed Video", processed_frame)
                    if cv2.waitKey(1) & 0xFF == 27:
                        self.stop_signal.set()
                        self.logger.info("ESC key pressed, stopping video receive")
                        break

        out.release()
        client_socket.close()
        cv2.destroyAllWindows()
        self.logger.info("Video receiving stopped and resources released")

    def start_client(self):
        self.logger.info("Starting client")
        os.makedirs(self.save_dir, exist_ok=True)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.server_ip, self.server_port))
            self.logger.info("Connected to server at %s:%d", self.server_ip, self.server_port)

            send_thread = threading.Thread(target=self.send_video, args=(client_socket,))
            self.logger.info("Created thread for sending video")

            receive_thread = threading.Thread(target=self.receive_video, args=(client_socket,))
            self.logger.info("Created thread for receiving video")

            send_thread.start()
            receive_thread.start()
            self.logger.info("Threads started")

            send_thread.join()
            receive_thread.join()
            self.logger.info("Threads joined and client finished")


if __name__ == "__main__":
    print_log = GetLogger.get_logger()
    print_log.info("Initializing parameters...")
    client = VideoClient(SERVER_IP, SERVER_PORT, PROCESSED_FOLDER)
    client.start_client()
