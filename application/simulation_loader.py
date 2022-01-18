import pygame
import pygame_gui

from sophysics_engine import EnvironmentComponent, Camera, Event, TimeSettings, GUIManager, RigidBody
from defaults import Attraction
from typing import Optional, Dict, List, Union
from .celestial_body import get_celestial_body
from .reference_frame import ReferenceFrameManager
import math
import json


class SimulationLoadEvent(Event):
    def __init__(self, path):
        self.__path = path

    @property
    def path(self):
        return self.__path


class SimulationLoader(EnvironmentComponent):
    """
    Loads the simulation from a JSON file
    """
    def __init__(self, celestial_body_config: Dict, camera: Camera):
        self.__camera = camera
        self.__celestial_body_config = celestial_body_config
        self.__time_settings: Optional[TimeSettings] = None
        self.__gui_manager: Optional[GUIManager] = None
        self.__reference_frame_manager: Optional[ReferenceFrameManager] = None

        super().__init__()

    def setup(self):
        self.__time_settings = self.environment.get_component(TimeSettings)
        self.__gui_manager = self.environment.get_component(GUIManager)
        self.__reference_frame_manager = self.environment.get_component(ReferenceFrameManager)

        self.environment.event_system.add_listener(SimulationLoadEvent, self.__handle_simulation_load_event)

        super().setup()

    def __handle_simulation_load_event(self, event: SimulationLoadEvent):
        self.load_simulation_from_json(event.path)

    def load_simulation_from_json(self, path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                json_string = file.read()

            sim_dict = json.loads(json_string)
            self.__load_from_dict(sim_dict)

        except (ValueError, TypeError, KeyError) as e:
            self.__create_warning_window("loc.error", f"Could not load the file. {repr(e)}")

    def __load_from_dict(self, simulation_dict: Dict):
        self.__clear_current_simulation()

        origin_id: Optional[int] = simulation_dict.get("origin_id", None)
        time_settings_config: Optional[Dict] = simulation_dict.get("time_settings", None)
        camera_settings: Optional[Dict] = simulation_dict.get("camera_settings", None)

        if time_settings_config is not None:
            self.__set_time_settings(time_settings_config)

        if camera_settings is not None:
            self.__set_camera(camera_settings)

        bodies = simulation_dict["bodies"]

        if not isinstance(bodies, list):
            raise TypeError("'bodies' attribute must be a list")

        self.__load_bodies(bodies, origin_id)

    def __load_bodies(self, bodies: List, origin_id: Optional[int]):
        new_bodies = []
        new_origin = None

        for body in bodies:
            body_id = body.get("id", None)
            body_parameters = body["parameters"]
            self.__validate_body_parameters(body_parameters)

            body = get_celestial_body(
                config=self.__celestial_body_config,
                camera=self.__camera,
                **body_parameters
            )

            new_bodies.append(body)

            if origin_id is not None and body_id is not None and origin_id == body_id:
                rigidbody = body.get_component(RigidBody)
                new_origin = rigidbody

        for body in new_bodies:
            self.environment.attach_sim_object(body)

        self.__reference_frame_manager.origin_body = new_origin

    def __validate_body_parameters(self, parameters: Dict):
        if not isinstance(parameters["name"], str):
            raise TypeError("'name' parameter must be a string")

        if not self.__is_vector_compatible(parameters["initial_position"]):
            raise TypeError("'initial_position' parameter must be a vector-like")

        if not self.__is_vector_compatible(parameters["initial_velocity"]):
            raise TypeError("'initial_velocity' parameter must be a vector-like")

        if not self.__is_positive_number(parameters["mass"]):
            raise TypeError("'mass' parameter must be a positive number")

        if not self.__is_positive_number(parameters["radius"]):
            raise TypeError("'radius' parameter must be a positive number")

        if not isinstance(parameters["is_attractor"], bool):
            raise TypeError("'is_attractor' parameter must be a bool")

        if not isinstance(parameters["min_screen_radius"], int):
            raise TypeError("'min_screen_radius' must be an int")

        if not parameters["min_screen_radius"] >= 0:
            raise ValueError("'min_screen_radius' parameter can't be negative")

        if not isinstance(parameters["draw_layer"], int):
            raise TypeError("'draw_layer' parameter must be an int")

        if not 1 <= parameters["draw_layer"] <= 3:
            raise ValueError("the only allowed values for draw layer are 1, 2, or 3")

        # make sure it converts
        pygame.Color(parameters["color"])

    @staticmethod
    def __is_positive_number(number: Union[int, float]) -> bool:
        if not isinstance(number, (int, float)):
            return False

        if not math.isfinite(number):
            return False

        if number < 0:
            return False

        return True

    @staticmethod
    def __is_vector_compatible(value: List) -> bool:
        if not isinstance(value, list):
            return False

        if not len(value) == 2:
            return False

        if not (math.isfinite(value[0]) and math.isfinite(value[1])):
            return False

        return True

    def __clear_current_simulation(self):
        """
        Destroys all objects that have an Attraction component.
        """
        for sim_object in self.environment.sim_objects.copy():
            if not sim_object.has_component(Attraction):
                continue

            sim_object.destroy()

    def __set_time_settings(self, time_settings: Dict):
        dt = time_settings.get("dt", None)
        steps_per_frame = time_settings.get("steps_per_frame", None)
        paused = time_settings.get("paused", None)

        # if values are specified and are the correct types
        if dt is not None:
            if (isinstance(dt, int) or isinstance(dt, float)) and dt >= 0:
                self.__time_settings.dt = dt
            else:
                self.__create_warning_window("loc.warning", "loc.wrong_dt")

        if steps_per_frame is not None:
            if isinstance(steps_per_frame, int) and steps_per_frame >= 0:
                self.__time_settings.steps_per_frame = steps_per_frame
            else:
                self.__create_warning_window("loc.warning", "loc.wrong_steps_per_frame")

        if paused is not None:
            if isinstance(paused, bool):
                self.__time_settings.paused = paused
            else:
                self.__create_warning_window("loc.warning", "loc.wrong_paused")

    def __set_camera(self, camera_settings: Dict):
        units_per_pixel = camera_settings.get("units_per_pixel", None)
        position = camera_settings.get("position", None)

        if units_per_pixel is not None:
            if (isinstance(units_per_pixel, int) or isinstance(units_per_pixel, float)) and units_per_pixel > 0:
                self.__camera.units_per_pixel = units_per_pixel
            else:
                self.__create_warning_window("loc.warning", "loc.wrong_units_per_pixel")

        if position is not None:
            try:
                vector_position = pygame.Vector2(position)
                self.__camera.position = vector_position
            except ValueError:
                self.__create_warning_window("loc.warning", "loc.wrong_position")

    def __create_warning_window(self, title: str, message: str):
        # don't need to save it into a variable
        pygame_gui.windows.UIMessageWindow(
            rect=pygame.Rect(200, 100, 400, 200),
            html_message=message,
            manager=self.__gui_manager.ui_manager,
            window_title=title
        )

    def _on_destroy(self):
        self.environment.event_system.remove_listener(SimulationLoadEvent, self.__handle_simulation_load_event)
        self.__time_settings = None
        self.__gui_manager = None
        self.__camera = None
        self.__reference_frame_manager = None

        super()._on_destroy()
