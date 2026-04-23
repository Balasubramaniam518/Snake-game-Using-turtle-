import turtle as t
import random
import time
import json
import os

WIDTH, HEIGHT = 700, 700
GRID = 20
WALL = 320
HS_FILE = "snake_highscores.json"

BG          = "#0a0a1a"
NEON_GREEN  = "#39ff14"
NEON_CYAN   = "#00fff7"
NEON_PINK   = "#ff006e"
NEON_YELLOW = "#ffe600"
NEON_ORANGE = "#ff6b00"
DARK_PANEL  = "#12122a"
GRID_COLOR  = "#1a1a3a"
WHITE       = "#ffffff"
STAR_COLOR  = "#ffffff"


def load_scores():
    if os.path.exists(HS_FILE):
        try:
            with open(HS_FILE) as f:
                return json.load(f)
        except:
            pass
    return []

def save_score(score):
    scores = load_scores()
    scores.append(score)
    scores = sorted(scores, reverse=True)[:5]
    with open(HS_FILE, "w") as f:
        json.dump(scores, f)
    return scores


sc = t.Screen()
sc.title("NEON SNAKE")
sc.bgcolor(BG)
sc.setup(width=WIDTH, height=HEIGHT)
sc.tracer(0)


def make_turtle(shape="square", color=WHITE, visible=True):
    T = t.Turtle()
    T.speed(0)
    T.shape(shape)
    T.color(color)
    T.penup()
    if not visible:
        T.hideturtle()
    return T


stars = []

def draw_stars():
    for _ in range(80):
        s = make_turtle("circle", STAR_COLOR, True)
        s.shapesize(random.uniform(0.05, 0.2))
        s.goto(random.randint(-340, 340), random.randint(-340, 340))
        stars.append(s)

def clear_stars():
    for s in stars:
        s.hideturtle()
    stars.clear()


grid_turtles = []

def draw_grid():
    pen = make_turtle(visible=False)
    pen.color(GRID_COLOR)
    pen.pensize(1)
    pen.speed(0)
    for x in range(-WALL, WALL + 1, GRID):
        pen.penup()
        pen.goto(x, -WALL)
        pen.pendown()
        pen.goto(x, WALL)
    for y in range(-WALL, WALL + 1, GRID):
        pen.penup()
        pen.goto(-WALL, y)
        pen.pendown()
        pen.goto(WALL, y)
    pen.penup()
    grid_turtles.append(pen)

def clear_grid():
    for g in grid_turtles:
        g.clear()
        g.hideturtle()
    grid_turtles.clear()


border_pen = None

def draw_border(color=NEON_CYAN, width=3):
    global border_pen
    if border_pen:
        border_pen.clear()
    else:
        border_pen = make_turtle(visible=False)
    border_pen.color(color)
    border_pen.pensize(width)
    border_pen.goto(-WALL, -WALL)
    border_pen.pendown()
    for _ in range(4):
        border_pen.forward(WALL * 2)
        border_pen.left(90)
    border_pen.penup()


particles = []

def burst(x, y, color):
    for _ in range(8):
        p = make_turtle("circle", color)
        p.shapesize(0.3)
        px = x + random.randint(-30, 30)
        py = y + random.randint(-30, 30)
        p.goto(px, py)
        particles.append(p)
    sc.update()
    sc.ontimer(lambda: clear_particles(), 200)

def clear_particles():
    for p in particles:
        p.hideturtle()
    particles.clear()


overlays = []

def label(txt, x, y, color=WHITE, font=("Courier", 18, "bold"), align="center"):
    T = make_turtle(visible=False)
    T.color(color)
    T.goto(x, y)
    T.write(txt, align=align, font=font)
    overlays.append(T)
    return T

def box(x, y, w, h, fill_color, outline=None):
    T = make_turtle(visible=False)
    T.color(fill_color)
    T.goto(x, y)
    T.begin_fill()
    for dx, dy in [(w, 0), (0, -h), (-w, 0), (0, h)]:
        T.goto(T.xcor() + dx, T.ycor() + dy)
    T.end_fill()
    if outline:
        T.color(outline)
        T.pensize(2)
        T.goto(x, y)
        T.pendown()
        for dx, dy in [(w, 0), (0, -h), (-w, 0), (0, h)]:
            T.goto(T.xcor() + dx, T.ycor() + dy)
        T.penup()
    overlays.append(T)
    return T

def clear_overlays():
    for o in overlays:
        o.clear()
        o.hideturtle()
    overlays.clear()


logo_segs = []

def draw_logo_snake():
    colors = [NEON_GREEN, NEON_CYAN, NEON_YELLOW, NEON_ORANGE, NEON_PINK]
    positions = [
        (-80, 180), (-60, 180), (-40, 180), (-20, 180), (0, 180),
        (20, 180), (40, 180), (40, 160), (40, 140), (20, 140), (0, 140)
    ]
    for i, pos in enumerate(positions):
        seg = make_turtle("square", colors[i % len(colors)])
        seg.shapesize(0.9)
        seg.goto(1000, 1000)
        logo_segs.append((seg, pos))

def animate_logo():
    for i, (seg, pos) in enumerate(logo_segs):
        sc.ontimer(lambda s=seg, p=pos: (s.goto(p), sc.update()), i * 60)

def clear_logo():
    for seg, _ in logo_segs:
        seg.hideturtle()
    logo_segs.clear()


pulse_colors = [NEON_CYAN, NEON_GREEN, NEON_PINK, NEON_YELLOW, NEON_CYAN]
pulse_idx = [0]

def pulse_border():
    if game_state[0] == "playing":
        c = pulse_colors[pulse_idx[0] % len(pulse_colors)]
        draw_border(c, 3)
        pulse_idx[0] += 1
        sc.ontimer(pulse_border, 400)


hud = None

def init_hud():
    global hud
    hud = make_turtle(visible=False)
    hud.color(NEON_GREEN)
    hud.goto(0, WALL + 15)
    hud.write("Score: 0   Best: 0", align="center", font=("Courier", 16, "bold"))

def update_hud(score, best):
    hud.clear()
    hud.write(f"Score: {score}   Best: {best}", align="center", font=("Courier", 16, "bold"))


game_state = ["menu"]
s  = 0
hs = 0
d  = 0.1
seg = []

h = make_turtle("square", NEON_GREEN)
h.shapesize(0.85)
h.goto(0, 0)
h.direction = "Stop"
h.hideturtle()

f = make_turtle("circle", NEON_PINK)
f.shapesize(0.7)
f.hideturtle()


def up():
    if h.direction != "down":
        h.direction = "up"

def down():
    if h.direction != "up":
        h.direction = "down"

def left():
    if h.direction != "right":
        h.direction = "left"

def right():
    if h.direction != "left":
        h.direction = "right"

def move():
    if h.direction == "up":
        h.sety(h.ycor() + GRID)
    if h.direction == "down":
        h.sety(h.ycor() - GRID)
    if h.direction == "left":
        h.setx(h.xcor() - GRID)
    if h.direction == "right":
        h.setx(h.xcor() + GRID)

sc.listen()
sc.onkeypress(up,    "Up")
sc.onkeypress(down,  "Down")
sc.onkeypress(left,  "Left")
sc.onkeypress(right, "Right")
sc.onkeypress(up,    "w")
sc.onkeypress(down,  "s")
sc.onkeypress(left,  "a")
sc.onkeypress(right, "d")


def show_menu():
    game_state[0] = "menu"
    clear_overlays()
    clear_logo()
    sc.bgcolor(BG)
    draw_stars()
    draw_border(NEON_CYAN, 4)

    label("N E O N",   0, 230, NEON_CYAN,  ("Courier", 32, "bold"))
    label("S N A K E", 0, 170, NEON_GREEN, ("Courier", 48, "bold"))

    draw_logo_snake()
    animate_logo()

    box(-110, 80, 220, 50, DARK_PANEL, NEON_GREEN)
    label("▶   PLAY", 0, 55, NEON_GREEN, ("Courier", 20, "bold"))

    box(-110, 10, 220, 50, DARK_PANEL, NEON_YELLOW)
    label("🏆  HIGH SCORES", 0, -15, NEON_YELLOW, ("Courier", 18, "bold"))

    label("Arrow Keys / WASD to move",        0, -80,  "#555577", ("Courier", 12, "normal"))
    label("Eat food. Avoid walls & yourself.", 0, -105, "#555577", ("Courier", 12, "normal"))

    sc.update()

    def menu_click(x, y):
        if -110 <= x <= 110 and 30 <= y <= 80:
            sc.onclick(None)
            start_game()
        elif -110 <= x <= 110 and -40 <= y <= 10:
            sc.onclick(None)
            show_highscores()

    sc.onclick(menu_click)


def show_highscores():
    clear_overlays()
    draw_border(NEON_YELLOW, 4)

    label("🏆  HIGH SCORES", 0, 240, NEON_YELLOW, ("Courier", 28, "bold"))

    scores = load_scores()
    medals = ["🥇", "🥈", "🥉", "④", "⑤"]

    if scores:
        for i, sc_val in enumerate(scores):
            col = [NEON_YELLOW, "#cccccc", NEON_ORANGE, NEON_CYAN, NEON_GREEN][i]
            label(f"{medals[i]}   {sc_val:>6} pts", 0, 160 - i * 60, col, ("Courier", 20, "bold"))
    else:
        label("No scores yet!", 0, 100, "#555577", ("Courier", 18, "italic"))

    box(-90, -200, 180, 46, DARK_PANEL, NEON_CYAN)
    label("← BACK", 0, -225, NEON_CYAN, ("Courier", 18, "bold"))

    sc.update()

    def hs_click(x, y):
        if -90 <= x <= 90 and -246 <= y <= -200:
            sc.onclick(None)
            show_menu()

    sc.onclick(hs_click)


def start_game():
    global s, d, seg, hs
    game_state[0] = "playing"
    clear_overlays()
    clear_logo()
    clear_stars()

    scores = load_scores()
    hs = scores[0] if scores else 0

    s = 0
    d = 0.12

    for segment in seg:
        segment.hideturtle()
    seg.clear()

    sc.bgcolor(BG)
    draw_grid()
    draw_border(NEON_CYAN, 3)
    pulse_border()

    h.color(NEON_GREEN)
    h.shapesize(0.85)
    h.goto(0, 0)
    h.direction = "Stop"
    h.showturtle()

    f.color(NEON_PINK)
    f.shape("circle")
    f.shapesize(0.7)
    f.goto(random.randint(-15, 15) * GRID, random.randint(-15, 15) * GRID)
    f.showturtle()

    init_hud()
    update_hud(s, hs)
    countdown()


def countdown():
    nums = ["3",         "2",          "1",         "GO!"]
    cols = [NEON_ORANGE, NEON_YELLOW, NEON_GREEN,  NEON_CYAN]

    def show_num(i):
        if i < len(nums):
            clear_overlays()
            draw_border(cols[i], 4)
            label(nums[i], 0, 0, cols[i], ("Courier", 72, "bold"))
            sc.update()
            sc.ontimer(lambda: show_num(i + 1), 700)
        else:
            clear_overlays()
            draw_border(NEON_CYAN, 3)
            update_hud(s, hs)
            sc.update()
            run_game()

    show_num(0)


def run_game():
    global s, d, hs

    if game_state[0] != "playing":
        return

    sc.update()

    if h.xcor() > WALL or h.xcor() < -WALL or h.ycor() > WALL or h.ycor() < -WALL:
        trigger_game_over()
        return

    if h.distance(f) < GRID:
        burst(f.xcor(), f.ycor(), NEON_PINK)

        fx = random.randint(-15, 15) * GRID
        fy = random.randint(-15, 15) * GRID
        f.goto(fx, fy)
        f.color(random.choice([NEON_PINK, NEON_ORANGE, NEON_YELLOW, NEON_CYAN]))

        n_seg = make_turtle("square", NEON_GREEN)
        n_seg.shapesize(0.85)
        seg.append(n_seg)

        d = max(0.04, d - 0.003)
        s += 10
        if s > hs:
            hs = s
        update_hud(s, hs)

        draw_border(NEON_PINK, 5)
        sc.ontimer(lambda: draw_border(NEON_CYAN, 3), 150)

    for i in range(len(seg) - 1, 0, -1):
        seg[i].goto(seg[i - 1].xcor(), seg[i - 1].ycor())

    if seg:
        seg[0].goto(h.xcor(), h.ycor())

    rainbow = [NEON_GREEN, NEON_CYAN, NEON_YELLOW, NEON_ORANGE, NEON_PINK]
    for i, segment in enumerate(seg):
        segment.color(rainbow[i % len(rainbow)])

    move()

    for segment in seg[3:]:
        if segment.distance(h) < GRID * 0.8:
            trigger_game_over()
            return

    sc.ontimer(run_game, int(d * 1000))


def trigger_game_over():
    game_state[0] = "gameover"
    scores = save_score(s)

    for i in range(6):
        sc.ontimer(lambda i=i: draw_border(NEON_PINK if i % 2 == 0 else BG, 5), i * 100)

    sc.ontimer(lambda: show_game_over(scores), 700)


def show_game_over(scores):
    clear_overlays()
    draw_border(NEON_PINK, 4)

    box(-200, 200, 400, 380, DARK_PANEL, NEON_PINK)

    label("GAME  OVER",   0, 140, NEON_PINK,   ("Courier", 34, "bold"))
    label(f"Score:  {s}", 0,  80, NEON_YELLOW, ("Courier", 22, "bold"))

    is_best = scores and scores[0] == s and s > 0
    if is_best:
        label("🎉 NEW BEST!", 0, 40, NEON_CYAN, ("Courier", 18, "bold"))

    label("— TOP SCORES —", 0, 0 if not is_best else -10, "#888899", ("Courier", 13, "normal"))

    for i, sc_val in enumerate(scores[:3]):
        col = [NEON_YELLOW, "#aaaaaa", NEON_ORANGE][i]
        label(f"#{i+1}  {sc_val} pts", 0, (-30 if not is_best else -40) - i * 28, col, ("Courier", 15, "bold"))

    box(-100, -110, 200, 46, DARK_PANEL, NEON_GREEN)
    label("▶  PLAY AGAIN", 0, -134, NEON_GREEN, ("Courier", 16, "bold"))

    box(-100, -170, 200, 46, DARK_PANEL, NEON_CYAN)
    label("⌂  MAIN MENU",  0, -194, NEON_CYAN,  ("Courier", 16, "bold"))

    box(-100, -230, 200, 46, DARK_PANEL, NEON_PINK)
    label("✕  QUIT",       0, -254, NEON_PINK,  ("Courier", 16, "bold"))

    sc.update()

    def go_click(x, y):
        if -100 <= x <= 100 and -156 <= y <= -110:
            sc.onclick(None)
            h.hideturtle()
            f.hideturtle()
            for segment in seg:
                segment.hideturtle()
            seg.clear()
            clear_grid()
            start_game()
        elif -100 <= x <= 100 and -216 <= y <= -170:
            sc.onclick(None)
            h.hideturtle()
            f.hideturtle()
            for segment in seg:
                segment.hideturtle()
            seg.clear()
            clear_grid()
            show_menu()
        elif -100 <= x <= 100 and -276 <= y <= -230:
            sc.bye()

    sc.onclick(go_click)


show_menu()
t.mainloop()
