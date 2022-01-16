import pygame
import pygame_gui
import pymunk
import math

from sophysics_engine import GUIPanel, TimeSettings, UnpauseEvent
from .selection import BodyController, SelectionUpdateEvent, SelectedBodyPositionUpdateEvent
from .velocity_controller import SelectedBodyVelocityUpdateEvent
from .ui_elements import UIElement, TextBox, SwitchButtons
from .reference_frame import ReferenceFrameManager
from .body_creator import BodyCreator
from typing import Dict, Optional, List

# I hate this fucking code so much, it's so fucking shitty
# if I had more time, I'd fucking nuke it and do it the right way
# but here we are, and here means in hell


class SidePanel(GUIPanel):
    def __init__(self, config: Dict, body_creator: BodyCreator):
        self.__config = config
        self.__body_creator = body_creator
        self.__elements: List[UIElement] = []
        self.__selected_body: Optional[BodyController] = None

        super().__init__()

    @property
    def is_enabled(self) -> bool:
        return self.__panel.is_enabled

    @is_enabled.setter
    def is_enabled(self, value: bool):
        if value:
            self.__panel.enable()
            self.__panel.show()
        else:
            self.__panel.disable()
            self.__panel.hide()

    def _setup_ui(self):
        self.__time_settings: TimeSettings = self.environment.get_component(TimeSettings)
        self.__reference_frame_manager: ReferenceFrameManager = self.environment.get_component(ReferenceFrameManager)

        # create ui elements
        self.__create_panel()
        self.__create_element_containers()
        self.__fill_info_panel()
        self.__fill_creation_panel()

        # set initial condition
        self.__disable_info_panel()
        self.__disable_creation_panel()

        # subscribe to events
        self.environment.event_system.add_listener(SelectionUpdateEvent, self.__handle_selection_update_event)
        self.environment.event_system.add_listener(UnpauseEvent, self.__on_unpause)
        self.environment.event_system.add_listener(SelectedBodyPositionUpdateEvent,
                                                   self.__handle_position_update_event)
        self.environment.event_system.add_listener(SelectedBodyVelocityUpdateEvent,
                                                   self.__handle_velocity_update_event)

    # event listeners
    def __on_unpause(self, _: UnpauseEvent):
        for element in self.__elements:
            element.on_unpause()

    def __handle_velocity_update_event(self, _: SelectedBodyVelocityUpdateEvent):
        self.__update_velocity_textboxes()

    def __handle_selection_update_event(self, event: SelectionUpdateEvent):
        self.__selected_body = event.selected_body

        # if the current opened panel is the info panel or just an empty panel (i.e. not the creation panel)
        if self.__selected_body is None:
            self.__disable_info_panel()
            return

        if not self.__creation_panel.is_enabled:
            self.__enable_info_panel()

    def __handle_position_update_event(self, _: SelectedBodyPositionUpdateEvent):
        self.__update_position_textboxes()

    def __on_create_panel_close(self):
        self.__disable_creation_panel()

        if self.__selected_body is not None:
            self.__enable_info_panel()

    # creation panel
    def __fill_creation_panel(self):
        local_config = self.__config["creation_panel"]
        self.__close_create_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(local_config["close_button_rect"]),
            text="loc.close",
            manager=self._pygame_gui_manager,
            container=self.__creation_panel
        )
        self._ui_manager.add_callback(
            pygame_gui.UI_BUTTON_PRESSED,
            self.__close_create_button,
            self.__on_create_panel_close
        )

        # color
        self.__create_color_picker(local_config["color_picker"])

        # name
        self.__creation_name_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(local_config["name_label_rect"]),
            text="loc.name",
            manager=self._pygame_gui_manager,
            container=self.__creation_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@info_labels",
                object_id="#creation_name_label"
            )
        )
        name_textbox_wrapper = TextBox(
            rect=pygame.Rect(local_config["name_textbox_rect"]),
            gui_manager=self._ui_manager,
            container=self.__creation_panel,
            change_callback=self.__on_creation_name_textbox_changed,
        )
        self.__elements.append(name_textbox_wrapper)
        self.__creation_name_textbox = name_textbox_wrapper.element
        self.__creation_name_textbox.set_text(self.__body_creator.body_parameters["name"])

        # mass
        self.__creation_mass_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(local_config["mass_label_rect"]),
            manager=self._pygame_gui_manager,
            text="loc.mass",
            container=self.__creation_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@info_labels",
                object_id="#creation_mass_label"
            )
        )
        mass_textbox_wrapper = TextBox(
            rect=pygame.Rect(local_config["mass_textbox_rect"]),
            gui_manager=self._ui_manager,
            container=self.__creation_panel,
            allowed_characters=".-+0123456789Ee",
            finish_callback=self.__on_creation_mass_textbox_changed,
            refresh_callback=self.__refresh_creation_mass_textbox,
            pause_callback=self.__on_creation_mass_textbox_changed,
            unpause_callback=self.__on_creation_mass_textbox_changed
        )
        self.__elements.append(mass_textbox_wrapper)
        self.__creation_mass_textbox = mass_textbox_wrapper.element

        # radius
        self.__creation_radius_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(local_config["radius_label_rect"]),
            manager=self._pygame_gui_manager,
            text="loc.radius",
            container=self.__creation_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@info_labels",
                object_id="#creation_radius_label"
            )
        )
        radius_textbox_wrapper = TextBox(
            rect=pygame.Rect(local_config["radius_textbox_rect"]),
            gui_manager=self._ui_manager,
            container=self.__creation_panel,
            allowed_characters=".-+0123456789Ee",
            finish_callback=self.__on_creation_radius_textbox_changed,
            refresh_callback=self.__refresh_creation_radius_textbox,
            pause_callback=self.__on_creation_radius_textbox_changed,
            unpause_callback=self.__on_creation_radius_textbox_changed
        )
        self.__elements.append(radius_textbox_wrapper)
        self.__creation_radius_textbox = radius_textbox_wrapper.element

        # min screen radius
        self.__min_pixel_radius_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(local_config["min_pixel_radius_label_rect"]),
            manager=self._pygame_gui_manager,
            text="loc.min_pixel_radius",
            container=self.__creation_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@info_labels",
                object_id="#creation_min_pixel_radius_label"
            )
        )
        min_pixel_radius_textbox_wrapper = TextBox(
            rect=pygame.Rect(local_config["min_pixel_radius_textbox_rect"]),
            gui_manager=self._ui_manager,
            container=self.__creation_panel,
            allowed_characters="0123456789",
            finish_callback=self.__on_min_pixel_radius_textbox_changed,
            refresh_callback=self.__refresh_min_pixel_radius_textbox,
            pause_callback=self.__on_min_pixel_radius_textbox_changed,
            unpause_callback=self.__on_min_pixel_radius_textbox_changed
        )
        self.__elements.append(min_pixel_radius_textbox_wrapper)
        self.__min_pixel_radius_textbox = min_pixel_radius_textbox_wrapper.element

        # is attractor
        self.__is_attractor_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(local_config["is_attractor_label_rect"]),
            manager=self._pygame_gui_manager,
            text="loc.is_attractor",
            container=self.__creation_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@info_labels",
                object_id="#is_attractor_label"
            )
        )
        self.__is_attractor_switch = SwitchButtons(
            rect1=pygame.Rect(local_config["is_attractor_on_rect"]),
            rect2=pygame.Rect(local_config["is_attractor_off_rect"]),
            texts=("loc.yes", "loc.no"),
            gui_manager=self._ui_manager,
            container=self.__creation_panel,
            is_enabled=True,
            refresh_callback=self.__refresh_is_attractor_switch,
            state_change_callback=self.__on_is_attractor_state_change
        )
        self.__elements.append(self.__is_attractor_switch)

    def __on_is_attractor_state_change(self):
        self.__body_creator.body_parameters["is_attractor"] = self.__is_attractor_switch.is_enabled

    def __refresh_is_attractor_switch(self):
        self.__is_attractor_switch.is_enabled = self.__body_creator.body_parameters["is_attractor"]

    def __on_min_pixel_radius_textbox_changed(self):
        text = self.__min_pixel_radius_textbox.text
        try:
            value = int(text)
            self.__body_creator.body_parameters["min_screen_radius"] = value
            self.__body_creator.refresh_parameters()
        except ValueError:
            self.__refresh_min_pixel_radius_textbox()

    def __refresh_min_pixel_radius_textbox(self):
        self.__min_pixel_radius_textbox.set_text(str(self.__body_creator.body_parameters["min_screen_radius"]))

    def __on_creation_radius_textbox_changed(self):
        text = self.__creation_radius_textbox.text
        try:
            value = float(text)

            if value <= 0 or not math.isfinite(value):
                raise ValueError()

            self.__body_creator.body_parameters["radius"] = value
            self.__body_creator.refresh_parameters()
        except ValueError:
            self.__refresh_creation_radius_textbox()

    def __refresh_creation_radius_textbox(self):
        self.__creation_radius_textbox.set_text(str(self.__body_creator.body_parameters["radius"]))

    def __on_creation_mass_textbox_changed(self):
        text = self.__creation_mass_textbox.text
        try:
            value = float(text)

            if value <= 0 or not math.isfinite(value):
                raise ValueError()

            self.__body_creator.body_parameters["mass"] = value
        except ValueError:
            self.__refresh_creation_mass_textbox()

    def __refresh_creation_mass_textbox(self):
        self.__creation_mass_textbox.set_text(str(self.__body_creator.body_parameters["mass"]))

    def __on_creation_name_textbox_changed(self):
        text = self.__creation_name_textbox.text
        self.__body_creator.body_parameters["name"] = text

    # color picker
    def __create_color_picker(self, config: Dict):
        self.__color_picker_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(config["label_rect"]),
            text="loc.color",
            manager=self._pygame_gui_manager,
            container=self.__creation_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@info_labels",
                object_id="#color_label"
            )
        )
        # creating a color display surface
        self.__color_surface = pygame.Surface(tuple(config["image_rect"][2:]), pygame.SRCALPHA)
        self.__body_color = pygame.Color(config["initial_color"])
        self.__color_circle_radius = config["circle_radius"]

        self.__color_image = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(config["image_rect"]),
            image_surface=self.__color_surface,
            manager=self._pygame_gui_manager,
            container=self.__creation_panel
        )

        # red
        self.__r_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(config["r_label_rect"]),
            text="loc.r",
            manager=self._pygame_gui_manager,
            container=self.__creation_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@info_labels",
                object_id="#color_r"
            )
        )
        # slider
        self.__r_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(config["r_slider_rect"]),
            start_value=0,
            value_range=(0, 255),
            manager=self._pygame_gui_manager,
            container=self.__creation_panel
        )
        self._ui_manager.add_callback(
            pygame_gui.UI_HORIZONTAL_SLIDER_MOVED,
            self.__r_slider,
            self.__on_sliders_changed
        )
        # textbox
        r_textbox_wrapper = TextBox(
            rect=pygame.Rect(config["r_textbox_rect"]),
            gui_manager=self._ui_manager,
            container=self.__creation_panel,
            allowed_characters="0123456789",
            finish_callback=self.__on_color_textboxes_confirmed
        )
        self.__elements.append(r_textbox_wrapper)
        self.__r_textbox = r_textbox_wrapper.element

        # green
        self.__r_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(config["g_label_rect"]),
            text="loc.g",
            manager=self._pygame_gui_manager,
            container=self.__creation_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@info_labels",
                object_id="#color_g"
            )
        )
        # slider
        self.__g_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(config["g_slider_rect"]),
            start_value=0,
            value_range=(0, 255),
            manager=self._pygame_gui_manager,
            container=self.__creation_panel
        )
        self._ui_manager.add_callback(
            pygame_gui.UI_HORIZONTAL_SLIDER_MOVED,
            self.__g_slider,
            self.__on_sliders_changed
        )
        # textbox
        g_textbox_wrapper = TextBox(
            rect=pygame.Rect(config["g_textbox_rect"]),
            gui_manager=self._ui_manager,
            container=self.__creation_panel,
            allowed_characters="0123456789",
            finish_callback=self.__on_color_textboxes_confirmed
        )
        self.__elements.append(g_textbox_wrapper)
        self.__g_textbox = g_textbox_wrapper.element

        # blue
        self.__b_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(config["b_label_rect"]),
            text="loc.b",
            manager=self._pygame_gui_manager,
            container=self.__creation_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@info_labels",
                object_id="#color_b"
            )
        )
        # slider
        self.__b_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(config["b_slider_rect"]),
            start_value=0,
            value_range=(0, 255),
            manager=self._pygame_gui_manager,
            container=self.__creation_panel
        )
        self._ui_manager.add_callback(
            pygame_gui.UI_HORIZONTAL_SLIDER_MOVED,
            self.__b_slider,
            self.__on_sliders_changed
        )
        # textbox
        b_textbox_wrapper = TextBox(
            rect=pygame.Rect(config["b_textbox_rect"]),
            gui_manager=self._ui_manager,
            container=self.__creation_panel,
            allowed_characters="0123456789",
            finish_callback=self.__on_color_textboxes_confirmed
        )
        self.__elements.append(b_textbox_wrapper)
        self.__b_textbox = b_textbox_wrapper.element

        self.__refresh_color_picker()

    def __on_color_textboxes_confirmed(self):
        r_text = self.__r_textbox.text
        g_text = self.__g_textbox.text
        b_text = self.__b_textbox.text

        try:
            r_value = min(int(r_text), 255)
            self.__body_color.r = r_value

            g_value = min(int(g_text), 255)
            self.__body_color.g = g_value

            b_value = min(int(b_text), 255)
            self.__body_color.b = b_value
        except ValueError:
            pass

        self.__refresh_color_picker()

    def __on_sliders_changed(self):
        r_value = int(self.__r_slider.current_value)
        g_value = int(self.__g_slider.current_value)
        b_value = int(self.__b_slider.current_value)

        self.__body_color.r = r_value
        self.__body_color.g = g_value
        self.__body_color.b = b_value

        self.__refresh_color_picker()

    def __refresh_color_picker(self):
        # redraw the surface
        circle_pos = tuple(map(lambda x: x // 2, self.__color_surface.get_size()))
        pygame.draw.circle(self.__color_surface, self.__body_color, circle_pos, self.__color_circle_radius),
        # outline
        pygame.draw.circle(self.__color_surface, (255, 255, 255), circle_pos, self.__color_circle_radius, 2)
        self.__color_image.set_image(self.__color_surface)
        # update things
        # R
        self.__r_slider.set_current_value(self.__body_color.r)
        self.__r_textbox.set_text(str(self.__body_color.r))
        # G
        self.__g_slider.set_current_value(self.__body_color.g)
        self.__g_textbox.set_text(str(self.__body_color.g))
        # B
        self.__b_slider.set_current_value(self.__body_color.b)
        self.__b_textbox.set_text(str(self.__body_color.b))

        self.__body_creator.body_parameters["color"] = self.__body_color
        self.__body_creator.refresh_parameters()

    # info panel
    def __fill_info_panel(self):
        local_config = self.__config["info_panel"]

        # name
        self.__name_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(local_config["name_label_rect"]),
            text="loc.name",
            manager=self._pygame_gui_manager,
            container=self.__info_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@info_labels",
                object_id="#name_label"
            )
        )
        name_textbox_wrapper = TextBox(
            rect=pygame.Rect(local_config["name_textbox_rect"]),
            gui_manager=self._ui_manager,
            container=self.__info_panel,
            # this is the only place where we can modify the name (tag), so we will update the object's tag
            # every time the text box is changed
            change_callback=self.__on_name_textbox_changed,
            refresh_callback=self.__update_name_textbox
        )
        self.__elements.append(name_textbox_wrapper)
        self.__name_textbox = name_textbox_wrapper.element

        # mass
        self.__mass_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(local_config["mass_label_rect"]),
            text="loc.mass",
            manager=self._pygame_gui_manager,
            container=self.__info_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@info_labels",
                object_id="#mass_label"
            )
        )
        mass_textbox_wrapper = TextBox(
            rect=pygame.Rect(local_config["mass_textbox_rect"]),
            gui_manager=self._ui_manager,
            container=self.__info_panel,
            allowed_characters=".-+0123456789Ee",
            change_callback=self.__pause_simulation,
            finish_callback=self.__on_mass_textbox_confirmed,
            step_callback=self.__update_mass_textbox,
            unpause_callback=self.__on_mass_textbox_confirmed,
            refresh_callback=self.__update_mass_textbox
        )
        self.__elements.append(mass_textbox_wrapper)
        self.__mass_textbox = mass_textbox_wrapper.element

        # radius
        self.__radius_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(local_config["radius_label_rect"]),
            text="loc.radius",
            manager=self._pygame_gui_manager,
            container=self.__info_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@info_labels",
                object_id="#radius_label"
            )
        )
        radius_textbox_wrapper = TextBox(
            rect=pygame.Rect(local_config["radius_textbox_rect"]),
            gui_manager=self._ui_manager,
            container=self.__info_panel,
            allowed_characters=".-+0123456789Ee",
            change_callback=self.__pause_simulation,
            finish_callback=self.__on_radius_textbox_confirmed,
            unpause_callback=self.__on_radius_textbox_confirmed,
            refresh_callback=self.__update_radius_textbox
        )
        self.__elements.append(radius_textbox_wrapper)
        self.__radius_textbox = radius_textbox_wrapper.element

        # position
        self.__position_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(local_config["position_label_rect"]),
            text="loc.position",
            manager=self._pygame_gui_manager,
            container=self.__info_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@info_labels",
                object_id="#position_label"
            )
        )
        self.__position_x_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(local_config["position_x_label_rect"]),
            text="x:",
            manager=self._pygame_gui_manager,
            container=self.__info_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@info_labels",
                object_id="#position_x_label"
            )
        )
        position_x_textbox_wrapper = TextBox(
            rect=pygame.Rect(local_config["position_x_textbox_rect"]),
            gui_manager=self._ui_manager,
            container=self.__info_panel,
            allowed_characters=".-+0123456789Ee",
            finish_callback=self.__on_position_textbox_confirmed,
            step_callback=self.__update_position_textboxes,
            unpause_callback=self.__on_position_textbox_confirmed,
            refresh_callback=self.__update_position_textboxes
        )
        self.__elements.append(position_x_textbox_wrapper)
        self.__position_x_textbox = position_x_textbox_wrapper.element

        self.__position_y_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(local_config["position_y_label_rect"]),
            text="y:",
            manager=self._pygame_gui_manager,
            container=self.__info_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@info_labels",
                object_id="#position_y_label"
            )
        )
        position_y_textbox_wrapper = TextBox(
            rect=pygame.Rect(local_config["position_y_textbox_rect"]),
            gui_manager=self._ui_manager,
            container=self.__info_panel,
            allowed_characters=".-+0123456789Ee",
            change_callback=self.__pause_simulation,
            finish_callback=self.__on_position_textbox_confirmed,
            step_callback=self.__update_position_textboxes,
            unpause_callback=self.__on_position_textbox_confirmed,
            refresh_callback=self.__update_position_textboxes
        )
        self.__elements.append(position_y_textbox_wrapper)
        self.__position_y_textbox = position_y_textbox_wrapper.element

        # velocity
        self.__velocity_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(local_config["velocity_label_rect"]),
            text="loc.velocity",
            manager=self._pygame_gui_manager,
            container=self.__info_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@info_labels",
                object_id="#velocity_label"
            )
        )
        velocity_textbox_wrapper = TextBox(
            rect=pygame.Rect(local_config["velocity_textbox_rect"]),
            gui_manager=self._ui_manager,
            container=self.__info_panel,
            allowed_characters=".-+0123456789Ee",
            change_callback=self.__pause_simulation,
            finish_callback=self.__on_velocity_textbox_confirmed,
            step_callback=self.__update_velocity_textboxes,
            unpause_callback=self.__on_velocity_textbox_confirmed,
            refresh_callback=self.__update_velocity_textboxes
        )
        self.__elements.append(velocity_textbox_wrapper)
        self.__velocity_textbox = velocity_textbox_wrapper.element

        self.__velocity_x_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(local_config["velocity_x_label_rect"]),
            text="x:",
            manager=self._pygame_gui_manager,
            container=self.__info_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@info_labels",
                object_id="#velocity_x_label"
            )
        )
        self.__velocity_y_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(local_config["velocity_y_label_rect"]),
            text="y:",
            manager=self._pygame_gui_manager,
            container=self.__info_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@info_labels",
                object_id="#velocity_y_label"
            )
        )
        velocity_x_textbox_wrapper = TextBox(
            rect=pygame.Rect(local_config["velocity_x_textbox_rect"]),
            gui_manager=self._ui_manager,
            container=self.__info_panel,
            allowed_characters=".-+0123456789Ee",
            change_callback=self.__pause_simulation,
            finish_callback=self.__on_velocity_coords_confirmed,
            step_callback=self.__update_velocity_textboxes,
            unpause_callback=self.__on_velocity_coords_confirmed,
            refresh_callback=self.__update_velocity_textboxes
        )
        self.__elements.append(velocity_x_textbox_wrapper),
        self.__velocity_x_textbox = velocity_x_textbox_wrapper.element

        velocity_y_textbox_wrapper = TextBox(
            rect=pygame.Rect(local_config["velocity_y_textbox_rect"]),
            gui_manager=self._ui_manager,
            container=self.__info_panel,
            allowed_characters=".-+0123456789Ee",
            change_callback=self.__pause_simulation,
            finish_callback=self.__on_velocity_coords_confirmed,
            step_callback=self.__update_velocity_textboxes,
            unpause_callback=self.__on_velocity_coords_confirmed,
            refresh_callback=self.__update_velocity_textboxes
        )
        self.__elements.append(velocity_y_textbox_wrapper),
        self.__velocity_y_textbox = velocity_y_textbox_wrapper.element

        # draw trail
        self.__draw_trails_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(local_config["draw_trails_label"]),
            text="loc.draw_trail",
            manager=self._pygame_gui_manager,
            container=self.__info_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@info_labels",
                object_id="#draw_trail_label"
            )
        )
        self.__draw_trail_switch = SwitchButtons(
            rect1=pygame.Rect(local_config["enable_trails_rect"]),
            rect2=pygame.Rect(local_config["disable_trails_rect"]),
            texts=("loc.yes", "loc.no"),
            gui_manager=self._ui_manager,
            container=self.__info_panel,
            state_change_callback=self.__on_draw_trail_change,
            refresh_callback=self.__refresh_draw_trail_buttons
        )
        self.__elements.append(self.__draw_trail_switch)

        # use as origin
        self.__origin_switch_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(local_config["origin_label_rect"]),
            text="loc.use_as_origin",
            manager=self._pygame_gui_manager,
            container=self.__info_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@info_labels",
                object_id="#origin_label"
            )
        )
        self.__origin_switch = SwitchButtons(
            rect1=pygame.Rect(local_config["enable_origin_rect"]),
            rect2=pygame.Rect(local_config["disable_origin_rect"]),
            texts=("loc.yes", "loc.no"),
            gui_manager=self._ui_manager,
            container=self.__info_panel,
            state_change_callback=self.__on_origin_change,
            refresh_callback=self.__refresh_origin_switch
        )
        self.__elements.append(self.__origin_switch)

        # delete button
        self.__delete_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(local_config["delete_button_rect"]),
            text="loc.delete",
            manager=self._pygame_gui_manager,
            container=self.__info_panel
        )
        self._ui_manager.add_callback(
            pygame_gui.UI_BUTTON_PRESSED,
            self.__delete_button,
            self.__on_delete_button_pressed
        )

    def __on_delete_button_pressed(self):
        if self.__selected_body is None:
            return

        if self.__selected_body.rigidbody is self.__reference_frame_manager.origin_body:
            self.__reference_frame_manager.origin_body = None

        self.__selected_body.sim_object.destroy()

    def __on_origin_change(self):
        if self.__selected_body is None:
            return

        is_origin = self.__origin_switch.is_enabled

        if is_origin:
            self.__reference_frame_manager.origin_body = self.__selected_body.rigidbody
        else:
            self.__reference_frame_manager.origin_body = None

    def __refresh_origin_switch(self):
        if self.__selected_body is None:
            return

        selected_is_origin = self.__selected_body.rigidbody is self.__reference_frame_manager.origin_body

        self.__origin_switch.is_enabled = selected_is_origin

    def __on_draw_trail_change(self):
        if self.__selected_body is None:
            return

        is_enabled = self.__draw_trail_switch.is_enabled

        self.__selected_body.trail_renderer.reset_trail()
        self.__selected_body.trail_renderer.is_active = is_enabled

    def __refresh_draw_trail_buttons(self):
        if self.__selected_body is None:
            return

        self.__draw_trail_switch.is_enabled = self.__selected_body.trail_renderer.is_active

    def __on_velocity_coords_confirmed(self):
        if self.__selected_body is None:
            return

        text_x = self.__velocity_x_textbox.text
        text_y = self.__velocity_y_textbox.text
        rigidbody = self.__selected_body.rigidbody
        try:
            value_x = float(text_x)
            value_y = float(text_y)

            if not (math.isfinite(value_x) and math.isfinite(value_y)):
                raise ValueError()

            initial_vector = tuple(rigidbody.velocity)
            new_vector = (value_x, value_y)

            if new_vector == initial_vector:
                return

            rigidbody.velocity = (value_x, value_y)

        except ValueError:
            pass

        self.__update_velocity_textboxes()

    def __on_velocity_textbox_confirmed(self):
        if self.__selected_body is None:
            return

        text = self.__velocity_textbox.text
        rigidbody = self.__selected_body.rigidbody

        try:
            initial_vector = pygame.Vector2(rigidbody.velocity)
            scalar = float(text)

            if not math.isfinite(scalar):
                raise ValueError()

            direction = initial_vector.normalize()

            new_vector = direction * scalar
            if new_vector == initial_vector:
                return

            rigidbody.velocity = new_vector
        except ValueError:
            pass

        self.__update_velocity_textboxes()

    def __update_velocity_textboxes(self):
        if self.__selected_body is None:
            return

        velocity = self.__selected_body.rigidbody.velocity

        self.__velocity_textbox.set_text(str(velocity.length))
        self.__velocity_x_textbox.set_text(str(velocity.x))
        self.__velocity_y_textbox.set_text(str(velocity.y))

    def __on_position_textbox_confirmed(self):
        if self.__selected_body is None:
            return

        text_x = self.__position_x_textbox.text
        text_y = self.__position_y_textbox.text
        try:
            value_x = float(text_x)
            value_y = float(text_y)

            if not (math.isfinite(value_x) and math.isfinite(value_y)):
                raise ValueError()

            self.__selected_body.sim_object.transform.position = (value_x, value_y)

        except ValueError:
            self.__update_position_textboxes()

    def __update_position_textboxes(self):
        if self.__selected_body is None:
            return

        position = self.__selected_body.sim_object.transform.position
        if self.__position_x_textbox.text != str(position.x):
            self.__position_x_textbox.set_text(str(position.x))

        if self.__position_y_textbox.text != str(position.y):
            self.__position_y_textbox.set_text(str(position.y))

    def __on_radius_textbox_confirmed(self):
        if self.__selected_body is None:
            return

        text = self.__radius_textbox.text

        try:
            value = float(text)
            if value <= 0 or not math.isfinite(value):
                raise ValueError()

            self.__selected_body.radius = value
            circle: pymunk.Circle = self.__selected_body.rigidbody.shapes.copy().pop()  # type: ignore
            circle.unsafe_set_radius(value)
            for renderer in self.__selected_body.renderers:
                renderer.radius = value

        except ValueError:
            self.__update_radius_textbox()

    def __on_mass_textbox_confirmed(self):
        if self.__selected_body is None:
            return

        text = self.__mass_textbox.text

        try:
            value = float(text)
            if value <= 0 or not math.isfinite(value):
                raise ValueError()

            self.__selected_body.rigidbody.mass = value

            # so, changing the radius resets the mass for some obscure reason (it actually does make a little sense)
            # so, we're gonna change the mass of the shape as well
            circle: pymunk.Circle = self.__selected_body.rigidbody.shapes.copy().pop()  # type: ignore
            circle.mass = value
        except ValueError:
            pass

        self.__update_mass_textbox()

    def __update_mass_textbox(self):
        if self.__selected_body is None:
            return

        if str(self.__selected_body.rigidbody.mass) == self.__mass_textbox.text:
            return

        self.__mass_textbox.set_text(str(self.__selected_body.rigidbody.mass))

    def __update_radius_textbox(self):
        if self.__selected_body is None:
            return

        self.__radius_textbox.set_text(str(self.__selected_body.radius))

    # pause
    def __pause_simulation(self):
        self.__time_settings.paused = True

    def __update_name_textbox(self):
        if self.__selected_body is None:
            return

        self.__name_textbox.set_text(self.__selected_body.sim_object.tag)

    def __on_name_textbox_changed(self):
        """
        Changing the selected sim object's tag (name) to whatever is in the name textbox
        """
        if self.__selected_body is None:
            return

        self.__selected_body.sim_object.tag = self.__name_textbox.text

    def __create_element_containers(self):
        """
        Creates 2 invisible panels, that contain the elements of the InfoPanel.
        We do this because we need to display different sets of elements depending on
        the state of the panel
        """
        # panel for displaying info about the selected object
        self.__info_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, *self.__config["rect"][2:]),
            starting_layer_height=self.__config["starting_layer_height"],
            manager=self._pygame_gui_manager,
            container=self.__panel
        )
        self.__info_panel.visible = 0

        # a panel for creating new objects
        self.__creation_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, *self.__config["rect"][2:]),
            starting_layer_height=self.__config["starting_layer_height"],
            manager=self._pygame_gui_manager,
            container=self.__panel
        )
        self.__creation_panel.visible = 0

        # this thing kinda exists separately from the 2 panels, but idk where to put it
        # it switches to the create panel, so I'll plop it here
        self.__create_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.__config["create_button_rect"]),
            text="loc.create",
            manager=self._pygame_gui_manager,
            container=self.__panel
        )
        self._ui_manager.add_callback(
            pygame_gui.UI_BUTTON_PRESSED,
            self.__create_button,
            self.__enable_creation_panel
        )

    # enable / disable containers
    def __enable_info_panel(self):
        self.__info_panel.enable()
        self.__info_panel.show()
        # we want to show the elements that the panel has but not the panel itself
        self.__info_panel.visible = 0

        self.__disable_creation_panel()

        for element in self.__elements:
            element.refresh()

    def __disable_info_panel(self):
        self.__info_panel.disable()
        self.__info_panel.hide()

    def __enable_creation_panel(self):
        self.__creation_panel.enable()
        self.__creation_panel.show()
        self.__creation_panel.visible = 0

        self.__body_creator.is_enabled = True

        self.__create_button.disable()
        self.__create_button.hide()

        self.__disable_info_panel()

        for element in self.__elements:
            element.refresh()

    def __disable_creation_panel(self):
        self.__creation_panel.disable()
        self.__creation_panel.hide()

        self.__body_creator.is_enabled = False

        self.__create_button.enable()
        self.__create_button.show()

    # create panel
    def __create_panel(self):
        self.__panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(self.__config["rect"]),
            starting_layer_height=self.__config["starting_layer_height"],
            manager=self._pygame_gui_manager
        )

    def _update_ui(self):
        if not self.__time_settings.paused:
            for element in self.__elements:
                element.on_step()

    def _on_destroy(self):
        self.environment.event_system.remove_listener(SelectionUpdateEvent, self.__handle_selection_update_event)
        self.environment.event_system.remove_listener(UnpauseEvent, self.__on_unpause)
        self.environment.event_system.remove_listener(SelectedBodyPositionUpdateEvent,
                                                      self.__handle_position_update_event)
        self.environment.event_system.remove_listener(SelectedBodyVelocityUpdateEvent,
                                                      self.__handle_velocity_update_event)

        super()._on_destroy()
