add_library('sound')
ROWS, COLS = 21, 21
CELL_SIZE = 32
MAZE_X = 40
MAZE_Y = 80
NAVY    = color(18, 32, 47)
YELLOW  = color(245, 200, 70)
WHITE   = color(255, 255, 255)
RED     = color(255, 0, 0)
BLACK   = color(0, 0, 0)
GRAY    = color(40, 44, 52)
GREEN   = color(50, 205, 50)
ORANGE  = color(255, 170, 30)
GERM_COLOR = color(120, 200, 255)

STATE_INSTRUCTIONS = 0
STATE_STAGE_SELECT = 1
STATE_LEVEL_SELECT = 2
STATE_GAME = 3

state = STATE_INSTRUCTIONS
selected_stage = 0
selected_level = 0
level = 1

player_img = None
player_sneeze_img = None
tissue_img = None
germ_img = None
door_img = None
key_img = None

maze = []
dots = []
tissues = []
allergens = []
player = None
germs = []
moving_allergens = []

doors = []
keys = []
player_keys_collected = []
key_to_door = {}

sneeze_bar = 0
sneezing = False
sneeze_message_timer = 0

moving_up = False
moving_down = False
moving_left = False
moving_right = False

move_cooldown = 0
MOVE_DELAY = 2

timer = 0
timer_max = 0
timer_running = True
timer_gameover = False
game_won = False
game_over_reason = ""

score = 0
score_this_level = 0

GERM_START_COUNT = 2
GERM_MAX_COUNT = 6
GERM_BASE_SPEED = 40
GERM_MIN_SPEED = 10

sound_bg = None
sound_door = None
sound_tissue = None
sound_allergen = None
sound_sneeze = None

import random as pyrandom

class GermEnemy(object):
    def __init__(self, x, y, speed_frames):
        self.grid_x = x
        self.grid_y = y
        self.speed_frames = speed_frames
        self.move_timer = pyrandom.randint(0, speed_frames - 1)
        self.last_move_dir = None

    def update(self):
        self.move_timer += 1
        if self.move_timer >= self.speed_frames:
            self.move_timer = 0
            self.move_randomly()

    def move_randomly(self):
        possible = []
        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            nx, ny = self.grid_x + dx, self.grid_y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] == 0:
                possible.append((dx, dy))
        if possible:
            pyrandom.shuffle(possible)
            move_choice = possible[0]
            if self.last_move_dir and (-self.last_move_dir[0], -self.last_move_dir[1]) in possible and len(possible) > 1:
                for mv in possible:
                    if mv != (-self.last_move_dir[0], -self.last_move_dir[1]):
                        move_choice = mv
                        break
            self.grid_x += move_choice[0]
            self.grid_y += move_choice[1]
            self.last_move_dir = move_choice

    def display(self):
        x = MAZE_X + self.grid_x * CELL_SIZE
        y = MAZE_Y + self.grid_y * CELL_SIZE
        if germ_img is not None:
            image(germ_img, x, y, CELL_SIZE, CELL_SIZE)
        else:
            fill(GERM_COLOR)
            ellipse(x + CELL_SIZE/2, y + CELL_SIZE/2, CELL_SIZE*0.85, CELL_SIZE*0.85)

class MovingAllergen(object):
    def __init__(self, x, y, speed_frames):
        self.grid_x = x
        self.grid_y = y
        self.speed_frames = speed_frames
        self.move_timer = pyrandom.randint(0, speed_frames - 1)
        self.last_move_dir = None

    def update(self):
        self.move_timer += 1
        if self.move_timer >= self.speed_frames:
            self.move_timer = 0
            self.move_randomly()

    def move_randomly(self):
        possible = []
        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            nx, ny = self.grid_x + dx, self.grid_y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] == 0:
                possible.append((dx, dy))
        if possible:
            pyrandom.shuffle(possible)
            move_choice = possible[0]
            if self.last_move_dir and (-self.last_move_dir[0], -self.last_move_dir[1]) in possible and len(possible) > 1:
                for mv in possible:
                    if mv != (-self.last_move_dir[0], -self.last_move_dir[1]):
                        move_choice = mv
                        break
            self.grid_x += move_choice[0]
            self.grid_y += move_choice[1]
            self.last_move_dir = move_choice

    def display(self):
        x = MAZE_X + self.grid_x * CELL_SIZE
        y = MAZE_Y + self.grid_y * CELL_SIZE
        if germ_img:
            image(germ_img, x, y, CELL_SIZE, CELL_SIZE)
        else:
            fill(RED)
            ellipse(x + CELL_SIZE/2, y + CELL_SIZE/2, 12, 12)

def spawn_germs():
    global germs
    germs = []
    if level >= 2:
        count = min(GERM_START_COUNT + level//2, GERM_MAX_COUNT)
        speed = max(GERM_BASE_SPEED - (level-2)*6, GERM_MIN_SPEED)
        used = set()
        for _ in range(count):
            tries = 0
            while tries < 100:
                x = pyrandom.randint(1, COLS-2)
                y = pyrandom.randint(1, ROWS-2)
                if maze[y][x]==0 and (abs(x-1)+abs(y-1)) > 5 and (abs(x-(COLS-2))+abs(y-(ROWS-2))) > 5 and (x,y) not in used:
                    germs.append(GermEnemy(x, y, speed))
                    used.add((x, y))
                    break
                tries += 1

def setup():
    global player_img, tissue_img, germ_img, player_sneeze_img, door_img, key_img
    global sound_bg, sound_door, sound_tissue, sound_allergen, sound_sneeze
    size(COLS * CELL_SIZE + 2 * MAZE_X, ROWS * CELL_SIZE + 2 * MAZE_Y)
    frameRate(30)
    try:
        player_img = loadImage("Professor_Munir.png")
    except:
        player_img = None
    try:
        player_sneeze_img = loadImage("Professor_Munir_Sneeze.png")
    except:
        player_sneeze_img = None
    try:
        tissue_img = loadImage("Tissues.png")
    except:
        tissue_img = None
    try:
        germ_img = loadImage("Germs.png")
    except:
        germ_img = None
    try:
        door_img = loadImage("door.png")
    except:
        door_img = None
    try:
        key_img = loadImage("key.png")
    except:
        key_img = None

    try:
        from processing.sound import SoundFile
        sound_bg = SoundFile(this, "background.mp3")
        sound_door = SoundFile(this, "door_opened.wav")
        sound_tissue = SoundFile(this, "tissue.wav")
        sound_allergen = SoundFile(this, "allergen.wav")
        sound_sneeze = SoundFile(this, "sneeze.wav")
        if sound_bg:
            sound_bg.loop()
    except Exception as e:
        print("Sound error:", e)

def bfs_path(maze, sx, sy, ex, ey):
    visited = [[False for _ in range(COLS)] for _ in range(ROWS)]
    parent = {}
    q = []
    q.append((sx, sy))
    visited[sy][sx] = True
    while q:
        cx, cy = q.pop(0)
        if (cx, cy) == (ex, ey):
            path = []
            node = (ex, ey)
            while node != (sx, sy):
                path.append(node)
                node = parent[node]
            path.append((sx, sy))
            path.reverse()
            return path
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = cx+dx, cy+dy
            if 0<=nx<COLS and 0<=ny<ROWS and maze[ny][nx]==0 and not visited[ny][nx]:
                visited[ny][nx]=True
                parent[(nx, ny)] = (cx, cy)
                q.append((nx, ny))
    return None

def find_branches(maze, path):
    path_set = set(path)
    branches = []
    for i in range(1, len(path)-2):
        x, y = path[i]
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = x+dx, y+dy
            if 0<=nx<COLS and 0<=ny<ROWS and maze[ny][nx]==0 and (nx,ny) not in path_set:
                branch = [(nx, ny)]
                prev = (x, y)
                cur = (nx, ny)
                valid = True
                while True:
                    nexts = []
                    for ddx, ddy in [(0,1),(0,-1),(1,0),(-1,0)]:
                        nnx, nny = cur[0]+ddx, cur[1]+ddy
                        if 0<=nnx<COLS and 0<=nny<ROWS and maze[nny][nnx]==0 and (nnx,nny)!=prev and (nnx,nny) not in path_set and (nnx,nny) not in branch:
                            nexts.append((nnx, nny))
                    if not nexts:
                        break
                    if len(nexts) > 1:
                        valid = False
                        break
                    prev, cur = cur, nexts[0]
                    branch.append(cur)
                if valid and len(branch)>0:
                    branches.append(branch)
    return branches

def place_door_and_key_1to1():
    global doors, keys, key_to_door
    path = bfs_path(maze, 1, 1, COLS-2, ROWS-2)
    if not path:
        return
    branches = find_branches(maze, path)
    if not branches:
        return
    branch = branches[int(random(len(branches)))]
    keyCell = branch[-1]
    doorIdx = len(path)-3
    while doorIdx > 1 and (path[doorIdx] in doors or path[doorIdx] in keys):
        doorIdx -= 1
    doorCell = path[doorIdx]
    doors.append(doorCell)
    keys.append(keyCell)
    key_to_door[keyCell] = doorCell

def handle_sneeze_special():
    if level >= 7:
        place_door_and_key_1to1()

def init_game():
    global maze, dots, tissues, allergens, player, sneeze_bar, sneezing, sneeze_message_timer
    global timer, timer_max, timer_running, timer_gameover, game_won, score_this_level, moving_allergens
    global game_over_reason, doors, keys, player_keys_collected, key_to_door
    maze[:] = generate_maze()
    dots[:] = []
    tissues[:] = []
    allergens[:] = []
    moving_allergens[:] = []
    doors[:] = []
    keys[:] = []
    player_keys_collected[:] = []
    key_to_door = {}
    for y in range(ROWS):
        for x in range(COLS):
            if maze[y][x] == 0 and (x, y) != (1,1):
                dots.append((x, y))
                r = random(1)
                if r < 0.08:
                    tissues.append((x, y))
                elif r < 0.13:
                    if level > 3:
                        moving_allergens.append(MovingAllergen(x, y, 24))
                    else:
                        allergens.append((x, y))
    if level >= 4:
        place_door_and_key_1to1()
    player = Player(1, 1)
    sneeze_bar = 0
    sneezing = False
    sneeze_message_timer = 0
    timer_max = get_timer_for_level(level)
    timer = timer_max
    timer_running = True
    timer_gameover = False
    game_won = False
    score_this_level = 0
    game_over_reason = ""
    spawn_germs()

def get_timer_for_level(lvl):
    return 60 * 30  

def generate_maze():
    m = [[1 for _ in range(COLS)] for _ in range(ROWS)]
    stack = [(1, 1)]
    m[1][1] = 0
    directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
    while stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 < nx < COLS - 1 and 0 < ny < ROWS - 1 and m[ny][nx] == 1:
                neighbors.append((nx, ny, dx, dy))
        if neighbors:
            idx = int(random(len(neighbors)))
            nx, ny, dx, dy = neighbors[idx]
            m[y + dy // 2][x + dx // 2] = 0
            m[ny][nx] = 0
            stack.append((nx, ny))
        else:
            stack.pop()
    m[1][1] = 0
    return m

class Player(object):
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.target_x = grid_x
        self.target_y = grid_y
        self.moving = False

    def move(self, dx, dy):
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy
        if (new_x, new_y) in doors and (new_x, new_y) not in player_keys_collected:
            return
        if 0 <= new_x < COLS and 0 <= new_y < ROWS and maze[new_y][new_x] == 0:
            self.moving = True
            self.target_x = new_x
            self.target_y = new_y

    def update(self):
        if self.moving:
            self.grid_x = self.target_x
            self.grid_y = self.target_y
            self.moving = False

    def display(self):
        x = MAZE_X + self.grid_x * CELL_SIZE
        y = MAZE_Y + self.grid_y * CELL_SIZE
        if sneezing and player_sneeze_img:
            image(player_sneeze_img, x, y, CELL_SIZE, CELL_SIZE)
        elif player_img:
            image(player_img, x, y, CELL_SIZE, CELL_SIZE)
        else:
            fill(ORANGE)
            rect(x, y, CELL_SIZE, CELL_SIZE)

def draw():
    if state == STATE_INSTRUCTIONS:
        draw_instructions()
    elif state == STATE_STAGE_SELECT:
        draw_stage_select()
    elif state == STATE_LEVEL_SELECT:
        draw_level_select()
    elif state == STATE_GAME:
        draw_game()

def draw_maze():
    for y in range(ROWS):
        for x in range(COLS):
            if maze[y][x] == 1:
                fill(YELLOW)
                noStroke()
                rect(MAZE_X + x * CELL_SIZE, MAZE_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

def draw_doors_and_keys():
    for d in doors:
        if door_img:
            image(door_img, MAZE_X + d[0] * CELL_SIZE, MAZE_Y + d[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    for i, k in enumerate(keys):
        if k not in player_keys_collected:
            if key_img:
                image(key_img, MAZE_X + k[0] * CELL_SIZE, MAZE_Y + k[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)

def draw_dots():
    fill(WHITE)
    noStroke()
    for (x, y) in dots:
        ellipse(MAZE_X + x * CELL_SIZE + CELL_SIZE / 2, MAZE_Y + y * CELL_SIZE + CELL_SIZE / 2, 8, 8)

def draw_tissues():
    for (x, y) in tissues:
        if tissue_img is not None:
            image(tissue_img, MAZE_X + x * CELL_SIZE, MAZE_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        else:
            fill(GREEN)
            ellipse(MAZE_X + x * CELL_SIZE + CELL_SIZE / 2, MAZE_Y + y * CELL_SIZE + CELL_SIZE / 2, 12, 12)

def draw_allergens():
    for (x, y) in allergens:
        if germ_img:
            image(germ_img, MAZE_X + x * CELL_SIZE, MAZE_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        else:
            fill(RED)
            ellipse(MAZE_X + x * CELL_SIZE + CELL_SIZE / 2, MAZE_Y + y * CELL_SIZE + CELL_SIZE / 2, 12, 12)
    for a in moving_allergens:
        a.display()

def draw_instructions():
    background(YELLOW)
    win_w, win_h = int(width * 0.7), int(height * 0.6)
    rx = width // 2 - win_w // 2
    ry = height // 2 - win_h // 2
    rect_fill = color(255, 235, 100)
    fill(rect_fill)
    noStroke()
    rect(rx, ry, win_w, win_h, 30)
    left_margin = 40
    lines = [
        "SNEEZE ATTACK!",
        "By HamzaxDevelopers !",
        "1. Use Arrow Keys to move.",
        "2. Collect tissues to reduce sneeze bar.",
        "3. Avoid allergens which increase it.",
        "4. From level 2: Germs will move!",
        "5. From level 4: Find key to open doors!",
        "6. From Level 7: Avoid sneeze, it will increase hurdles.",
        "7. Timeline reduces 5 sec for every stage (complexity).",
        "8. Speed of Germs gradually increases as level up and up.",
        "Press any key to continue..."
    ]
    textFont(createFont("Arial", 20))
    line_spacing = 32
    total_height = line_spacing * len(lines)
    text_start_y = ry + (win_h - total_height) // 2
    fill(NAVY)
    for i, line in enumerate(lines[:-1]):
        text(line, rx + left_margin, text_start_y + i * line_spacing)
    fill(RED)
    text(lines[-1], width//2 - textWidth(lines[-1])//2, ry + win_h - 38)

def draw_stage_select():
    background(NAVY)
    win_w, win_h = int(width * 0.5), int(height * 0.36)
    rx = width // 2 - win_w // 2
    ry = height // 2 - win_h // 2
    fill(YELLOW)
    rect(rx, ry, win_w, win_h, 30)
    fill(NAVY)
    textFont(createFont("Arial Bold", 32))
    text("Select Stage", width//2 - 90, ry + 50)
    stages = ["Easy (1)", "Medium (2)", "Difficult (3)"]
    textFont(createFont("Arial", 24))
    for i, s in enumerate(stages):
        text(s, rx + 70, ry + 100 + i*50)
    fill(RED)
    text("Press 1, 2, or 3 to select", width//2 - 105, ry + win_h - 24)

def draw_level_select():
    background(NAVY)
    win_w, win_h = int(width * 0.5), int(height * 0.36)
    rx = width // 2 - win_w // 2
    ry = height // 2 - win_h // 2
    fill(YELLOW)
    rect(rx, ry, win_w, win_h, 30)
    stage_names = ["Easy", "Medium", "Difficult"]
    fill(NAVY)
    textFont(createFont("Arial Bold", 32))
    text(stage_names[selected_stage-1] + " Stage", width//2 - 90, ry + 50)
    base_level = 1 + (selected_stage-1)*3
    textFont(createFont("Arial", 24))
    for i in range(3):
        text("Level %d (%d)" % (base_level+i, i+1), rx + 70, ry + 100 + i*50)
    fill(RED)
    text("Press 1, 2, or 3 to select level", width//2 - 130, ry + win_h - 24)

def draw_game():
    background(NAVY)
    draw_maze()
    draw_doors_and_keys()
    draw_dots()
    draw_tissues()
    draw_allergens()
    draw_exit_label()
    draw_germs()
    draw_player()
    draw_top_bar()
    check_collisions()
    draw_sneeze_message()
    handle_continuous_movement()
    update_germs()
    update_moving_allergens()
    handle_timer_gameover()
    handle_game_win()

def draw_exit_label():
    label = "EXIT"
    fontSize = int(CELL_SIZE * 0.8)
    textSize(fontSize)
    fill(GREEN)
    exit_x = MAZE_X + (COLS-2) * CELL_SIZE
    exit_y = MAZE_Y + (ROWS-2) * CELL_SIZE
    textAlign(CENTER, CENTER)
    text(label, exit_x + CELL_SIZE, exit_y + CELL_SIZE/2)

def draw_germs():
    for germ in germs:
        germ.display()

def draw_player():
    player.update()
    player.display()

def draw_top_bar():
    global sneeze_bar, timer, timer_max, level, score, timer_running, game_won, timer_gameover
    bar_x = 40
    bar_y = 30
    bar_width = 240
    bar_height = 18
    fill(GRAY)
    rect(bar_x, bar_y, bar_width, bar_height, 10)
    fill(RED)
    fill_width = int(bar_width * constrain(sneeze_bar, 0, 100) / 100)
    rect(bar_x, bar_y, fill_width, bar_height, 10)
    fill(WHITE)
    textSize(14)
    textAlign(LEFT, CENTER)
    text("Sneeze Bar", bar_x, bar_y - 8)
    if not sneezing and timer_running and not game_won:
        sneeze_bar += 0.08
        sneeze_bar = min(sneeze_bar, 100)
    timer_x = width - 180
    timer_y = 30
    timer_w = 120
    timer_h = 18
    if timer_running and not game_won:
        timer -= 1
        if timer <= 0:
            timer = 0
            timer_running = False
            timer_gameover = True
            global game_over_reason
            game_over_reason = "time"
    fill(GRAY)
    rect(timer_x, timer_y, timer_w, timer_h, 10)
    fill(WHITE)
    fill_width = int(timer_w * float(timer) / float(timer_max))
    rect(timer_x, timer_y, fill_width, timer_h, 10)
    fill(255)
    textSize(14)
    textAlign(LEFT, CENTER)
    sec_left = int(timer/30)
    text("Time:", timer_x, timer_y - 8)
    textAlign(CENTER, CENTER)
    text("{}s".format(sec_left), timer_x + timer_w/2, timer_y + timer_h/2)
    score_x = width/2 + 50
    fill(255, 240, 80)
    textSize(18)
    textAlign(LEFT, CENTER)
    text("Score: {}".format(score), score_x, 33)
    textAlign(RIGHT, CENTER)
    fill(255)
    textSize(16)
    text("Level: {}".format(level), width/2 - 60, 33)

def check_collisions():
    global sneeze_bar, sneezing, sneeze_message_timer
    global timer_running, timer_gameover, game_won, score, score_this_level
    px, py = player.grid_x, player.grid_y
    for i in range(len(keys)):
        if (px, py) == keys[i] and keys[i] not in player_keys_collected:
            player_keys_collected.append(keys[i])
            if keys[i] in key_to_door:
                door = key_to_door[keys[i]]
                if door not in player_keys_collected:
                    player_keys_collected.append(door)
                    if sound_door: sound_door.play()
    if not timer_running or game_won:
        return
    if (px, py) in dots:
        dots.remove((px, py))
    if (px, py) in tissues:
        tissues.remove((px, py))
        sneeze_bar = max(sneeze_bar - 20, 0)
        if sound_tissue: sound_tissue.play()
    if (px, py) in allergens:
        allergens.remove((px, py))
        sneeze_bar += 10
        sneeze_bar = min(sneeze_bar, 100)
        if sound_allergen: sound_allergen.play()
    if level > 3:
        for a in moving_allergens:
            if a.grid_x == px and a.grid_y == py:
                sneeze_bar += 10
                sneeze_bar = min(sneeze_bar, 100)
                if sound_allergen: sound_allergen.play()
    if sneeze_bar >= 100 and not sneezing:
        sneezing = True
        sneeze_message_timer = 8
        sneeze_bar = 0
        if sound_sneeze: sound_sneeze.play()
        if level >= 7:
            handle_sneeze_special()
    if (px, py) == (COLS-2, ROWS-2):
        timer_running = False
        game_won = True
        sec_left = int(timer/30)
        score_this_level = 5 * sec_left
        score += score_this_level

def update_germs():
    if level >= 2 and not game_won and timer_running:
        for germ in germs:
            germ.update()

def update_moving_allergens():
    if level > 3:
        for a in moving_allergens:
            a.update()

def draw_sneeze_message():
    global sneezing, sneeze_message_timer
    if sneezing and sneeze_message_timer > 0:
        fill(255, 255, 0)
        textSize(40)
        textAlign(CENTER, CENTER)
        text("ACHOO!", width/2, 55)
        sneeze_message_timer -= 1
    if sneeze_message_timer <= 0 and sneezing:
        sneezing = False

def handle_continuous_movement():
    global move_cooldown
    if move_cooldown > 0:
        move_cooldown -= 1
        return
    if not player.moving and timer_running and not game_won:
        if moving_up:
            player.move(0, -1)
            move_cooldown = MOVE_DELAY
        elif moving_down:
            player.move(0, 1)
            move_cooldown = MOVE_DELAY
        elif moving_left:
            player.move(-1, 0)
            move_cooldown = MOVE_DELAY
        elif moving_right:
            player.move(1, 0)
            move_cooldown = MOVE_DELAY

def handle_timer_gameover():
    global timer_gameover, timer_running, score
    if timer_gameover:
        fill(255, 0, 0, 220)
        rectMode(CENTER)
        rect(width/2, height/2, 340, 120, 22)
        fill(255)
        textSize(34)
        textAlign(CENTER, CENTER)
        if game_over_reason == "time":
            text("Time's Up!", width/2, height/2-18)
        else:
            text("Game Over!", width/2, height/2-18)
        textSize(18)
        text("Final Score: {}".format(score), width/2, height/2+10)
        text("Press 'R' to Restart", width/2, height/2+34)
        rectMode(CORNER)
        timer_running = False

def handle_game_win():
    global game_won, score_this_level
    if game_won:
        fill(0, 180, 0, 220)
        rectMode(CENTER)
        rect(width/2, height/2, 420, 170, 22)
        fill(255)
        textSize(34)
        textAlign(CENTER, CENTER)
        text("You Escaped!", width/2, height/2-40)
        textSize(20)
        text("Level Score: +{}".format(score_this_level), width/2, height/2-10)
        text("Total Score: {}".format(score), width/2, height/2+18)
        textSize(18)
        text("Press 'N' for next level", width/2, height/2+48)
        text("Press 'R' to restart", width/2, height/2+72)
        rectMode(CORNER)

def next_level():
    global level, timer_gameover, game_won, score_this_level
    level += 1
    timer_gameover = False
    game_won = False
    score_this_level = 0
    init_game()

def keyPressed():
    global moving_up, moving_down, moving_left, moving_right
    global timer_gameover, game_won, level, score, timer_running
    global state, selected_stage, selected_level
    if state == STATE_INSTRUCTIONS:
        state = STATE_STAGE_SELECT
        return
    elif state == STATE_STAGE_SELECT:
        if key in ['1', '2', '3']:
            selected_stage = int(key)
            state = STATE_LEVEL_SELECT
        return
    elif state == STATE_LEVEL_SELECT:
        if key in ['1','2','3']:
            selected_level = int(key)
            level = (selected_stage - 1) * 3 + selected_level
            state = STATE_GAME
            init_game()
        return
    elif state == STATE_GAME:
        if timer_gameover and (key == 'r' or key == 'R'):
            timer_gameover = False
            game_won = False
            level = 1
            score = 0
            timer_running = True
            state = STATE_STAGE_SELECT
            return
        if game_won and (key == 'n' or key == 'N'):
            next_level()
            return
        if (timer_gameover or game_won) and (key == 'r' or key == 'R'):
            timer_gameover = False
            game_won = False
            level = 1
            score = 0
            timer_running = True
            state = STATE_STAGE_SELECT
            return
        if not timer_running or game_won:
            return
        if keyCode == UP:
            moving_up = True
        elif keyCode == DOWN:
            moving_down = True
        elif keyCode == LEFT:
            moving_left = True
        elif keyCode == RIGHT:
            moving_right = True

def keyReleased():
    global moving_up, moving_down, moving_left, moving_right
    if state != STATE_GAME:
        return
    if keyCode == UP:
        moving_up = False
    elif keyCode == DOWN:
        moving_down = False
    elif keyCode == LEFT:
        moving_left = False
    elif keyCode == RIGHT:
        moving_right = False
