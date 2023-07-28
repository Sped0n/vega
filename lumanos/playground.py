from time import sleep, time

from luma.core.render import canvas


def hello_world(device):
    device.capabilities(width=128, height=64, rotate=0, mode="1")
    start = time()
    while True:
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            if time() - start > 3:
                draw.text((30, 20), "World Hello", fill="white")
            else:
                draw.text((30, 20), "Hello World", fill="white")
            if time() - start > 6:
                break
            sleep(0.02)
    device.clear()
