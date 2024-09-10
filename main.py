from typing import List, Tuple
import pygame, sys
from widgets import TextField
from strfilter import str_to_numlist

FPS = 60
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700


class BinSearcher:
    BLOCK_SIZE = 50, 50

    def __init__(self, array: List[int], offset: Tuple[int, int, int]):
        """offset =x, y, right"""
        self.array = array
        self.low, self.mid = 0, 0
        self.high = max(0, len(array) - 1)
        self.text_blocks = []
        self.margin = offset

        self.low_pointer = pygame.Surface((20, 20))
        self.high_pointer = pygame.Surface((20, 20))

        self.init_text_blocks()

    def update_array(self, array: List[int]):
        self.array = array
        self.text_blocks.clear()
        self.init_text_blocks()

    def init_text_blocks(self):
        x, y, right = self.margin
        i = 0
        for elem in self.array:
            pos_x = x + (i + 1) * BinSearcher.BLOCK_SIZE[0]
            pos_y = y
            if pos_x > right - BinSearcher.BLOCK_SIZE[0] // 2:
                i = 0
                pos_x = x + (i + 1) * BinSearcher.BLOCK_SIZE[0]
                y += int(BinSearcher.BLOCK_SIZE[1] * 1.5)
                pos_y = y
            text_block = TextField(
                pos_x, pos_y, elem, size=BinSearcher.BLOCK_SIZE, readonly=True
            )
            self.text_blocks.append(text_block)
            i += 1

    def draw_blocks(self, display_surface: pygame.Surface):
        for block in self.text_blocks:
            block.draw(display_surface)


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
        allowed_keys = [
            pygame.K_COMMA,
            pygame.K_BACKSPACE,
            pygame.K_RETURN,
            pygame.K_LEFT,
            pygame.K_RIGHT,
            pygame.K_0,
            pygame.K_KP0,
            pygame.K_1,
            pygame.K_KP1,
            pygame.K_2,
            pygame.K_KP2,
            pygame.K_3,
            pygame.K_KP3,
            pygame.K_4,
            pygame.K_KP4,
            pygame.K_5,
            pygame.K_KP5,
            pygame.K_6,
            pygame.K_KP6,
            pygame.K_7,
            pygame.K_KP7,
            pygame.K_8,
            pygame.K_KP8,
            pygame.K_9,
            pygame.K_KP9,
        ]
        self.input_field.allow_keys(allowed_keys)

        init_array = [x for x in range(50)]
        self.bin_searcher = BinSearcher(init_array, self.input_field.get_offset())

    def perform_search(self):
        pass

    def handle_event(self):
        for event in pygame.event.get():
            self.input_field.handle_event(event)

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    values = str_to_numlist(self.input_field.get_value())
                    self.bin_searcher.update_array(values)

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.bin_searcher.draw_blocks(self.screen)
        self.input_field.draw(self.screen)
        pygame.display.flip()

    def update(self):
        self.input_field.update()

    def run(self):
        while True:
            self.handle_event()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = BinarySearchVisualization()
    game.run()
