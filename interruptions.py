import os
import sys
import argparse
from time import sleep
from script import watch_videos


def set_speed(network_interface, speed):
    os.system(
        'wondershaper -a {0} -d {1}'.format(network_interface, speed))


def restore(network_inteface):
    os.system('wondershaper -a {0} -c'.format(network_inteface))


def make_interruptions(network_inteface, speed, time):
    while True:
        try:
            print('Dropping down network speed to: {} Kbps'.format(speed))
            set_speed(network_inteface, speed)
            sleep(time)
            print('Restoring network speed...')
            restore(network_inteface)
            sleep(time)
        except KeyboardInterrupt:
            break
    print('Restoring network...')
    restore(network_inteface)
    print('Done!')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(allow_abbrev=True,
                                     description='Set speed network speed and interval of switching\nScript requires sudo and having wondershaper installed')

    parser.add_argument('-interface', type=str, help='Network interface name')
    parser.add_argument('-speed', type=int, help='Speed in Kbps')
    parser.add_argument('-time', type=int, help='Sleep interval')

    args = parser.parse_args()

    make_interruptions(args.interface, args.speed, args.time)
