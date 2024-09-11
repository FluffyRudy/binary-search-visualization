from typing import List, Tuple, Optional
import pygame, sys
from widgets import TextField, Button
from strfilter import str_to_numlist
from constants import MARKER_SIZE, SEARCH_FIELD_SIZE
from constants import NUMERIC_KEYS, NON_NUMERIC_KEYS
import time

FPS = 60
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700


def load_image(path: str, size: Tuple[int, int]):
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(image, size)


class BinSearcher:
    BLOCK_SIZE = 50, 50

    def __init__(
        self,
        array: List[int],
        offset: Tuple[int, int, int],
        search_value: Optional[int] = None,
    ):
        """offset =x, y, right"""
        self.array = array
        self.low, self.mid = 0, 0
        self.high = max(0, len(array) - 1)
        self.search_value = search_value
        self.margin = offset

        self.text_blocks = []
        self.low_marker = load_image("./marker.png", MARKER_SIZE)
        self.mid_marker = load_image("./mid.png", MARKER_SIZE)
        self.high_marker = pygame.transform.rotate(self.low_marker.copy(), 180)

        self.is_init_move = True
        self.prev_time = pygame.time.get_ticks()

        self.font = pygame.font.Font(None, 30)
        self.detail_surface = pygame.Surface(
            (SCREEN_WIDTH, int(SCREEN_HEIGHT * 0.2)), pygame.SRCALPHA
        )
        self.detail_rect = self.detail_surface.get_rect(bottomleft=(0, SCREEN_HEIGHT))
        self.font_height = self.font.size(f"{self.low}")[1] + 30 + 5

        self.init_text_blocks()

    def update_array(self, array: List[int]):
        self.array = array
        self.low = 0
        self.mid = 0
        self.high = max(0, len(self.array) - 1)
        self.is_init_move = True
        self.mid_marker.set_alpha(255)
        self.init_text_blocks()

    def set_value(self, value: int):
        self.search_value = value

    def init_text_blocks(self):
        x, y, right = self.margin
        i = 0
        for elem in self.array:
            pos_x = x + (i + 1) * BinSearcher.BLOCK_SIZE[0]
            pos_y = y
            if pos_x > right - BinSearcher.BLOCK_SIZE[0] // 2:
                i = 0
                pos_x = x + (i + 1) * BinSearcher.BLOCK_SIZE[0]
                y += int(BinSearcher.BLOCK_SIZE[1] * 2)
                pos_y = y
            text_block = TextField(
                pos_x, pos_y, elem, size=BinSearcher.BLOCK_SIZE, readonly=True
            )
            self.text_blocks.append(text_block)
            i += 1

    def draw_blocks(self, display_surface: pygame.Surface):
        for block in self.text_blocks:
            if block == self.text_blocks[self.low]:
                display_surface.blit(
                    self.low_marker, (block.marker_position[0], block.rect.bottom)
                )
            if block == self.text_blocks[self.mid]:
                display_surface.blit(self.mid_marker, block.marker_position)
            if block == self.text_blocks[self.high]:
                display_surface.blit(self.high_marker, block.marker_position)

            block.draw(display_surface)
        self.display_search_detail()
        display_surface.blit(self.detail_surface, self.detail_rect.topleft)
        self.detail_surface.fill((0, 0, 0))

    def display_search_detail(self):
        details = [
            (f"low: {self.low}", 0),
            (f"mid: {self.mid}", self.font_height),
            (f"high: {self.high}", self.font_height * 2),
        ]
        for i, (label, position_y) in enumerate(details):
            text_surface = self.font.render(label, True, (255, 255, 255))
            self.detail_surface.blit(text_surface, (MARKER_SIZE[0] + 20, position_y))
            self.detail_surface.blit(
                [self.low_marker, self.mid_marker, self.high_marker][i], (0, position_y)
            )

    def init_search(self):
        if self.low > self.high:
            self.mid_marker.set_alpha(0)
            return
        if len(self.array) == 0 or self.search_value is None:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.prev_time >= 1500:
            self.prev_time = current_time

            if self.is_init_move:
                self.is_init_move = False
                return

            self.mid = self.low + (self.high - self.low) // 2

            if self.array[self.mid] == self.search_value:
                return
            elif self.array[self.mid] < self.search_value:
                self.low = self.mid + 1
            else:
                self.high = self.mid - 1


class BinarySearchVisualization:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Binary Search Visualization")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        screen_rect = self.screen.get_rect(topleft=(0, 0))
        centerx, top = screen_rect.midtop

        self.input_field = self.create_text_field(
            centerx, top + 10, screen_rect.width * 0.9, 100
        )
        self.search_value_field = self.create_text_field(
            int(self.input_field.get_offset()[2] - SEARCH_FIELD_SIZE[0] * 2),
            self.input_field.get_offset()[1] - SEARCH_FIELD_SIZE[1],
            *SEARCH_FIELD_SIZE,
            color=(100, 100, 100),
        )

        self.search_button = Button(
            self.search_value_field.rect.topright[0] + 30,
            self.search_value_field.rect.topright[1],
            self.handle_search,
        )

        self.bin_searcher = BinSearcher(
            [],
            (
                self.input_field.get_offset()[0],
                self.search_value_field.rect.top + SEARCH_FIELD_SIZE[1] * 2 + 20,
                self.input_field.get_offset()[2],
            ),
            None,
        )

        ALL_ALLOWED_KEYS = NUMERIC_KEYS + NON_NUMERIC_KEYS
        self.input_field.allow_keys(ALL_ALLOWED_KEYS.copy())

        ALL_ALLOWED_KEYS.remove(pygame.K_COMMA)
        self.search_value_field.allow_keys(ALL_ALLOWED_KEYS)

        self.error_message = ""
        self.show_error = False
        self.err_start_timer = 0
        self.font = pygame.font.Font(None, 25)

    def create_text_field(self, x, y, width, height, color=(255, 255, 255)):
        return TextField(x, y, "", (int(width), height), color=color)

    def perform_search(self):
        if self.bin_searcher.search_value is not None and self.bin_searcher.array:
            self.bin_searcher.init_search()

    def handle_event(self):
        for event in pygame.event.get():
            self.input_field.handle_event(event)
            self.search_value_field.handle_event(event)
            self.search_button.handle_event(event)

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def handle_search(self):
        search_value = self.search_value_field.get_value()
        if not search_value:
            return

        if search_value.find("-") == -1:
            pass
        elif search_value.index("-") != 0:
            self.show_error = True
            self.error_message = "Invalid search value"
            self.err_start_timer = pygame.time.get_ticks()
            return

        self.bin_searcher.set_value(int(search_value))
        values = sorted(str_to_numlist(self.input_field.get_value()))
        self.bin_searcher.update_array(values)

    def display_error(self):

        if self.show_error:
            error_message = self.font.render(self.error_message, True, (250, 0, 0))
            self.screen.blit(error_message, self.search_value_field.rect.bottomleft)

            current_time = pygame.time.get_ticks()
            if current_time - self.err_start_timer >= 2000:
                self.show_error = False
                self.err_start_timer = current_time

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.bin_searcher.draw_blocks(self.screen)
        self.search_value_field.draw(self.screen)
        self.search_button.draw(self.screen)
        self.input_field.draw(self.screen)
        self.display_error()
        pygame.display.flip()

    def update(self):
        self.input_field.update()
        self.search_value_field.update()
        self.perform_search()

    def run(self):
        while True:
            self.handle_event()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = BinarySearchVisualization()
    game.run()
