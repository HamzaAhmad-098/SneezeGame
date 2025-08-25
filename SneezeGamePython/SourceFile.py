import pygame
import sys
import random
import collections
ROWS, COLS = 21, 21
FPS = 30
NAVY = (18, 32, 47)
YELLOW = (245, 200, 70)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (40, 44, 52)
GREEN = (50, 205, 50)
ORANGE = (255, 170, 30)
WIDTH, HEIGHT = 800, 800 
BAR_HEIGHT = 60
CELL_SIZE = 1 
MAZE_WIDTH = 1
MAZE_HEIGHT = 1
MAZE_X = 0
MAZE_Y = 0
def recalc_layout(width, height):
    global WIDTH, HEIGHT, BAR_HEIGHT, CELL_SIZE, MAZE_WIDTH, MAZE_HEIGHT, MAZE_X, MAZE_Y
    WIDTH, HEIGHT = width, height
    BAR_HEIGHT = max(int(HEIGHT * 0.08), 60)
    max_cell_w = WIDTH // COLS
    max_cell_h = (HEIGHT - BAR_HEIGHT) // ROWS
    CELL_SIZE = min(max_cell_w, max_cell_h)
    MAZE_WIDTH = CELL_SIZE * COLS
    MAZE_HEIGHT = CELL_SIZE * ROWS
    MAZE_X = (WIDTH - MAZE_WIDTH) // 2
    MAZE_Y = BAR_HEIGHT + (HEIGHT - BAR_HEIGHT - MAZE_HEIGHT) // 2
maze = []
dots = []
tissues = []
allergens = []
moving_allergens = []
doors = []
key_positions = []
player_keys_collected = set()
player_has_key = False
sneeze_bar = 0
sneeze_timer = 0
score = 0
level = 1
lost = False
game_completed = False
show_instructions = True
restart_button = False
level_won = False
level_time = 30 * FPS
main_path = []
MOVE_SPEED = 1
sneezing = False
SNEEZE_DURATION = 30
sneeze_countdown = 0
player_img = None
player_sneeze_img = None
tissue_img = None
germ_img = None
door_img = None
key_img = None
sneeze_sound = None
tissue_sound = None
allergen_sound = None
key_sound = None
door_sound = None
def load_sounds():
    global sneeze_sound, tissue_sound, allergen_sound, key_sound, door_sound
    sneeze_sound = pygame.mixer.Sound("audios/sneeze.wav")
    tissue_sound = pygame.mixer.Sound("audios/tissue.wav")
    allergen_sound = pygame.mixer.Sound("audios/allergen.wav")
    key_sound = pygame.mixer.Sound("audios/key.wav")
    door_sound = pygame.mixer.Sound("audios/door.wav")
    pygame.mixer.music.load("audios/background.mp3")
    pygame.mixer.music.play(-1)
def load_images():
    global player_img, player_sneeze_img, tissue_img, germ_img, door_img, key_img
    def scale_img(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, (CELL_SIZE, CELL_SIZE))
    player_img = scale_img("images/Professor_Munir.png")
    player_sneeze_img = scale_img("images/Professor_Munir_Sneeze.png")
    tissue_img = scale_img("images/Tissues.png")
    germ_img = scale_img("images/Germs.png")
    door_img = scale_img("images/door.png")
    key_img = scale_img("images/key.png")
def rescale_images():
    global player_img, player_sneeze_img, tissue_img, germ_img, door_img, key_img
    def scale_img(img):
        return pygame.transform.smoothscale(img, (CELL_SIZE, CELL_SIZE))
    if player_img:
        player_img = scale_img(player_img)
    if player_sneeze_img:
        player_sneeze_img = scale_img(player_sneeze_img)
    if tissue_img:
        tissue_img = scale_img(tissue_img)
    if germ_img:
        germ_img = scale_img(germ_img)
    if door_img:
        door_img = scale_img(door_img)
    if key_img:
        key_img = scale_img(key_img)
def generate_maze(complexity=1):
    maze = [[1 for _ in range(COLS)] for _ in range(ROWS)]
    start_x, start_y = 1, 1
    maze[start_y][start_x] = 0
    stack = [(start_x, start_y)]
    directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
    while stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 < nx < COLS - 1 and 0 < ny < ROWS - 1 and maze[ny][nx] == 1:
                neighbors.append((nx, ny, dx, dy))
        if neighbors:
            nx, ny, dx, dy = random.choice(neighbors)
            maze[y + dy // 2][x + dx // 2] = 0
            maze[ny][nx] = 0
            stack.append((nx, ny))
        else:
            stack.pop()
    maze[1][1] = 0
    return maze
def neighbors(x, y, maze):
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx, ny = x+dx, y+dy
        if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] == 0:
            yield (nx, ny)
class Player:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pos_x = grid_x * CELL_SIZE + CELL_SIZE / 2
        self.pos_y = grid_y * CELL_SIZE + CELL_SIZE / 2
        self.moving = False
        self.target_x = grid_x
        self.target_y = grid_y
    def start_move(self, dx, dy, maze):
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy
        if (new_x, new_y) in doors:
            idx = doors.index((new_x, new_y))
            if idx < len(key_positions) and key_positions[idx] in player_keys_collected:
                self.moving = True
                self.target_x = new_x
                self.target_y = new_y
            return
        if 0 <= new_x < COLS and 0 <= new_y < ROWS and maze[new_y][new_x] == 0:
            self.moving = True
            self.target_x = new_x
            self.target_y = new_y
    def update(self):
        if self.moving:
            target_px = self.target_x * CELL_SIZE + CELL_SIZE / 2
            target_py = self.target_y * CELL_SIZE + CELL_SIZE / 2
            dx = target_px - self.pos_x
            dy = target_py - self.pos_y
            dist = (dx**2 + dy**2) ** 0.5
            if dist < MOVE_SPEED:
                self.pos_x = target_px
                self.pos_y = target_py
                self.grid_x = self.target_x
                self.grid_y = self.target_y
                self.moving = False
            else:
                self.pos_x += MOVE_SPEED * dx / dist
                self.pos_y += MOVE_SPEED * dy / dist
class MovingAllergen:
    def __init__(self, x, y, move_delay=5):
        self.grid_x = x
        self.grid_y = y
        self.pos_x = x * CELL_SIZE + CELL_SIZE // 2
        self.pos_y = y * CELL_SIZE + CELL_SIZE // 2
        self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        self.speed = 1
        self.move_delay = move_delay
        self.move_counter = 0
    def move(self, maze):
        self.move_counter += 1
        if self.move_counter < self.move_delay:
            return
        self.move_counter = 0
        if random.random() < 0.10:
            self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        next_x = self.grid_x + self.direction[0]
        next_y = self.grid_y + self.direction[1]
        if (0 <= next_x < COLS and 0 <= next_y < ROWS and 
                maze[next_y][next_x] == 0 and (next_x, next_y) not in doors):
            self.grid_x = next_x
            self.grid_y = next_y
            self.pos_x = self.grid_x * CELL_SIZE + CELL_SIZE // 2
            self.pos_y = self.grid_y * CELL_SIZE + CELL_SIZE // 2
        else:
            self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
    def draw(self, screen):
        pos = (int(MAZE_X + self.grid_x * CELL_SIZE), int(MAZE_Y + self.grid_y * CELL_SIZE))
        screen.blit(germ_img, pos)
player = None
def bfs_path(maze, start, end, forbidden=None):
    if forbidden is None:
        forbidden = set()
    queue = collections.deque()
    queue.append((start, [start]))
    visited = set()
    visited.add(start)
    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == end:
            return path
        for nx, ny in neighbors(x, y, maze):
            if (nx, ny) not in visited and (nx, ny) not in forbidden:
                visited.add((nx, ny))
                queue.append(((nx,ny), path+[(nx,ny)]))
    return None
def find_branch_for_key(maze, main_path, forbidden=None):
    path_set = set(main_path)
    if forbidden:
        path_set = path_set.union(forbidden)
    branches = []
    for i, (x, y) in enumerate(main_path[1:-2], 1):
        for nx, ny in neighbors(x, y, maze):
            if (nx, ny) not in path_set:
                branch = [(nx, ny)]
                prev = (x, y)
                cur = (nx, ny)
                valid = True
                while True:
                    nexts = [n for n in neighbors(cur[0], cur[1], maze)
                             if n != prev and n not in path_set and n not in branch]
                    if not nexts:
                        break
                    if len(nexts) > 1:
                        valid = False
                        break
                    prev, cur = cur, nexts[0]
                    branch.append(cur)
                if valid and branch:
                    if all((pos not in main_path[1:] and pos != (COLS-2,ROWS-2)) for pos in branch[1:]):
                        branches.append(branch)
    return branches
def get_available_door_pos(main_path, doors, keys):
    for i in range(len(main_path) - 3, 1, -1):
        cell = main_path[i]
        if cell not in doors and cell not in keys and cell != (COLS-2, ROWS-2):
            return cell
    return None
def add_door_and_key(maze, main_path, doors, keys):
    forbidden = set(doors) | set(keys)
    branches = find_branch_for_key(maze, main_path, forbidden=forbidden)
    available_branches = [b for b in branches if b[-1] not in doors and b[-1] not in keys]
    if not available_branches:
        return False
    key_cell = random.choice(available_branches)[-1]
    door_cell = get_available_door_pos(main_path, doors, keys + [key_cell])
    if not door_cell:
        return False
    doors.append(door_cell)
    keys.append(key_cell)
    return True
def reset_game():
    global player, maze, dots, tissues, allergens, sneeze_bar, sneeze_timer, lost, game_completed
    global level_won, sneezing, sneeze_countdown, moving_allergens, doors, key_positions, player_keys_collected, player_has_key, level_time, main_path, MOVE_SPEED
    if level >= 7:
        level_time = 20 * FPS
    elif level >= 4:
        level_time = 25 * FPS
    else:
        level_time = 30 * FPS
    doors.clear()
    key_positions.clear()
    player_keys_collected.clear()
    player_has_key = False
    maze.clear()
    maze.extend(generate_maze(complexity=1))
    player = Player(1, 1)
    dots.clear()
    tissues.clear()
    allergens.clear()
    moving_allergens.clear()
    for y in range(ROWS):
        for x in range(COLS):
            if maze[y][x] == 0 and (x, y) != (1, 1):
                dots.append((x, y))
                rnd = random.random()
                if rnd < 0.08:
                    tissues.append((x, y))
                elif rnd < 0.13:
                    if level < 3:
                        allergens.append((x, y))
                    else:
                        move_delay = max(2, 5 - (level - 3))
                        moving_allergens.append(MovingAllergen(x, y, move_delay=move_delay))
    if level < 4:
        sneeze_bar = 0
        sneeze_timer = 0
        lost = False
        game_completed = False
        level_won = False
        sneezing = False
        sneeze_countdown = 0
        main_path = []
        MOVE_SPEED = CELL_SIZE / 5
        return
    start = (1, 1)
    end = (COLS - 2, ROWS - 2)
    main_path = bfs_path(maze, start, end)
    if not main_path:
        print("Maze path not found (should not happen with complexity=1). Exiting.")
        sys.exit(1)
    add_door_and_key(maze, main_path, doors, key_positions)
    sneeze_bar = 0
    sneeze_timer = 0
    lost = False
    game_completed = False
    level_won = False
    sneezing = False
    sneeze_countdown = 0
    MOVE_SPEED = CELL_SIZE / 5
def handle_sneeze():
    global sneezing, sneeze_countdown, sneeze_bar, main_path
    if level >= 7 and not sneezing and main_path:
        add_door_and_key(maze, main_path, doors, key_positions)
    sneezing = True
    sneeze_countdown = SNEEZE_DURATION
    sneeze_sound.play()
    sneeze_bar = 0
def draw_stage_selection(screen, font):
    screen.fill(NAVY)
    title = font.render("Select Stage:", True, YELLOW)
    option1 = font.render(">Press 1 for Easy", True, YELLOW)
    option2 = font.render(">Press 2 for Medium", True, YELLOW)
    option3 = font.render(">Press 3 for Hard", True, YELLOW)
    center_x = WIDTH // 2
    center_y = HEIGHT // 2
    gap = 50
    screen.blit(title, (center_x - title.get_width() // 2, center_y - gap*2))
    screen.blit(option1, (center_x - option1.get_width() // 2, center_y - gap//2))
    option2_x = center_x - option2.get_width() // 2 + 30
    screen.blit(option2, (option2_x, center_y + gap//2))
    screen.blit(option3, (center_x - option3.get_width() // 2, center_y + gap + gap//2))
def draw_level_selection(screen, font, stage):
    screen.fill(NAVY)
    if stage == 1:
        title = font.render("Easy: Select Level", True, YELLOW)
        option1 = font.render("Press 1 for Level 1", True, YELLOW)
        option2 = font.render("Press 2 for Level 2", True, YELLOW)
        option3 = font.render("Press 3 for Level 3", True, YELLOW)
    elif stage == 2:
        title = font.render("Medium: Select Level", True, YELLOW)
        option1 = font.render("Press 1 for Level 4", True, YELLOW)
        option2 = font.render("Press 2 for Level 5", True, YELLOW)
        option3 = font.render("Press 3 for Level 6", True, YELLOW)
    else:
        title = font.render("Hard: Select Level", True, YELLOW)
        option1 = font.render("Press 1 for Level 7", True, YELLOW)
        option2 = font.render("Press 2 for Level 8", True, YELLOW)
        option3 = font.render("Press 3 for Level 9", True, YELLOW)
    center_x = WIDTH // 2
    center_y = HEIGHT // 2
    gap = 50
    screen.blit(title, (center_x - title.get_width() // 2, center_y - gap*2))
    screen.blit(option1, (center_x - option1.get_width() // 2, center_y - gap//2))
    option2_x = center_x - option2.get_width() // 2 + 30
    screen.blit(option2, (option2_x, center_y + gap//2))
    screen.blit(option3, (center_x - option3.get_width() // 2, center_y + gap + gap//2))
def draw_maze(screen):
    for y in range(ROWS):
        for x in range(COLS):
            if maze[y][x] == 1:
                rect = pygame.Rect(MAZE_X + x * CELL_SIZE, MAZE_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, YELLOW, rect)
def draw_dots(screen):
    for (x, y) in dots:
        center = (MAZE_X + x * CELL_SIZE + CELL_SIZE // 2, MAZE_Y + y * CELL_SIZE + CELL_SIZE // 2)
        pygame.draw.circle(screen, WHITE, center, max(2, CELL_SIZE // 8))
def draw_tissues(screen):
    for (x, y) in tissues:
        pos = (MAZE_X + x * CELL_SIZE, MAZE_Y + y * CELL_SIZE)
        screen.blit(tissue_img, pos)
def draw_allergens(screen):
    for (x, y) in allergens:
        pos = (MAZE_X + x * CELL_SIZE, MAZE_Y + y * CELL_SIZE)
        screen.blit(germ_img, pos)
def draw_moving_allergens(screen):
    for m in moving_allergens:
        m.draw(screen)
def draw_player(screen):
    img = player_sneeze_img if sneezing else player_img
    pos = (int(MAZE_X + player.pos_x - CELL_SIZE / 2), int(MAZE_Y + player.pos_y - CELL_SIZE / 2))
    screen.blit(img, pos)
def draw_doors(screen):
    for (x, y) in doors:
        pos = (MAZE_X + x * CELL_SIZE, MAZE_Y + y * CELL_SIZE)
        screen.blit(door_img, pos)
def draw_key(screen):
    for k in key_positions:
        if k not in player_keys_collected:
            pos = (MAZE_X + k[0] * CELL_SIZE, MAZE_Y + k[1] * CELL_SIZE)
            screen.blit(key_img, pos)
def draw_exit_label(screen, font):
    label_font = pygame.font.SysFont("Arial", int(max(16, CELL_SIZE * 0.8)), bold=True)
    label = label_font.render("EXIT", True, GREEN)
    label_x = MAZE_X + (COLS - 2) * CELL_SIZE + (CELL_SIZE - label.get_width()) // 2
    label_y = MAZE_Y + (ROWS - 2) * CELL_SIZE + (CELL_SIZE - label.get_height()) // 2
    screen.blit(label, (label_x, label_y))
def draw_top_bar(screen, font, big_font):
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, BAR_HEIGHT))
    score_font = pygame.font.SysFont("Arial", int(BAR_HEIGHT*0.37), bold=True)
    score_label = score_font.render(f"Score: {score}  Level: {level}", True, ORANGE)
    bar_x = 20
    score_y = 4
    screen.blit(score_label, (bar_x, score_y))
    bar_y = BAR_HEIGHT // 2 + 8
    bar_width = max(120, int(WIDTH * 0.22))
    bar_height = max(16, int(BAR_HEIGHT * 0.32))
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), border_radius=8)
    fill_width = int(bar_width * min(sneeze_bar, 100) / 100)
    pygame.draw.rect(screen, RED, (bar_x, bar_y, fill_width, bar_height), border_radius=8)
    title_text = big_font.render("SNEEZE ATTACK", True, YELLOW)
    title_x = WIDTH // 2 - title_text.get_width() // 2
    title_y = BAR_HEIGHT // 2 - title_text.get_height() // 2 + 2
    screen.blit(title_text, (title_x, title_y))
    time_left = max(0, int((level_time - sneeze_timer) / FPS))
    timer_big_font = pygame.font.SysFont("Arial", int(BAR_HEIGHT*0.60), bold=True)
    timer_color = (70, 120, 255)
    timer_text = timer_big_font.render(f"Time: {time_left}s", True, timer_color)
    timer_x = WIDTH - timer_text.get_width() - 30
    timer_y = BAR_HEIGHT // 2 - timer_text.get_height() // 2
    screen.blit(timer_text, (timer_x, timer_y))
def draw_instructions(screen, font):
    win_w, win_h = int(WIDTH * 0.7), int(HEIGHT * 0.6)
    rect = pygame.Rect(WIDTH // 2 - win_w // 2, HEIGHT // 2 - win_h // 2, win_w, win_h)
    pygame.draw.rect(screen, YELLOW, rect, border_radius=30)
    left_margin = 40
    line_spacing = int(font.get_height() * 1.2)
    lines = [
        "SNEEZE ATTACK!",
        "By Maitha Ali & Shahenaz Al Shamsi",
        "1. Use Arrow Keys to move.",
        "2. Collect tissues to reduce sneeze bar.",
        "3. Avoid allergens which increase it.",
        "4. From level 3 : Germs will move!",
        "5. From level 4: Find key to open doors!",
        "6. From Level 7 : Avoid sneeze it will increase  Hurdles ",
        "7. Time line reduces 5 sec for every stage (complexity)",
        "8. Speed of Germs gradually increases as level up and up",
        "Press any key to continue..."
    ]
    line_surfs = [font.render(line, True, NAVY) for line in lines[:-1]]
    prompt_surf = font.render(lines[-1], True, RED)
    total_text_height = len(line_surfs) * line_spacing
    text_start_y = rect.top + (rect.height - total_text_height - prompt_surf.get_height() - 20) // 2
    for i, surf in enumerate(line_surfs):
        y = text_start_y + i * line_spacing
        screen.blit(surf, (rect.left + left_margin, y))
    prompt_y = rect.bottom - prompt_surf.get_height() - 20
    screen.blit(prompt_surf, (rect.centerx - prompt_surf.get_width() // 2, prompt_y))
def draw_level_win(screen, font):
    screen.fill(YELLOW)
    msg1 = font.render("You completed this level!", True, NAVY)
    msg2 = font.render("Press any key to continue to next level", True, NAVY)
    msg3 = font.render("Press 1 to quit", True, NAVY)
    screen.blit(msg1, (WIDTH // 2 - msg1.get_width() // 2, HEIGHT // 2 - 60))
    screen.blit(msg2, (WIDTH // 2 - msg2.get_width() // 2, HEIGHT // 2))
    screen.blit(msg3, (WIDTH // 2 - msg3.get_width() // 2, HEIGHT // 2 + 40))
def draw_win_screen(screen, font):
    screen.fill(YELLOW)
    msg = font.render("YOU'VE WON!", True, NAVY)
    score_msg = font.render(f"Your Score: {score}", True, NAVY)
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 40))
    screen.blit(score_msg, (WIDTH // 2 - score_msg.get_width() // 2, HEIGHT // 2 + 10))
def draw_game_over(screen, font):
    screen.fill(NAVY)
    msg1 = font.render("Game Over!", True, WHITE)
    msg2 = font.render("Click anywhere to Restart", True, RED)
    screen.blit(msg1, (WIDTH // 2 - msg1.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(msg2, (WIDTH // 2 - msg2.get_width() // 2, HEIGHT // 2 + 10))
def update_moving_allergens():
    for m in moving_allergens:
        m.move(maze)
def check_collisions():
    global sneeze_bar, player_has_key, player_keys_collected, doors, key_positions
    current_cell = (player.grid_x, player.grid_y)
    if current_cell in dots:
        dots.remove(current_cell)
    if current_cell in tissues:
        tissues.remove(current_cell)
        sneeze_bar = max(sneeze_bar - 20, 0)
        tissue_sound.play()
    if current_cell in allergens:
        allergens.remove(current_cell)
        sneeze_bar += 30
        allergen_sound.play()
    for idx, key_cell in enumerate(key_positions):
        if current_cell == key_cell and key_cell not in player_keys_collected:
            player_keys_collected.add(key_cell)
            if key_sound:
                key_sound.play()
    for m in moving_allergens:
        if (player.grid_x, player.grid_y) == (m.grid_x, m.grid_y):
            sneeze_bar += 40
            allergen_sound.play()
    for d in doors[:]:
        if d == current_cell and d in doors and len(player_keys_collected) > 0:
            idx = doors.index(d)
            if idx < len(key_positions) and key_positions[idx] in player_keys_collected:
                if door_sound:
                    door_sound.play()
                del doors[idx]
                del key_positions[idx]
def main():
    global show_instructions, lost, sneeze_timer, sneeze_bar
    global level, level_won, game_completed, restart_button, player, maze, sneezing, sneeze_countdown, score
    global player_img, player_sneeze_img, tissue_img, germ_img, door_img, key_img
    pygame.init()
    pygame.mixer.init()
    recalc_layout(WIDTH, HEIGHT)
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Sneeze Attack!")
    font = pygame.font.SysFont("Arial", 18)
    big_font = pygame.font.SysFont("Arial", 26, bold=True)
    large_font = pygame.font.SysFont("Arial", 36)
    clock = pygame.time.Clock()
    load_images()
    load_sounds()
    maze.extend(generate_maze())
    reset_game()
    running = True
    maze_completed_time = None
    stage_selected = False
    selected_stage = None
    level_selected = False
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.VIDEORESIZE:
                recalc_layout(event.w, event.h)
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                load_images() 
                reset_game()
            elif event.type == pygame.KEYDOWN:
                if show_instructions:
                    show_instructions = False
                    continue
                if not stage_selected:
                    if event.key == pygame.K_1:
                        selected_stage = 1
                        stage_selected = True
                    elif event.key == pygame.K_2:
                        selected_stage = 2
                        stage_selected = True
                    elif event.key == pygame.K_3:
                        selected_stage = 3
                        stage_selected = True
                    continue
                if stage_selected and not level_selected:
                    if event.key == pygame.K_1:
                        if selected_stage == 1:
                            level = 1
                        elif selected_stage == 2:
                            level = 4
                        else:
                            level = 7
                        level_selected = True
                        reset_game()
                        maze_completed_time = None
                        continue
                    elif event.key == pygame.K_2:
                        if selected_stage == 1:
                            level = 2
                        elif selected_stage == 2:
                            level = 5
                        else:
                            level = 8
                        level_selected = True
                        reset_game()
                        maze_completed_time = None
                        continue
                    elif event.key == pygame.K_3:
                        if selected_stage == 1:
                            level = 3
                        elif selected_stage == 2:
                            level = 6
                        else:
                            level = 9
                        level_selected = True
                        reset_game()
                        maze_completed_time = None
                        continue
                if level_won:
                    if level == 9:
                        game_completed = True
                        level_won = False
                    else:
                        level += 1
                        level_won = False
                        reset_game()
                        maze_completed_time = None
                    continue
                if lost:
                    reset_game()
                    lost = False
                    maze_completed_time = None
                    continue
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if lost or restart_button:
                    reset_game()
                    lost = False
                    restart_button = False
                    maze_completed_time = None
        if show_instructions:
            screen.fill(YELLOW)
            draw_instructions(screen, large_font)
            pygame.display.flip()
            continue
        if not stage_selected:
            draw_stage_selection(screen, large_font)
            pygame.display.flip()
            continue
        if stage_selected and not level_selected:
            draw_level_selection(screen, large_font, selected_stage)
            pygame.display.flip()
            continue
        if not sneezing and not player.moving:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.start_move(-1, 0, maze)
            elif keys[pygame.K_RIGHT]:
                player.start_move(1, 0, maze)
            elif keys[pygame.K_UP]:
                player.start_move(0, -1, maze)
            elif keys[pygame.K_DOWN]:
                player.start_move(0, 1, maze)
        player.update()
        if level_won:
            draw_level_win(screen, large_font)
            pygame.display.flip()
            continue
        if game_completed:
            draw_win_screen(screen, large_font)
            pygame.display.flip()
            continue
        if not maze_completed_time:
            sneeze_timer += 1

        if not sneezing:
            sneeze_bar += 0.1 + (0.1 * (level - 1))
        if sneeze_bar >= 100 and not sneezing:
            handle_sneeze()
        if sneezing:
            sneeze_countdown -= 1
            if sneeze_countdown <= 0:
                sneezing = False
                sneeze_bar = 0
        if level >= 3:
            update_moving_allergens()

        time_left = max(0, int((level_time - sneeze_timer) / FPS))
        if time_left <= 5 and (pygame.time.get_ticks() // 300) % 2 == 0:
            screen.fill(RED)
        else:
            screen.fill(NAVY)
        draw_top_bar(screen, font, big_font)
        draw_maze(screen)
        draw_dots(screen)
        draw_tissues(screen)
        if level < 3:
            draw_allergens(screen)
        draw_doors(screen)
        draw_key(screen)
        draw_moving_allergens(screen)
        draw_exit_label(screen, font)
        draw_player(screen)
        if not player.moving and not sneezing:
            check_collisions()
        if not maze_completed_time and (player.grid_x, player.grid_y) == (COLS - 2, ROWS - 2):
            if not doors:
                maze_completed_time = sneeze_timer
                base_time = level_time // FPS
                time_taken = maze_completed_time // FPS
                score += max(0, (base_time - time_taken) * 5) + (100 * level)
                level_won = True
                continue
        if sneeze_timer > level_time and not level_won:
            lost = True
        if lost:
            draw_game_over(screen, large_font)
            restart_button = True
        pygame.display.flip()
    pygame.quit()
    sys.exit()
if __name__ == "__main__":
    main()