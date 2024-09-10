from typing import Union, Tuple
import pygame


ARROW = pygame.SYSTEM_CURSOR_ARROW
IBEAM = pygame.SYSTEM_CURSOR_IBEAM


class Cursors:
    """
    A class to handle different types of cursors using the pygame library.

    Attributes:
        ARROW (int): The identifier for the standard arrow cursor.
        IBEAM (int): The identifier for the standard selection (text) cursor.
    """

    @classmethod
    def change_cursor(cls, cursor_type: Union[ARROW, IBEAM]):
        """
        Changes the cursor to the specified type.

        Args:
            cursor_type (CURSOR_TYPE): The type of cursor to set. Must be one of the predefined cursor types.
        """
        pygame.mouse.set_cursor(cursor_type)


class WidgetCursor(pygame.Surface):
    def __init__(self, size: Tuple[int, int], flag: int = 0):
        super().__init__(size, flag)
        self.fill((255, 255, 255))

        self.blinking_time = 500
        self.time_prev = pygame.time.get_ticks()
        self.is_visible = True
        self.index = 0

    def handle_blinking_event(self):
        time_current = pygame.time.get_ticks()

        if (time_current - self.time_prev) >= self.blinking_time:
            self.is_visible = not self.is_visible
            self.time_prev = time_current

        if self.is_visible:
            self.set_alpha(255)
        else:
            self.set_alpha(0)

    def force_visibility(self, value: bool):
        self.is_visible = value

    def update(self):
        self.handle_blinking_event()

    def update_cursor_index(self, factor: int):
        self.index += factor
