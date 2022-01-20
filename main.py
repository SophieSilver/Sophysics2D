import sophysics_engine
import defaults
import application
from typing import List
import pygame


class SophysicsApplication:
    def __init__(self):
        # initializing pygame
        pygame.init()

        # loading the config file
        self.__config = application.load_config("config.json")

        # initializing the display
        self.__display = application.get_display_from_config(self.__config["displayCfg"])
        pygame.display.set_caption(f"{self.__config['appName']} {self.__config['appVersion']}")

        # creating the environment
        self.__environment = application.get_environment_from_config(self.__display, self.__config["environmentCfg"])

        # getting a reference to the environment's event processor
        self.__event_processor: sophysics_engine.PygameEventProcessor = self.__environment.get_component(
            sophysics_engine.PygameEventProcessor)

        # creating the updater
        self.__environment_updater = defaults.DefaultUpdater(self.__environment)

        # the first argument is usually the name of the program
        # the second is the name of the file
        # I'll just grab the last one

        self.__run_game_loop()

    def __run_game_loop(self):
        is_running = True
        fps = self.__config["fps"]
        clock = pygame.time.Clock()

        while is_running:
            clock.tick(fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False
                    break

                self.__event_processor.process_event(event)

            self.__environment_updater.update()
            pygame.display.update()


if(__name__ == "__main__"):
    SophysicsApplication()
