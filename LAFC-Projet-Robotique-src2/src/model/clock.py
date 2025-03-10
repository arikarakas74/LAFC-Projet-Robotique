import time

class Clock:
    def __init__(self):
        self.subscribers = []
        self.last_time = time.time()
        self.running = True
        
    def add_subscriber(self, callback):
        self.subscribers.append(callback)
        
    def start(self):
        while self.running:
            current_time = time.time()
            delta_time = current_time - self.last_time
            self.last_time = current_time
            for callback in self.subscribers:
                callback(delta_time)
            time.sleep(0.001)  # Réduire la charge CPU

    def stop(self):
        self.running = False