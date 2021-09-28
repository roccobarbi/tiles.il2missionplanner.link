import os
import sys
from math import ceil

from PIL import Image

from cut_tiles import slice_image, zoomed_width


package_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MapTooSmallException(Exception):
    """Exception raised to stop execution when the zoom size exceeds the image size.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


def parse_params(params):
    config = {
        "image_directory": "",
        "zoom_level": 0,
        "root": package_root
    }
    for i in range(len(params)):
        if i < (len(params) - 1):
            if params[i] == "-i":
                config["image_directory"] = params[i + 1]
            elif params[i] == "-z":
                config["zoom_level"] = params[i + 1]
            elif params[i] == "-r":
                config["root"] = params[i + 1]
    return config


def get_map_root(config):
    return os.path.join(config["root"], "dist", config["image_directory"])


def process_image(config):
    config["map_root"] = get_map_root(config)
    if not os.path.exists(config["map_root"]):
        os.makedirs(config["map_root"], exist_ok=True)
    for zoom in zoomed_width.keys():
        config["zoom_level"] = zoom
        image = os.path.join(config["root"], config["image_directory"], str(config["zoom_level"]) + ".png")
        if os.path.exists(image):
            slice_image(Image.open(image), config)


def main(params):
    config = parse_params(params)
    if config["image_directory"] == "":
        pass
    else:
        process_image(config)


if __name__ == "__main__":
    main(sys.argv[1:])
