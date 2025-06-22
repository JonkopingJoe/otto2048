import pygame
import random
import math
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

pygame.init()

FPS = 60

WIDTH, HEIGHT = 800, 800
ROWS = 4
COLS = 4

RECT_HEIGHT = HEIGHT // ROWS
RECT_WIDTH = WIDTH // COLS

OUTLINE_COLOR = (160, 160, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205, 192, 180)
FONT_COLOR = (119, 110, 101)

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")

FONT = pygame.font.Font(os.path.join(BASE_DIR, "NotoSansCJK-Regular.ttc"), 42)

MOVE_VEL = 20

BLOCK_INFO = {
    2:  {"text": "B三狼", "sound": "B三狼.mp3"},
    4:  {"text": "哇欧", "sound": "哇欧.mp3"},
    8:  {"text": "奥利安费", "sound": "奥利安费.mp3"}, 
    16: {"text": "all in", "sound": "all in.mp3"},
    32: {"text": "没有", "sound": "没有.mp3"},
    64: {"text": "憋追了", "sound": "憋追了.mp3"}, 
    128: {"text": "wcsndm", "sound": "wcsndm.mp3"}, 
    256: {"text": "woc 炫狗", "sound": "woc 炫狗.mp3"}, 
    512: {"text": "哈比下", "sound": "哈比下.mp3"}, 
    1024: {"text": "哈里路大旋风", "sound": "哈里路大旋风.mp3"}, 
    2048: {"text": "哇哦", "sound": "哇哦.mp3"},

}


def draw_grid(window):
    for row in range(1, ROWS):
        y = row * RECT_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)
    
    for col in range(1, COLS):
        x = col * RECT_WIDTH
        pygame.draw.line(window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)

    pygame.draw.rect(window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)

class Tile:
    COLORS = [
        (237, 229, 218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237,208, 115),
        (237, 204, 99),
        (236, 202, 80),
        (60, 58, 50),
        (30, 30, 30),
    ]

    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT

    def get_color(self):
        color_index = int(math.log2(self.value)) - 1
        color = self.COLORS[color_index]
        return color

    def draw(self, window):
        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))

        text_label = BLOCK_INFO.get(self.value, {}).get("text", str(self.value))
        text = FONT.render(text_label, 1, FONT_COLOR)

        window.blit(
            text, 
            (self.x + (RECT_WIDTH / 2 - text.get_width() / 2),
             self.y + (RECT_HEIGHT / 2 - text.get_height() / 2))
        )



    def set_pos(self, ceil = False):
        if ceil:
            self.row = math.ceil(self.y / RECT_HEIGHT)
            self.col = math.ceil(self.x / RECT_WIDTH)
        else:
            self.row = math.floor(self.y / RECT_HEIGHT)
            self.col = math.floor(self.x / RECT_WIDTH)

    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]

def draw(window, tiles):
    window.fill(BACKGROUND_COLOR)

    for tile in tiles.values():
        tile.draw(window)

    draw_grid(window)

    pygame.display.update()

def get_random_pos(tiles):
    row = None
    col = None
    while True:
        row = random.randrange(0, ROWS)
        col = random.randrange(0, COLS)

        if f"{row}{col}" not in tiles:
            break
    
    return row, col

def tiles_changed(before, after):
    if len(before) != len(after):
        return True
    for key in before:
        if key not in after:
            return True
        if before[key].value != after[key].value:
            return True
    return False

def move_tiles(window, tiles, clock, direction):
    updated = True
    blocks = set()
    merged_values = []

    # 记录原始状态以检测是否有变化
    tiles_before = {k: Tile(t.value, t.row, t.col) for k, t in tiles.items()}

    if direction == "left":
        sort_func = lambda x: x.col
        reverse = False
        delta = (-MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col-1}")
        merge_check = lambda tile, next_tile: tile.x > next_tile.x + MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.x > next_tile.x + RECT_WIDTH + MOVE_VEL
        )
        ceil = True
    elif direction == "right":
        sort_func = lambda x: x.col
        reverse = True
        delta = (MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == COLS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col+1}")
        merge_check = lambda tile, next_tile: tile.x < next_tile.x - MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.x + RECT_WIDTH + MOVE_VEL < next_tile.x
        )
        ceil = False
    elif direction == "up":
        sort_func = lambda x: x.row
        reverse = False
        delta = (0, -MOVE_VEL)
        boundary_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row-1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.y > next_tile.y + RECT_WIDTH + MOVE_VEL
        )
        ceil = True
    elif direction == "down":
        sort_func = lambda x: x.row
        reverse = True
        delta = (0, MOVE_VEL)
        boundary_check = lambda tile: tile.row == ROWS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row+1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.y + RECT_WIDTH + MOVE_VEL < next_tile.y
        )
        ceil = False

    while updated:
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_func, reverse=reverse)

        for i, tile in enumerate(sorted_tiles):
            if boundary_check(tile):
                continue

            next_tile = get_next_tile(tile)

            if not next_tile:
                tile.move(delta)
            elif tile.value == next_tile.value and tile not in blocks and next_tile not in blocks:
                if merge_check(tile, next_tile):
                    tile.move(delta)
                else:
                    next_tile.value *= 2
                    blocks.add(tile)
                    blocks.add(next_tile)
                    merged_values.append(next_tile.value)
                    sorted_tiles.pop(i)
                    i -= 1  # ✅ 新增行：合并后回退索引，防止跳过下一个 tile
            elif move_check(tile, next_tile):
                tile.move(delta)
            else:
                continue

            tile.set_pos(ceil)
            updated = True

        update_tiles(window, tiles, sorted_tiles)

    # 若无实际变化，不添加新方块也不播放音效
    if not tiles_changed(tiles_before, tiles):
        return "no change"

    new_value = end_move(tiles)
    if new_value:
        merged_values.append(new_value)

    if merged_values:
        max_val = max(merged_values)
        sound_path = os.path.join(BASE_DIR, "sound", BLOCK_INFO.get(max_val, {}).get("sound", ""))
        if os.path.isfile(sound_path):
            pygame.mixer.Sound(sound_path).play()


    return "continue"


def start_screen(window):
    background_path = os.path.join(BASE_DIR, "pics", "start_bg.jpg")  # 更换为你的背景图名
    bg_image = pygame.image.load(background_path)
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

    # 播放背景音乐
    music_path = os.path.join(BASE_DIR, "sound", "background.mp3")  # 更换为你的音乐文件名
    if os.path.isfile(music_path):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)  # 循环播放

    # 字体
    start_font = pygame.font.Font(os.path.join(BASE_DIR, "NotoSansCJK-Regular.ttc"), 50)
    text = start_font.render("按任意键开始游戏", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    waiting = True
    while waiting:
        window.blit(bg_image, (0, 0))
        window.blit(text, text_rect)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                pygame.mixer.music.stop()  # 停止背景音乐
                waiting = False

def game_over_screen(window):
    pygame.mixer.music.stop()

    # 模糊背景截图
    surface_copy = window.copy()
    surface_scaled = pygame.transform.smoothscale(surface_copy, (WIDTH // 5, HEIGHT // 5))
    blur_surface = pygame.transform.smoothscale(surface_scaled, (WIDTH, HEIGHT))
    window.blit(blur_surface, (0, 0))

    # 播放结束音效
    end_music_path = os.path.join(BASE_DIR, "sound", "gameover.mp3")  # 换为你的音频名
    if os.path.isfile(end_music_path):
        pygame.mixer.music.load(end_music_path)
        pygame.mixer.music.play(-1)

    font1 = pygame.font.Font(os.path.join(BASE_DIR, "NotoSansCJK-Regular.ttc"), 64)
    font2 = pygame.font.Font(os.path.join(BASE_DIR, "NotoSansCJK-Regular.ttc"), 32)

    text1 = font1.render("菜, 绿色", True, (0, 100, 0))
    text2 = font2.render("按空格键返回首页", True, (255, 255, 255))

    text1_rect = text1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    text2_rect = text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))

    waiting = True
    while waiting:
        window.blit(text1, text1_rect)
        window.blit(text2, text2_rect)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pygame.mixer.music.stop()
                waiting = False


def can_move(tiles):
    for row in range(ROWS):
        for col in range(COLS):
            key = f"{row}{col}"
            if key not in tiles:
                return True  # 空格可以生成

            current_val = tiles[key].value
            for d_row, d_col in [(-1,0),(1,0),(0,-1),(0,1)]:
                n_row, n_col = row + d_row, col + d_col
                n_key = f"{n_row}{n_col}"
                if 0 <= n_row < ROWS and 0 <= n_col < COLS and n_key in tiles:
                    if tiles[n_key].value == current_val:
                        return True  # 可合并
    return False


def end_move(tiles):
    if len(tiles) == 16:
        return None
    
    new_value = random.choice([2, 4])
    row, col = get_random_pos(tiles)
    tiles[f"{row}{col}"] = Tile(new_value, row, col)

    return new_value


def update_tiles(window, tiles, sorted_tiles):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile
    
    draw(window, tiles)

def generate_tiles():
    tiles = {}
    for _ in range(2):
        row, col = get_random_pos(tiles)
        tiles[f"{row}{col}"] = Tile(2, row, col)

    return tiles
    # tiles = {}
    # row = 0  # 放在第 0 行
    # for col in range(3):  # 放在第 0、1、2 列
    #     tiles[f"{row}{col}"] = Tile(16, row, col)  # 16 = "all in"
    # return tiles


def main(window):
    clock = pygame.time.Clock()
    run = True


    start_screen(window) #显示启动界面

    tiles = generate_tiles()

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_tiles(window, tiles, clock, "left")
                if event.key == pygame.K_RIGHT:
                    move_tiles(window, tiles, clock, "right")
                if event.key == pygame.K_UP:
                    move_tiles(window, tiles, clock, "up")
                if event.key == pygame.K_DOWN:
                    move_tiles(window, tiles, clock, "down")    

        draw(window, tiles)

        if not can_move(tiles):
            game_over_screen(window)
            tiles = generate_tiles()
            start_screen(window)
    
    pygame.quit()



if __name__ == "__main__":
    main(WINDOW)
