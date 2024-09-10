from typing import Union, Tuple, Optional
import pygame
from cursor import Cursors, WidgetCursor
from cursor import ARROW, IBEAM


class TextField:
    def __init__(
        self, x: int, y: int, value: Union[str, int], size: Tuple[int, int], **kwargs
    ):
        self.mask_surface = pygame.Surface(size, pygame.SRCALPHA)

        self.size = size
        self.value = str(value)
        self.color = kwargs.get("color", (255, 255, 255))
        self.text_color = kwargs.get("textcolor", (255, 255, 255))
        self.rect = self.mask_surface.get_rect(midtop=(x, y))
        self.border_radius = kwargs.get("bradius", 3)
        self.border_width = kwargs.get("bwidth", 2)
        self.read_only = kwargs.get("readonly", False)

        self.is_focused = False

        self.font = pygame.font.Font(None, max(25, sum(size) // (10 * len(size))))

        self.text_surf = self.font.render(self.value, True, self.text_color)

        self.center = (self.rect.width // 2, self.rect.height // 2)
        self.text_center = self.text_surf.get_rect(center=self.center).topleft

        self.unrestricted_keys = []

        self.cursor = WidgetCursor((5, self.text_surf.get_height()))
        self.cursor_y = (self.rect.height - self.cursor.height) // 2

    def get_offset(self) -> Tuple[int, int, int]:
        "x, y, right"
        return (
            self.rect.left,
            self.rect.bottom + self.rect.height // 2,
            self.rect.right,
        )

    def allow_keys(self, keys: list[int]):
        for key in keys:
            self.unrestricted_keys.append(key)

    def change_color(self, new_color: Tuple[int, int, int]) -> None:
        if not isinstance(new_color, tuple) or len(new_color) != 3:
            raise TypeError("Expected tuple of integer for color in (r, g, b) format")
        self.color = new_color

    def add_char(self, value: Union[str, int]):
        if not isinstance(value, (str, int)):
            raise TypeError("Expected integer or string")
        self.value += str(value)

    def update_text_surf(self):
        self.text_surf = self.font.render(self.value, True, self.text_color)
        self.text_center = self.text_surf.get_rect(center=self.center).topleft

    def get_value(self) -> str:
        return self.value

    def is_hovered(self):
        x, y = pygame.mouse.get_pos()
        return self.rect.collidepoint(x, y)

    def handle_event(self, event: pygame.event.Event):
        if self.read_only:
            return
        self.handle_focus_blur_event(event)
        self.handle_key_input_event(event)

    def handle_focus_blur_event(self, event: pygame.event.Event):
        is_hovered = self.is_hovered()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if is_hovered:
                self.is_focused = True
            else:
                Cursors.change_cursor(ARROW)
                self.is_focused = False

        if self.is_focused or is_hovered:
            Cursors.change_cursor(IBEAM)
        else:
            Cursors.change_cursor(ARROW)

    def handle_key_input_event(self, event: pygame.event.Event):
        prev_value = self.value

        if self.is_focused and event.type == pygame.KEYDOWN:
            if len(self.unrestricted_keys) != 0:
                if event.key not in self.unrestricted_keys:
                    return

            if event.key == pygame.K_RETURN:
                self.is_focused = False

            elif event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]

            elif event.key == pygame.K_RIGHT:
                self.cursor.update_cursor_index(+1)

            elif event.key == pygame.K_LEFT:
                self.cursor.update_cursor_index(-1)

            keyname = pygame.key.name(event.key)

            if len(keyname) == 1:
                self.value += keyname
            elif (
                len(keyname) > 1 and keyname[1].isdigit()
            ):  # may cause potential problem in future
                self.value += keyname[1]
            if prev_value == self.value:
                return
            else:
                self.update_text_surf()

    def update(self):
        if self.read_only:
            return
        self.mask_surface.fill((0, 0, 0))
        self.cursor.update()
        if self.is_focused:
            """from input center to text right"""
            x = self.text_surf.get_width() // 2 + self.center[0]
            self.mask_surface.blit(self.cursor, (x, self.cursor_y))

    def draw(self, display_surface: pygame.Surface):
        self.mask_surface.blit(self.text_surf, self.text_center)
        display_surface.blit(self.mask_surface, self.rect.topleft)
        pygame.draw.rect(
            display_surface,
            self.color,
            self.rect,
            self.border_width,
            self.border_radius,
        )
