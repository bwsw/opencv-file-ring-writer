import zmq
import cv2
from time import time
import os
import glob
import lz4.frame
import pickle


class SplitWriter:
    def __init__(self, split_size=30,
                 pub_address="tcp://127.0.0.1:5557",
                 directory='/tmp',
                 split_history=2,
                 split_prefix='split',
                 compressed=True,
                 fps=30):
        self.pub_address = pub_address
        self.split_size = split_size
        self.directory = directory
        self.split_history = split_history
        self.fps = fps
        self.compressed = compressed
        self.split_prefix = split_prefix

        self.zmq_context = zmq.Context()
        self.src = self.zmq_context.socket(zmq.SUB)
        self.src.connect(self.pub_address)
        self.src.setsockopt_string(zmq.SUBSCRIBE, "")

        self.current_split = 0
        self.new_split = 0
        self.writer = None
        self.last_frame_delay = 0
        self.remote_frameno = 0
        self.frameno = 0

    def _gen_split_name(self):
        return os.path.join(self.directory, self.split_prefix + '.%d.%d.avi' % (self.current_split, self.split_size))

    def _start_new_split(self, frame):
        self.current_split = int(time())
        self.new_split = self.current_split + self.split_size
        if self.writer:
            self.writer.release()
        self.writer = cv2.VideoWriter(self._gen_split_name(),
                                      cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                                      self.fps, (frame.shape[1], frame.shape[0]))
        print("++", self._gen_split_name(),
              "Last_Frame_Delay", self.last_frame_delay,
              "Frame_Delta", self.remote_frameno - self.frameno)
        self._clear_old_splits()

    def write(self):
        if self.compressed:
            frame = pickle.loads(lz4.frame.decompress(self.src.recv()))
        else:
            frame = self.src.recv_pyobj()
        meta = self.src.recv_pyobj()
        now = time()
        self.frameno += 1
        self.remote_frameno = meta['frameno']
        self.last_frame_delay = int((now - meta['ts']) * 1000)
        if now > self.new_split:
            self._start_new_split(frame)
        self.writer.write(frame)

    def _clear_old_splits(self):
        for f in glob.glob(os.path.join(self.directory, self.split_prefix + '.*.*.avi')):
            parts = f.split('.')
            ts = int(parts[-3])
            if ts < time() - self.split_size * self.split_history:
                print("--", f)
                os.unlink(f)

    def release(self):
        self.writer.release()
        self.src.close()
        self.zmq_context.destroy()


if __name__ == "__main__":
    w = SplitWriter(split_history=3, split_size=5)
    while True:
        w.write()


