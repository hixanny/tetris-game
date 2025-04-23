import pygame
import random

# 初始化pygame
pygame.init()

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
SEMI_BLACK = (0, 0, 0, 180)  # 半透明黑色
LIGHT_GRAY = (200, 200, 200)  # 浅灰色，用于网格线

# 游戏设置
BLOCK_SIZE = 120  # 方块大小：120x120像素
GRID_WIDTH = 10   # 网格宽度：1200 / 120 = 10格
GRID_HEIGHT = 18  # 网格高度：2200 / 120 ≈ 18.33，调整为18格
SCREEN_WIDTH = 1200  # 手机分辨率宽度
SCREEN_HEIGHT = 2670  # 手机分辨率高度
GRID_OFFSET_X = 0  # 占满宽度
GRID_OFFSET_Y = 200  # 顶行之后
GAME_AREA_HEIGHT = BLOCK_SIZE * GRID_HEIGHT  # 游戏区域高度：2160像素

# 方块形状
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

# 游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris Mobile")

# 游戏状态
grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
current_piece = None
current_piece_x = 0
current_piece_y = 0
score = 0
lines = 0
level = 1
game_over = False

# 字体
font = pygame.font.SysFont(None, 60)

# 触摸按键区域（底部平均分布）
BUTTON_WIDTH = SCREEN_WIDTH // 4  # 每个按键宽度：300像素
BUTTON_HEIGHT = 200  # 按键高度
BUTTON_Y = GRID_OFFSET_Y + GAME_AREA_HEIGHT  # 按键起始Y坐标：2360
BUTTON_LEFT = pygame.Rect(0, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)  # 左移
BUTTON_RIGHT = pygame.Rect(BUTTON_WIDTH, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)  # 右移
BUTTON_DOWN = pygame.Rect(BUTTON_WIDTH * 2, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)  # 快速下落
BUTTON_ROTATE = pygame.Rect(BUTTON_WIDTH * 3, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)  # 旋转

# 弹窗按钮（上下排列）
POPUP_WIDTH = 400
POPUP_HEIGHT = 300
POPUP_X = (SCREEN_WIDTH - POPUP_WIDTH) // 2  # 居中
POPUP_Y = (SCREEN_HEIGHT - POPUP_HEIGHT) // 2  # 居中
BUTTON_RESTART = pygame.Rect(POPUP_X + (POPUP_WIDTH - 150) // 2, POPUP_Y + 120, 150, 80)  # RESTART按钮（第一行）
BUTTON_EXIT = pygame.Rect(POPUP_X + (POPUP_WIDTH - 150) // 2, POPUP_Y + 200, 150, 80)  # EXIT按钮（第二行）

def reset_game():
    global grid, current_piece, current_piece_x, current_piece_y, score, lines, level, game_over, current_piece_color
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    score = 0
    lines = 0
    level = 1
    game_over = False
    current_piece, current_piece_color = new_piece()
    current_piece_x = GRID_WIDTH // 2 - len(current_piece[0]) // 2
    current_piece_y = 0

def new_piece():
    shape_idx = random.randint(0, len(SHAPES) - 1)
    return SHAPES[shape_idx], SHAPE_COLORS[shape_idx]

def draw_grid():
    # 绘制游戏区域背景和网格线
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            pygame.draw.rect(screen, grid[y][x],
                            (GRID_OFFSET_X + x * BLOCK_SIZE, GRID_OFFSET_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    
    # 绘制游戏区域网格线
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(screen, LIGHT_GRAY, 
                        (GRID_OFFSET_X + x * BLOCK_SIZE, GRID_OFFSET_Y), 
                        (GRID_OFFSET_X + x * BLOCK_SIZE, GRID_OFFSET_Y + GAME_AREA_HEIGHT))
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(screen, LIGHT_GRAY, 
                        (GRID_OFFSET_X, GRID_OFFSET_Y + y * BLOCK_SIZE), 
                        (GRID_OFFSET_X + SCREEN_WIDTH, GRID_OFFSET_Y + y * BLOCK_SIZE))

def draw_piece(piece, color, x, y):
    # 绘制方块
    for py in range(len(piece)):
        for px in range(len(piece[py])):
            if piece[py][px]:
                pygame.draw.rect(screen, color,
                                (GRID_OFFSET_X + (x + px) * BLOCK_SIZE, GRID_OFFSET_Y + (y + py) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    
    # 绘制方块内部网格线
    for py in range(len(piece)):
        for px in range(len(piece[py])):
            if piece[py][px]:
                pygame.draw.rect(screen, LIGHT_GRAY,
                                (GRID_OFFSET_X + (x + px) * BLOCK_SIZE, GRID_OFFSET_Y + (y + py) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def check_collision(piece, x, y):
    for py in range(len(piece)):
        for px in range(len(piece[py])):
            if piece[py][px]:
                grid_x, grid_y = x + px, y + py
                if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y >= GRID_HEIGHT:
                    return True
                if grid_y >= 0 and grid[grid_y][grid_x] != BLACK:
                    return True
    return False

def merge_piece(piece, x, y, color):
    for py in range(len(piece)):
        for px in range(len(piece[py])):
            if piece[py][px]:
                grid_y = y + py
                if grid_y >= 0:
                    grid[grid_y][x + px] = color

def clear_lines():
    global lines, score, level
    new_grid = [row for row in grid if BLACK in row]
    cleared = GRID_HEIGHT - len(new_grid)
    lines += cleared
    score += cleared * 100
    level = lines // 10 + 1
    while len(new_grid) < GRID_HEIGHT:
        new_grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
    return new_grid

def rotate_piece(piece):
    return list(zip(*piece[::-1]))

def draw_buttons():
    pygame.draw.rect(screen, GRAY, BUTTON_LEFT)
    pygame.draw.rect(screen, GRAY, BUTTON_RIGHT)
    pygame.draw.rect(screen, GRAY, BUTTON_DOWN)
    pygame.draw.rect(screen, GRAY, BUTTON_ROTATE)

    # 按钮标签
    left_text = font.render("LEFT", True, WHITE)
    right_text = font.render("RIGHT", True, WHITE)
    down_text = font.render("DOWN", True, WHITE)
    rotate_text = font.render("ROTATE", True, WHITE)
    
    screen.blit(left_text, (BUTTON_LEFT.x + 50, BUTTON_LEFT.y + 70))
    screen.blit(right_text, (BUTTON_RIGHT.x + 50, BUTTON_RIGHT.y + 70))
    screen.blit(down_text, (BUTTON_DOWN.x + 50, BUTTON_DOWN.y + 70))
    screen.blit(rotate_text, (BUTTON_ROTATE.x + 20, BUTTON_ROTATE.y + 70))

def draw_popup():
    # 半透明背景
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(SEMI_BLACK)
    screen.blit(overlay, (0, 0))

    # 弹窗背景
    pygame.draw.rect(screen, BLACK, (POPUP_X, POPUP_Y, POPUP_WIDTH, POPUP_HEIGHT))
    pygame.draw.rect(screen, WHITE, (POPUP_X, POPUP_Y, POPUP_WIDTH, POPUP_HEIGHT), 2)  # 边框

    # 弹窗文字
    game_over_text = font.render("GAME OVER", True, WHITE)
    screen.blit(game_over_text, (POPUP_X + (POPUP_WIDTH - game_over_text.get_width()) // 2, POPUP_Y + 30))

    # 绘制按钮（上下排列）
    pygame.draw.rect(screen, GRAY, BUTTON_RESTART)
    pygame.draw.rect(screen, GRAY, BUTTON_EXIT)

    # 按钮文字
    restart_text = font.render("RESTART", True, WHITE)
    exit_text = font.render("EXIT", True, WHITE)
    screen.blit(restart_text, (BUTTON_RESTART.x + (BUTTON_RESTART.width - restart_text.get_width()) // 2, BUTTON_RESTART.y + 20))
    screen.blit(exit_text, (BUTTON_EXIT.x + (BUTTON_EXIT.width - exit_text.get_width()) // 2, BUTTON_EXIT.y + 20))

# 初始化第一个方块
current_piece, current_piece_color = new_piece()
current_piece_x = GRID_WIDTH // 2 - len(current_piece[0]) // 2
current_piece_y = 0

clock = pygame.time.Clock()
fall_time = 0
fall_speed = 500  # 毫秒

running = True
while running:
    fall_time += clock.get_rawtime()
    clock.tick()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if not game_over:
                # 游戏进行中的触摸按键
                if BUTTON_LEFT.collidepoint(pos):
                    if not check_collision(current_piece, current_piece_x - 1, current_piece_y):
                        current_piece_x -= 1
                elif BUTTON_RIGHT.collidepoint(pos):
                    if not check_collision(current_piece, current_piece_x + 1, current_piece_y):
                        current_piece_x += 1
                elif BUTTON_DOWN.collidepoint(pos):
                    while not check_collision(current_piece, current_piece_x, current_piece_y + 1):
                        current_piece_y += 1
                elif BUTTON_ROTATE.collidepoint(pos):
                    rotated = rotate_piece(current_piece)
                    if not check_collision(rotated, current_piece_x, current_piece_y):
                        current_piece = rotated
            else:
                # 游戏结束后的弹窗按钮
                if BUTTON_RESTART.collidepoint(pos):
                    reset_game()  # 重新开始
                elif BUTTON_EXIT.collidepoint(pos):
                    running = False  # 退出程序

    if fall_time >= fall_speed and not game_over:
        if not check_collision(current_piece, current_piece_x, current_piece_y + 1):
            current_piece_y += 1
        else:
            merge_piece(current_piece, current_piece_x, current_piece_y, current_piece_color)
            grid[:] = clear_lines()
            current_piece, current_piece_color = new_piece()
            current_piece_x = GRID_WIDTH // 2 - len(current_piece[0]) // 2
            current_piece_y = 0
            if check_collision(current_piece, current_piece_x, current_piece_y):
                game_over = True
        fall_time = 0

    screen.fill(BLACK)
    draw_grid()
    if not game_over:
        draw_piece(current_piece, current_piece_color, current_piece_x, current_piece_y)

    # 绘制触摸按键
    draw_buttons()

    # 显示分数、行数和等级（顶行）
    score_text = font.render(f"SCORE {score}", True, WHITE)
    lines_text = font.render(f"LINES {lines}", True, WHITE)
    level_text = font.render(f"LEVEL {level}", True, WHITE)
    screen.blit(score_text, (50, 50))
    screen.blit(lines_text, (450, 50))
    screen.blit(level_text, (850, 50))

    # 游戏结束时显示弹窗
    if game_over:
        draw_popup()

    pygame.display.flip()

pygame.quit()