import asyncio
import signal
import time

import gmqtt

z_minimum = 0
z_maximum = 100

positions = [
    {
        'from': (0, 0, 0, 0),
        'to': (50, 60, 0, 30)
    }
]



def publish_coordinates(client, x_position, y_position, z_position, rotation):
    client.publish('pick_n_plaser/coordinates', (x_position, y_position, z_position, rotation))


async def run(broker_host: str):
    will_message = gmqtt.Message('pick_n_plaser/stop', True)
    client = gmqtt.Client("mom", will_message=will_message)

    await client.connect(broker_host)

    loop = asyncio.get_event_loop()
    stop_event = asyncio.Event()

    def stop(*args):
        stop_event.set()

    loop.add_signal_handler(signal.SIGINT, stop)
    loop.add_signal_handler(signal.SIGTERM, stop)

    client.publish('pick_n_plaser/stop', False)
    publish_coordinates(client, 0, 0, 0, 0)

    for pos in positions:
        move_item(client, pos['from'], pos['to'])

    await stop_event.wait()

    await client.disconnect(reason_code=4, reason_string="MoM was forced to quit")


def pick_up(client, x_position, y_position, rotation):
    publish_coordinates(client, x_position, y_position, z_minimum, rotation)
    publish_coordinates(client, x_position, y_position, z_minimum, (rotation + 90) % 180)
    publish_coordinates(client, x_position, y_position, z_maximum, (rotation + 90) % 180)


def release(client, x_position, y_position, rotation):
    publish_coordinates(client, x_position, y_position, z_minimum, rotation)
    publish_coordinates(client, x_position, y_position, z_minimum, (rotation + 90) % 180)
    publish_coordinates(client, x_position, y_position, z_maximum, 0)


def move_item(client, from_position, to_position):
    from_x, from_y, from_z, from_rotation = from_position
    to_x, to_y, to_z, to_rotation = to_position
    time.sleep(1)
    publish_coordinates(client, from_x, from_y, from_z, from_rotation)
    time.sleep(1)
    pick_up(client, from_x, from_y, from_rotation)
    time.sleep(1)
    publish_coordinates(client, to_x, to_y, z_maximum, to_rotation)
    time.sleep(1)
    release(client, to_x, to_y, to_rotation)
