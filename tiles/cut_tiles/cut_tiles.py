import os
import sys
from math import floor
from math import ceil

from PIL import Image

Image.MAX_IMAGE_PIXELS = 933120000

zoomed_width = {
    0: 256,
    1: 512,
    2: 1024,
    3: 2048,
    4: 4096,
    5: 8192,
    6: 16384
}

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
        "image": "",
        "zoom_level": 0,
        "root": package_root
    }
    for i in range(len(params)):
        if i < (len(params) - 1):
            if params[i] == "-i":
                config["image"] = params[i + 1]
            elif params[i] == "-z":
                config["zoom_level"] = params[i + 1]
            elif params[i] == "-r":
                config["root"] = params[i + 1]
    return config


def read_image(config):
    return Image.open(config["image"])


def resize_image(config):
    image = read_image(config)
    longest_side_length = zoomed_width[int(config["zoom_level"])]
    longest_side = 0
    if image.size[0] < image.size[1]:
        longest_side = 1
    if image.size[longest_side] < longest_side_length:
        raise MapTooSmallException("File is too small.")
    shorter_side_length = floor(image.size[1 - longest_side] * longest_side_length / image.size[longest_side])
    new_size = [0, 0]
    new_size[longest_side] = zoomed_width[int(config["zoom_level"])]
    new_size[1 - longest_side] = shorter_side_length
    image = image.resize(tuple(new_size))
    if shorter_side_length % 256 != 0:
        corrected_size = [0, 0]
        corrected_size[longest_side] = longest_side_length
        corrected_size[1 - longest_side] = 256 * (floor(shorter_side_length / 256) + 1)
        tile_corrected_image = Image.new("RGBA", tuple(corrected_size))
        tile_corrected_image.paste(image, (0, 0))
        image = tile_corrected_image
    return image


def slice_image(image, config):
    print("trying to slice the image")
    z_directory = os.path.join(config["map_root"], str(config["zoom_level"]))
    max_x = ceil(image.size[0] / 256)
    max_y = ceil(image.size[1] / 256)
    print("checking zoom directory: " + z_directory)
    if not os.path.exists(z_directory):
        os.makedirs(z_directory)
    print("checking x directories...")
    print("max_x = " + str(max_x))
    for i in range(max_x):
        if not os.path.exists(os.path.join(z_directory, str(i))):
            current_directory = os.path.join(z_directory, str(i))
            os.makedirs(current_directory)
            print(current_directory)
    print("slicing the tiles...")
    for i in range(max_x):
        for j in range(max_y):
            file_path = os.path.join(z_directory, str(i), str(j) + ".png")
            tile = image.crop((i * 256, j * 256, i * 256 + 255, j * 256 + 255))
            tile.save(file_path)
            print(file_path)


def get_map_root(config):
    map_directory = config["image"].split("/")[len(config["image"].split("/")) - 1].replace(".png", "")
    return os.path.join(config["root"], "dist", map_directory)


def process_image(config):
    config["map_root"] = get_map_root(config)
    if not os.path.exists(config["map_root"]):
        os.makedirs(config["map_root"], exist_ok=True)
    for zoom in zoomed_width.keys():
        config["zoom_level"] = zoom
        image = resize_image(config)
        print(os.path.join(config["map_root"], str(config["zoom_level"]) + ".png"))
        image.save(os.path.join(config["map_root"], str(config["zoom_level"]) + ".png"))
        slice_image(image, config)


def main(params):
    config = parse_params(params)
    if config["image"] == "":
        full_maps_root = os.path.join(package_root, "full_maps")
        images = os.listdir(full_maps_root)
        for image in images:
            print(image)
            if os.path.isfile(os.path.join(full_maps_root, image)) and image.endswith(".png"):
                config["image"] = os.path.join(full_maps_root, image)
                try:
                    process_image(config)
                except MapTooSmallException:
                    pass
    else:
        process_image(config)


if __name__ == "__main__":
    main(sys.argv[1:])
