import cv2
import socket
import struct
import os
import numpy as np
import threading
import queue
from utils.config import *
from models.model import HandProcessor


class VideoProcessor:
    def __init__(self, save_dir):
        self.save_dir = save_dir
        self.frame_queue = queue.Queue()
        self.stop_signal = threading.Event()
        self.hand_processor = HandProcessor()

    def receive_video(self, conn):
        while not self.stop_signal.is_set():
            frame_size_data = conn.recv(4)
            if not frame_size_data:
                break
            frame_size = struct.unpack("I", frame_size_data)[0]
            if frame_size == 0:
                self.stop_signal.set()
                break
            frame_data = b''
            while len(frame_data) < frame_size:
                packet = conn.recv(frame_size - len(frame_data))
                if not packet:
                    self.stop_signal.set()
                    break
                frame_data += packet
            if frame_data:
                frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
                self.frame_queue.put(frame)
        self.frame_queue.put(None)

    def process_and_send_video(self, conn):
        os.makedirs(self.save_dir, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(os.path.join(self.save_dir, 'server_output.mp4'), fourcc, 20.0, (WIDTH, HEIGHT))
        try:
            while not self.stop_signal.is_set():
                frame = self.frame_queue.get()
                if frame is None:
                    break
                processed_frame = self.hand_processor.process_frame(frame)
                if processed_frame is not None:
                    out.write(processed_frame)
                    _, processed_buffer = cv2.imencode('.jpg', processed_frame)
                    processed_data = processed_buffer.tobytes()
                    conn.sendall(struct.pack("I", len(processed_data)) + processed_data)
        finally:
            out.release()
            cv2.destroyAllWindows()

class VideoServer:
    def __init__(self, server_ip, server_port, save_dir):
        self.server_ip = server_ip
        self.server_port = server_port
        self.save_dir = save_dir
        self.stop_signal = threading.Event()
        self.video_processor = VideoProcessor(save_dir)

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.server_ip, self.server_port))
            server_socket.listen(1)
            print(f"Server listening on {self.server_ip}:{self.server_port}")

            conn, addr = server_socket.accept()
            print(f"Connection from {addr}")

            receive_thread = threading.Thread(target=self.video_processor.receive_video, args=(conn,))
            process_thread = threading.Thread(target=self.video_processor.process_and_send_video, args=(conn,))

            receive_thread.start()
            process_thread.start()

            receive_thread.join()
            process_thread.join()


if __name__ == "__main__":
    video_server = VideoServer(CLIENT_IP, CLIENT_PORT, SERVER_PROCESS_VIS)
    video_server.start_server()
