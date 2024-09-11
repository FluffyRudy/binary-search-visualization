from typing import List, Tuple, Optional
import pygame, sys
from widgets import TextField, Button
from strfilter import str_to_numlist
from constants import MARKER_SIZE, SEARCH_FIELD_SIZE
from constants import ALLOWED_KEYS
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

        self.text_blocks = []
        self.margin = offset

        self.low_marker = load_image("./marker.png", (MARKER_SIZE))
        self.mid_marker = load_image("./mid.png", (MARKER_SIZE))
        self.high_marker = pygame.transform.rotate(self.low_marker.copy(), 180)

        self.init_text_blocks()

        self.prev_time = pygame.time.get_ticks()

        self.is_init_move = True

        font_size = 30
        self.font = pygame.font.Font(None, font_size)
        self.detail_surface = pygame.Surface(
            (SCREEN_WIDTH, int(SCREEN_HEIGHT * 0.2)), pygame.SRCALPHA
        )
        self.detail_rect = self.detail_surface.get_rect(bottomleft=(0, SCREEN_HEIGHT))
        self.font_height = self.font.size(f"{self.low}")[1] + font_size + 5

    def update_array(self, array: List[int]):
        self.array = array
        self.low = 0
        self.mid = 0
        self.high = max(0, len(self.array) - 1)
        self.is_init_move = True
        self.text_blocks.clear()
        self.init_text_blocks()
        self.mid_marker.set_alpha(255)

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
                x, y = block.marker_position
                display_surface.blit(self.low_marker, (x, block.rect.bottom))
            if block == self.text_blocks[self.mid]:
                display_surface.blit(self.mid_marker, block.marker_position)
            if block == self.text_blocks[self.high]:
                display_surface.blit(self.high_marker, block.marker_position)
            block.draw(display_surface)
        self.display_search_detail(display_surface)
        display_surface.blit(self.detail_surface, self.detail_rect.topleft)
        self.detail_surface.fill((0, 0, 0))

    def display_search_detail(self, display_surface: pygame.Surface):
        low_surface = self.font.render(f"low: {self.low}", True, (255, 255, 255))
        mid_surface = self.font.render(f"mid: {self.mid}", True, (255, 255, 255))
        high_surface = self.font.render(f"high: {self.high}", True, (255, 255, 255))

        low_position = (MARKER_SIZE[0] + 20, 0)
        mid_position = (MARKER_SIZE[0] + 20, self.font_height)
        high_position = (MARKER_SIZE[0] + 20, self.font_height * 2)

        font_render_surfaces = [
            (low_surface, low_position),
            (mid_surface, mid_position),
            (high_surface, high_position),
        ]

        self.detail_surface.blits(font_render_surfaces)
        self.detail_surface.blit(self.low_marker, (0, 0))
        self.detail_surface.blit(self.mid_marker, (0, MARKER_SIZE[1] + 20))
        self.detail_surface.blit(self.high_marker, (0, MARKER_SIZE[1] * 2 + 40))

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
            if self.array[self.mid] < self.search_value:
                self.low = self.mid + 1
            elif self.array[self.mid] > self.search_value:
                self.high = self.mid - 1


class BinarySearchVisualization:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Binary Search Visualization")

        self.screen = pygame.display.set_mode(size=(SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        screen_rect = self.screen.get_rect(topleft=(0, 0))
        centerx, top = screen_rect.midtop
        offset_y = 10
        self.input_field = TextField(
            centerx, top + offset_y, "", (int(screen_rect.width * 0.9), 100)
        )

        self.input_field.allow_keys(ALLOWED_KEYS)

        input_offset = self.input_field.get_offset()
        self.search_value_field = TextField(
            int(input_offset[2] - SEARCH_FIELD_SIZE[0] * 2),
            input_offset[1] - SEARCH_FIELD_SIZE[1],
            "",
            SEARCH_FIELD_SIZE,
            color=(100, 100, 100),
        )
        self.search_value_field.allow_keys(ALLOWED_KEYS)

        searcher_offset = (
            input_offset[0],
            self.search_value_field.rect.top + SEARCH_FIELD_SIZE[1] * 2 + 20,
            input_offset[2],
        )
        self.bin_searcher = BinSearcher([], searcher_offset, None)
        x, y = self.search_value_field.rect.topright
        self.search_button = Button(x + 30, y, self.handle_search)

    def perform_search(self):
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
        self.bin_searcher.set_value(int(search_value))
        values = sorted(str_to_numlist(self.input_field.get_value()))
        self.bin_searcher.update_array(values)

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.bin_searcher.draw_blocks(self.screen)
        self.search_value_field.draw(self.screen)
        self.search_button.draw(self.screen)
        self.input_field.draw(self.screen)
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
