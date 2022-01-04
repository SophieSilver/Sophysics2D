from typing import Dict
import pygame


def get_display_from_config(config: Dict):
    size = tuple(config["size"])
    flags = config["flags"]
    depth = config["depth"]
    display_arg = config["display"]
    vsync = config["vsync"]

    display = pygame.display.set_mode(
        size, flags, depth, display_arg, vsync
    )

    return display
