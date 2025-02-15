import time
import threading

class Clock:
    def __init__(self, tick_duration):
        self.tick_duration = tick_duration
        self.subscribers = []
        self.running = False
        self.thread = None

    def add_subscriber(self, callback):
        self.subscribers.append(callback)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._tick_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _tick_loop(self):
        while self.running:
            start_time = time.time()
            for callback in self.subscribers:
                callback()  # Notifie les abonnés
            elapsed = time.time() - start_time
            sleep_time = max(0, self.tick_duration - elapsed)
            time.sleep(sleep_time)