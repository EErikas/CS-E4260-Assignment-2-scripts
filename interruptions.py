import os
import threading
import time
from script import watch_videos

network_interface_name = "enp4s0"
speed = 1024


def interrupt(speed):
    os.system(
        'wondershaper -a {0} -d {1}'.format(network_interface_name, speed))


def restore():
    os.system('wondershaper -a {0} -c'.format(network_interface_name))


# video = threading.Thread(target=watch_videos)
# video.start()
while True:
    try:
        print('Dropping down network speed to: {}'.format(speed))
        interrupt(speed)
        time.sleep(10)
        print('Restoring network speed...')
        restore()
        time.sleep(10)
    except KeyboardInterrupt:
        print('Restoring network...')
        break

restore()
print('Done!')
