
# import time module, Observer, FileSystemEventHandler
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging.config
from file_handler import FileHandler

logging.config.dictConfig(FileHandler('\\\\work\\tech\\Henry\\Programs\\Python\\bgt-automate\\create_product\\loggin_config.json').open_json())
# Create logger
logger = logging.getLogger(__name__)

  
  
class OnMyWatch:
    # Set the directory on watch
    watchDirectory = '\\\\172.16.2.44\\Websites\\intranet\\v_1.0\\temp\\add_to_bgtown\\'
  
    def __init__(self):
        self.observer = Observer()
  
    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDirectory, recursive = True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            logger.warning("Observer Stopped")
  
        self.observer.join()
  
  
class Handler(FileSystemEventHandler):
  
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
  
        elif event.event_type == 'created':
            # Event is created, you can process it now
            logger.info("Watchdog received created event - % s." % event.src_path)
        elif event.event_type == 'modified':
            # Event is modified, you can process it now
            logger.info("Watchdog received modified event - % s." % event.src_path)
              
  
if __name__ == '__main__':
    watch = OnMyWatch()
    watch.run()