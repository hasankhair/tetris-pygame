import pygame
import random
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Load background music
music_path = os.path.join(os.path.dirname(__file__), "tetris_theme.mp3")
pygame.mixer.music.load(music_path)
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

# Game constants
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
COLS = SCREEN_WIDTH // BLOCK_SIZE
ROWS = SCREEN_HEIGHT // BLOCK_SIZE

# Colors
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),   # I
    (0, 0, 255),     # J
    (255, 165, 0),   # L
    (255, 255, 0),   # O
    (0, 255, 0),     # S
    (128, 0, 128),   # T
    (255, 0, 0),     # Z
]

# Tetrimino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],        # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # Z
]

# Helper functions
def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked_positions.items():
        if y >= 0:
            grid[y][x] = color
    return grid

def valid_space(shape, offset, grid):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                new_x, new_y = off_x + x, off_y + y
                if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                    return False
                if new_y >= 0 and grid[new_y][new_x] != BLACK:
                    return False
    return True

def clear_rows(grid, locked):
    cleared = 0
    for i in range(len(grid)-1, -1, -1):
        if BLACK not in grid[i]:
            cleared += 1
            for j in range(len(grid[i])):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if cleared > 0:
        for key in sorted(locked.keys(), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < i:
                new_key = (x, y + cleared)
                locked[new_key] = locked.pop(key)
    return cleared

class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = random.choice(COLORS)
        self.rotation = 0

    def rotated(self):
        return rotate(self.shape)

# Draw functions
def draw_grid(surface, grid):
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            pygame.draw.rect(surface, grid[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    for x in range(COLS):
        pygame.draw.line(surface, GRAY, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, SCREEN_HEIGHT))
    for y in range(ROWS):
        pygame.draw.line(surface, GRAY, (0, y * BLOCK_SIZE), (SCREEN_WIDTH, y * BLOCK_SIZE))

def draw_text_center(surface, text, size, color):
    font = pygame.font.SysFont("comicsans", size)
    label = font.render(text, True, color)
    rect = label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    surface.blit(label, rect)

# Main game function
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris with Music")
    clock = pygame.time.Clock()

    locked_positions = {}
    grid = create_grid(locked_positions)

    current_piece = Piece(3, 0, random.choice(SHAPES))
    next_piece = Piece(3, 0, random.choice(SHAPES))
    fall_time = 0
    fall_speed = 0.5
    score = 0
    running = True

    while running:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece.shape, (current_piece.x, current_piece.y), grid):
                current_piece.y -= 1
                for y, row in enumerate(current_piece.shape):
                    for x, cell in enumerate(row):
                        if cell:
                            locked_positions[(current_piece.x + x, current_piece.y + y)] = current_piece.color
                current_piece = next_piece
                next_piece = Piece(3, 0, random.choice(SHAPES))
                if not valid_space(current_piece.shape, (current_piece.x, current_piece.y), grid):
                    draw_text_center(screen, "GAME OVER", 40, WHITE)
                    pygame.display.update()
                    pygame.time.delay(2000)
                    running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece.shape, (current_piece.x, current_piece.y), grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece.shape, (current_piece.x, current_piece.y), grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece.shape, (current_piece.x, current_piece.y), grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    rotated_shape = rotate(current_piece.shape)
                    if valid_space(rotated_shape, (current_piece.x, current_piece.y), grid):
                        current_piece.shape = rotated_shape

        for y, row in enumerate(current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    grid[current_piece.y + y][current_piece.x + x] = current_piece.color

        cleared = clear_rows(grid, locked_positions)
        if cleared > 0:
            score += cleared * 100

        screen.fill(BLACK)
        draw_grid(screen, grid)
        draw_text_center(screen, f"Score: {score}", 24, WHITE)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
