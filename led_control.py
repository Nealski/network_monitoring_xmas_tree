import board
import neopixel
from time import sleep
import sys


""" Code to run on a Raspberry Pi to control LEDs """


def flash_colour(colour_code, flashes=5, interval=0.5):
    global pixels
    # Flash the lights 5 times
    for i in range(0, flashes):
        pixels.fill((0, 0, 0))
        pixels.show()
        sleep(interval)
        pixels.fill(colour_code)
        pixels.show()
        sleep(interval)
    return


def solid_colour(colour_code):
    global pixels
    # Solid fill the colours
    pixels.fill(colour_code)
    pixels.show()
    return


if __name__ == "__main__":

    number_lights = 48

    pixels = neopixel.NeoPixel(board.D21, number_lights, brightness=0.5)

    grb_colours = {
        "GREEN": (255, 0, 0),
        "AMBER": (192, 255, 0),
        "RED": (0, 255, 0),
        "BLUE": (0, 0, 255)
    }

    try:
        colour = sys.argv[1].upper()
    except IndexError:
        # Default to blue as neutral colour
        colour = "BLUE"

    try:
        operation = sys.argv[2].upper()
    except IndexError:
        operation = "SOLID"

    if operation == "FLASH" and colour in grb_colours:
        flash_colour(grb_colours[colour])
    elif operation == "SOLID" and colour in grb_colours:
        solid_colour(grb_colours[colour])