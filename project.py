"""
COSMIC DEFENDER - Single Window Edition
Turtle Intro -> Pygame Game + Matplotlib Live Stats Panel (side by side)
Install: pip install pygame matplotlib pillow
Controls: LEFT/RIGHT move, SPACE shoot, P pause, R restart, ESC quit
"""
import math, random, time, io
import turtle
import pygame
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from PIL import Image

# ── Layout ─────────────────────────────────────────────────────────
GAME_W, GAME_H = 700, 650
PANEL_W        = 340
WIN_W          = GAME_W + PANEL_W
WIN_H          = GAME_H
FPS            = 60

# ── Colours ────────────────────────────────────────────────────────
C_BG     = (  5,   5,  20)
C_PANEL  = ( 10,  10,  30)
C_WHITE  = (255, 255, 255)
C_CYAN   = (  0, 220, 255)
C_ORANGE = (255, 140,   0)
C_RED    = (255,  50,  50)
C_GREEN  = ( 50, 255, 120)
C_YELLOW = (255, 220,  50)
C_PURPLE = (180,  80, 255)
C_GREY   = (100, 100, 130)
C_PINK   = (255,  80, 180)
ENEMY_COLS = [C_RED, C_ORANGE, C_PURPLE, C_PINK]

# ══════════════════════════════════════════════
# TURTLE INTRO
# ══════════════════════════════════════════════
def turtle_intro():
    sc = turtle.Screen()
    sc.title("COSMIC DEFENDER - Press ENTER to Play")
    sc.bgcolor("black")
    sc.setup(660, 480)
    sc.tracer(0)
    t = turtle.Turtle()
    t.hideturtle(); t.speed(0); t.penup()

    for _ in range(200):
        t.goto(random.randint(-320,320), random.randint(-230,230))
        t.dot(random.uniform(1,3), random.choice(["white","#aaeeff","#ffeeaa","#ffaacc"]))

    t.goto(160, 90); t.color("#1a3a6a"); t.begin_fill(); t.circle(50); t.end_fill()
    t.goto(160, 90); t.color("#2255aa"); t.begin_fill(); t.circle(28); t.end_fill()
    t.pendown(); t.color("#4488dd"); t.width(3)
    for a in range(0, 181, 4):
        r = math.radians(a)
        t.goto(160+65*math.cos(r), 125+16*math.sin(r))
    t.penup()

    rx, ry = -50, -50
    t.color("cyan"); t.goto(rx, ry); t.pendown(); t.begin_fill()
    for dx,dy in [(0,28),(7,8),(7,-14),(-7,-14),(-7,8),(0,28)]:
        t.goto(rx+dx, ry+dy)
    t.end_fill(); t.penup()
    t.color("orange"); t.goto(rx, ry-14); t.begin_fill()
    t.goto(rx-4,ry-14); t.goto(rx,ry-30); t.goto(rx+4,ry-14); t.goto(rx,ry-14)
    t.end_fill(); t.penup()

    t.color("#00e6ff"); t.goto(0, 28)
    t.write("COSMIC  DEFENDER", align="center", font=("Courier New", 24, "bold"))
    t.color("#ffaa00"); t.goto(0, -4)
    t.write("Turtle  x  Pygame  x  Matplotlib", align="center", font=("Courier New", 10, "normal"))

    bt = turtle.Turtle(); bt.hideturtle(); bt.penup()
    for _ in range(7):
        sc.update()
        bt.clear(); bt.goto(0,-68); bt.color("#88ff99")
        bt.write("Press  ENTER  to  Launch", align="center", font=("Courier New",12,"bold"))
        sc.update(); time.sleep(0.35)
        bt.clear(); time.sleep(0.35)
    sc.update()
    sc.onkey(sc.bye, "Return")
    sc.listen()
    try:
        sc.mainloop()
    except Exception:
        pass

# ══════════════════════════════════════════════
# MATPLOTLIB -> PYGAME SURFACE (Agg, no window)
# ══════════════════════════════════════════════
def make_chart_surface(score_hist, acc_hist, wave_hist, kill_xs, kill_ys, width, height):
    dpi = 80
    fig = plt.figure(figsize=(width/dpi, height/dpi), facecolor="#080818", dpi=dpi)
    gs  = gridspec.GridSpec(3, 1, figure=fig, hspace=0.72,
                            left=0.15, right=0.93, top=0.93, bottom=0.07)
    axes = [fig.add_subplot(gs[i]) for i in range(3)]

    for ax in axes:
        ax.set_facecolor("#0a0a1e")
        for sp in ax.spines.values(): sp.set_color("#223344")
        ax.tick_params(colors="#667788", labelsize=7)
        ax.title.set_color("#00e6ff"); ax.title.set_fontsize(8)

    # Score
    ax = axes[0]; ax.set_title("Score Over Time")
    xs = list(range(len(score_hist)))
    ax.fill_between(xs, score_hist, color="#00e6ff", alpha=0.2)
    ax.plot(xs, score_hist, color="#00e6ff", lw=1.4)
    ax.set_xlim(0, max(1, len(score_hist)-1))
    ax.set_ylim(0, max(10, max(score_hist)*1.15))

    # Accuracy + Wave
    ax = axes[1]; ax.set_title("Accuracy % | Wave")
    acc  = acc_hist[-1]  if acc_hist  else 0.0
    wave = wave_hist[-1] if wave_hist else 1
    col  = "#ff4444" if acc < 30 else "#ffaa00" if acc < 60 else "#44ff88"
    ax.barh(["Acc"],  [acc],       color=col,      height=0.35)
    ax.barh(["Acc"],  [100-acc],   left=[acc],     color="#1a1a2e", height=0.35)
    ax.barh(["Wave"], [wave],      color="#cba6f7", height=0.35)
    ax.set_xlim(0, max(100, wave+2))
    ax.text(acc+1,    0, f"{acc:.0f}%",  va="center", color="white", fontsize=7)
    ax.text(wave+0.3, 1, f"W{wave}",     va="center", color="white", fontsize=7)

    # Kill heatmap
    ax = axes[2]; ax.set_title("Kill Heatmap")
    if len(kill_xs) >= 4:
        h, _, _ = np.histogram2d(kill_xs, kill_ys, bins=[12,8],
                                 range=[[0,GAME_W],[0,GAME_H]])
        ax.imshow(h.T, origin="upper", aspect="auto",
                  extent=[0,GAME_W,GAME_H,0], cmap="plasma", alpha=0.9)
    else:
        ax.text(0.5, 0.5, "Kill enemies to\nbuild heatmap",
                transform=ax.transAxes, ha="center", va="center",
                color="#556677", fontsize=8)
    ax.set_xlim(0,GAME_W); ax.set_ylim(GAME_H,0)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor="#080818")
    plt.close(fig)
    buf.seek(0)
    pil  = Image.open(buf).convert("RGB").resize((width, height), Image.LANCZOS)
    surf = pygame.image.fromstring(pil.tobytes(), pil.size, "RGB")
    return surf

# ══════════════════════════════════════════════
# GAME OBJECTS
# ══════════════════════════════════════════════                        
class Particle:
    def __init__(self, x, y, col):
        a = random.uniform(0, math.tau); sp = random.uniform(1, 5)
        self.x=x; self.y=y; self.vx=math.cos(a)*sp; self.vy=math.sin(a)*sp
        self.max_life=random.randint(20,45); self.life=self.max_life
        self.col=col; self.sz=random.randint(2,5)
    def update(self):
        self.x+=self.vx; self.y+=self.vy; self.vy+=0.07; self.vx*=0.97; self.life-=1
    def draw(self, surf):
        f = self.life/self.max_life
        c = (int(self.col[0]*f), int(self.col[1]*f), int(self.col[2]*f))
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), self.sz)

class StarField:
    def __init__(self, n=160):
        self.stars = [self._mk() for _ in range(n)]
    def _mk(self, x=None):
        return {"x": x if x else random.randint(0,GAME_W),
                "y": random.randint(0,GAME_H), "sp": random.uniform(0.3,1.8),
                "r": random.randint(1,2),
                "c": random.choice([C_WHITE,C_CYAN,C_YELLOW,(200,200,220)])}
    def update(self):
        for i,s in enumerate(self.stars):
            s["y"] += s["sp"]
            if s["y"] > GAME_H:
                self.stars[i] = self._mk(x=random.randint(0,GAME_W))
                self.stars[i]["y"] = 0
    def draw(self, surf):
        for s in self.stars:
            pygame.draw.circle(surf, s["c"], (int(s["x"]),int(s["y"])), s["r"])

class Bullet:
    W, H = 4, 14
    def __init__(self, x, y, vy=-10, col=C_CYAN, enemy=False):
        self.x=x; self.y=y; self.vy=vy; self.col=col
        self.enemy=enemy; self.alive=True; self.trail=[]
    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail)>6: self.trail.pop(0)
        self.y += self.vy
        if self.y < -20 or self.y > GAME_H+20: self.alive = False
    def draw(self, surf):
        for i,(tx,ty) in enumerate(self.trail):
            a = int(180*i/max(1,len(self.trail)))
            c = tuple(min(255, int(ch*a/180)) for ch in self.col)
            pygame.draw.rect(surf, c, (tx-self.W//2, ty, self.W, self.H//2))
        pygame.draw.rect(surf, self.col, (self.x-self.W//2, self.y-self.H//2, self.W, self.H))
    def rect(self):
        return pygame.Rect(self.x-self.W//2, self.y-self.H//2, self.W, self.H)

class Enemy:
    SZ = 28
    def __init__(self, x, y, wave):
        self.x=float(x); self.y=float(y); self.base_y=float(y)
        self.wave=wave; self.hp=1+wave//3; self.max_hp=self.hp
        self.col=random.choice(ENEMY_COLS); self.alive=True
        self.ang=random.uniform(0,math.tau); self.shoot_cd=random.randint(80,200)
        self.t=random.uniform(0,math.tau); self.spd=1.0+wave*0.12
        self.pts=10*(1+wave//2); self.bob=random.uniform(16,32)
        self.bfreq=random.uniform(0.02,0.04)
    def update(self):
        self.t += self.bfreq
        self.y = self.base_y + math.sin(self.t)*self.bob
        self.base_y += self.spd*0.15
        self.ang += 0.05; self.shoot_cd -= 1
    def wants_shoot(self):
        if self.shoot_cd <= 0:
            self.shoot_cd = random.randint(100,220); return True
        return False
    def draw(self, surf):
        s=self.SZ; cx,cy=int(self.x),int(self.y)
        bw=32; filled=int(bw*self.hp/self.max_hp)
        pygame.draw.rect(surf, C_GREY,  (cx-bw//2, cy-s-7, bw, 3))
        pygame.draw.rect(surf, C_GREEN, (cx-bw//2, cy-s-7, filled, 3))
        pts = [(cx+math.cos(self.ang+i*math.pi/3)*s*0.55,
                cy+math.sin(self.ang+i*math.pi/3)*s*0.55) for i in range(6)]
        pygame.draw.polygon(surf, self.col, pts)
        pygame.draw.polygon(surf, C_WHITE, pts, 2)
        pygame.draw.circle(surf, C_WHITE, (cx,cy), s//5)
    def rect(self):
        s=self.SZ//2; return pygame.Rect(self.x-s, self.y-s, s*2, s*2)
    def hit(self):
        self.hp -= 1
        if self.hp <= 0: self.alive=False; return True
        return False

class Player:
    SPD = 5.5
    def __init__(self):
        self.x=GAME_W//2; self.y=GAME_H-80
        self.hp=5; self.max_hp=5
        self.shoot_cd=0; self.alive=True; self.inv=0; self.tt=0
    def update(self, keys):
        if keys[pygame.K_LEFT]  and self.x > 28:        self.x -= self.SPD
        if keys[pygame.K_RIGHT] and self.x < GAME_W-28: self.x += self.SPD
        if self.shoot_cd > 0: self.shoot_cd -= 1
        if self.inv > 0: self.inv -= 1
        self.tt += 0.3
    def shoot(self):
        if self.shoot_cd == 0:
            self.shoot_cd = 12
            return Bullet(self.x, self.y-26)
        return None
    def hit(self):
        if self.inv > 0: return False
        self.hp -= 1; self.inv = 90
        if self.hp <= 0: self.alive = False
        return True
    def draw(self, surf):
        if self.inv > 0 and (self.inv//6)%2 == 0: return
        cx,cy = self.x, self.y
        fh = 10 + int(8*abs(math.sin(self.tt)))
        pygame.draw.polygon(surf, C_ORANGE, [(cx-9,cy+18),(cx,cy+18+fh),(cx+9,cy+18)])
        pygame.draw.polygon(surf, C_YELLOW, [(cx-4,cy+18),(cx,cy+12+fh),(cx+4,cy+18)])
        pygame.draw.polygon(surf, C_CYAN,   [(cx,cy-22),(cx+17,cy+20),(cx+7,cy+14),(cx-7,cy+14),(cx-17,cy+20)])
        pygame.draw.polygon(surf, C_WHITE,  [(cx,cy-22),(cx+17,cy+20),(cx+7,cy+14),(cx-7,cy+14),(cx-17,cy+20)], 2)
        pygame.draw.ellipse(surf, C_YELLOW, (cx-6,cy-12,13,15))
        pygame.draw.line(surf, C_PURPLE, (cx-17,cy+20),(cx-7,cy+4), 2)
        pygame.draw.line(surf, C_PURPLE, (cx+17,cy+20),(cx+7,cy+4), 2)
    def rect(self):
        return pygame.Rect(self.x-13, self.y-22, 26, 44)

class ScreenShake:
    def __init__(self): self.f=0; self.n=0
    def trigger(self, n=6, f=10): self.f=f; self.n=n
    def offset(self):
        if self.f > 0:
            self.f -= 1
            return random.randint(-self.n,self.n), random.randint(-self.n,self.n)
        return 0, 0

# ══════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════
def spawn_wave(wave):
    count=5+wave*2; cols=min(count,9); rows=math.ceil(count/cols); out=[]
    for r in range(rows):
        for c in range(cols):
            if len(out)>=count: break
            x = 60 + c*((GAME_W-120)//(cols-1 if cols>1 else 1))
            y = 55  + r*68
            out.append(Enemy(x,y,wave))
    return out

def draw_hud(surf, score, wave, player, fb, fs):
    surf.blit(fb.render(f"* {score}", True, C_YELLOW), (10,6))
    wt = fs.render(f"WAVE {wave}", True, C_PURPLE)
    surf.blit(wt, (GAME_W//2 - wt.get_width()//2, 10))
    for i in range(player.max_hp):
        col = C_GREEN if i < player.hp else (40,40,60)
        pygame.draw.rect(surf, col, (GAME_W-24-i*22, 10, 16, 20), border_radius=3)
    pygame.draw.rect(surf, (12,12,32), (0,GAME_H-26,GAME_W,26))
    hint = fs.render("LEFT/RIGHT  |  SPACE SHOOT  |  P PAUSE  |  ESC QUIT", True, C_GREY)
    surf.blit(hint, (GAME_W//2 - hint.get_width()//2, GAME_H-20))

def draw_overlay(surf, text1, text2, fb, fs):
    ov = pygame.Surface((GAME_W,GAME_H), pygame.SRCALPHA)
    ov.fill((0,0,0,160)); surf.blit(ov,(0,0))
    t = fb.render(text1, True, C_CYAN)
    surf.blit(t, (GAME_W//2-t.get_width()//2, GAME_H//2-36))
    t2 = fs.render(text2, True, C_WHITE)
    surf.blit(t2, (GAME_W//2-t2.get_width()//2, GAME_H//2+16))

def draw_gameover(surf, score, wave, fb, fs):
    ov = pygame.Surface((GAME_W,GAME_H), pygame.SRCALPHA)
    ov.fill((0,0,0,180)); surf.blit(ov,(0,0))
    for i,(fnt,txt,col) in enumerate([
        (fb,"GAME  OVER",C_RED),
        (fs,f"Score : {score}",C_YELLOW),
        (fs,f"Wave  : {wave}",C_CYAN),
        (fs,"R = Restart     ESC = Quit",C_WHITE)]):
        s = fnt.render(txt, True, col)
        surf.blit(s, (GAME_W//2-s.get_width()//2, GAME_H//2-80+i*46))

# ══════════════════════════════════════════════
# MAIN GAME LOOP
# ══════════════════════════════════════════════
def run_game():
    pygame.init()
    win   = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("COSMIC DEFENDER  |  Game + Live Dashboard")
    clock = pygame.time.Clock()

    try:
        fb = pygame.font.SysFont("Courier New", 28, bold=True)
        fs = pygame.font.SysFont("Courier New", 14)
        fp = pygame.font.SysFont("Courier New", 11, bold=True)
    except Exception:
        fb = pygame.font.Font(None, 34)
        fs = pygame.font.Font(None, 18)
        fp = pygame.font.Font(None, 14)

    def new_state():
        return dict(
            player=Player(), enemies=spawn_wave(1),
            bullets=[], particles=[],
            score=0, wave=1, shots_fired=0, shots_hit=0,
            paused=False, over=False, wave_timer=120, show_wave=True,
            score_hist=[0], acc_hist=[0.0], wave_hist=[1],
            kill_xs=[], kill_ys=[],
        )

    G           = new_state()
    stars       = StarField()
    shake       = ScreenShake()
    chart_surf  = None
    frame       = 0
    CHART_EVERY = 90        # rebuild chart every ~1.5 s at 60fps
    game_surf   = pygame.Surface((GAME_W, GAME_H))
    panel_surf  = pygame.Surface((PANEL_W, WIN_H))

    running = True
    while running:
        clock.tick(FPS)
        frame += 1
        keys = pygame.key.get_pressed()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: running = False
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE: running = False
                if ev.key == pygame.K_p and not G["over"]:
                    G["paused"] = not G["paused"]
                if ev.key == pygame.K_r and G["over"]:
                    G = new_state(); stars = StarField(); frame = 0; chart_surf = None
                if (ev.key == pygame.K_SPACE
                        and not G["paused"] and not G["over"]
                        and not G["show_wave"]):
                    b = G["player"].shoot()
                    if b:
                        G["bullets"].append(b)
                        G["shots_fired"] += 1

        if not G["paused"] and not G["over"]:
            stars.update()
            G["player"].update(keys)

            if G["show_wave"]:
                G["wave_timer"] -= 1
                if G["wave_timer"] <= 0: G["show_wave"] = False
            else:
                for en in G["enemies"]:
                    en.update()
                    if en.y > GAME_H+50: en.alive = False
                    if en.wants_shoot():
                        G["bullets"].append(Bullet(en.x, en.y+16,
                            vy=random.uniform(3.5,5.5), col=C_RED, enemy=True))

            for b in G["bullets"]: b.update()

            for b in [x for x in G["bullets"] if not x.enemy and x.alive]:
                for en in [e for e in G["enemies"] if e.alive]:
                    if b.rect().colliderect(en.rect()):
                        b.alive = False; G["shots_hit"] += 1
                        if en.hit():
                            G["score"] += en.pts; shake.trigger(5,8)
                            for _ in range(20):
                                G["particles"].append(Particle(en.x,en.y,en.col))
                            G["kill_xs"].append(en.x)
                            G["kill_ys"].append(en.y)
                        break

            for b in [x for x in G["bullets"] if x.enemy and x.alive]:
                if b.rect().colliderect(G["player"].rect()):
                    b.alive = False
                    if G["player"].hit():
                        shake.trigger(9,14)
                        for _ in range(12):
                            G["particles"].append(Particle(G["player"].x, G["player"].y, C_ORANGE))

            for pt in G["particles"]: pt.update()
            G["bullets"]   = [b  for b  in G["bullets"]   if b.alive]
            G["enemies"]   = [e  for e  in G["enemies"]   if e.alive]
            G["particles"] = [pt for pt in G["particles"] if pt.life>0]

            if not G["enemies"] and not G["show_wave"]:
                G["wave"] += 1
                G["enemies"] = spawn_wave(G["wave"])
                G["wave_timer"] = 130; G["show_wave"] = True

            if not G["player"].alive:
                G["over"] = True; shake.trigger(14,22)

            if frame % 30 == 0:
                acc = (G["shots_hit"]/G["shots_fired"]*100 if G["shots_fired"] else 0)
                G["score_hist"].append(G["score"])
                G["acc_hist"].append(acc)
                G["wave_hist"].append(G["wave"])
                if len(G["score_hist"]) > 200:
                    G["score_hist"] = G["score_hist"][-200:]
                    G["acc_hist"]   = G["acc_hist"][-200:]
                    G["wave_hist"]  = G["wave_hist"][-200:]

            # Rebuild chart surface every CHART_EVERY frames
            if frame % CHART_EVERY == 0:
                chart_surf = make_chart_surface(
                    G["score_hist"], G["acc_hist"], G["wave_hist"],
                    G["kill_xs"], G["kill_ys"], PANEL_W, WIN_H-34)

        # Draw game
        game_surf.fill(C_BG)
        stars.draw(game_surf)
        for en in G["enemies"]:   en.draw(game_surf)
        for b  in G["bullets"]:   b.draw(game_surf)
        for pt in G["particles"]: pt.draw(game_surf)
        G["player"].draw(game_surf)
        draw_hud(game_surf, G["score"], G["wave"], G["player"], fb, fs)
        if G["show_wave"]: draw_overlay(game_surf, f"--- WAVE {G['wave']} ---", "GET READY!", fb, fs)
        if G["paused"]:    draw_overlay(game_surf, "--- PAUSED ---", "Press P to Resume", fb, fs)
        if G["over"]:      draw_gameover(game_surf, G["score"], G["wave"], fb, fs)

        # Draw panel
        panel_surf.fill(C_PANEL)
        pygame.draw.rect(panel_surf, (18,18,48), (0,0,PANEL_W,32))
        ht = fp.render("  LIVE DASHBOARD (Matplotlib)", True, C_CYAN)
        panel_surf.blit(ht, (PANEL_W//2-ht.get_width()//2, 9))
        pygame.draw.line(panel_surf, (40,40,90), (0,32),(PANEL_W,32), 1)
        if chart_surf:
            panel_surf.blit(chart_surf, (0, 34))
        else:
            msg  = fs.render("Building charts...", True, C_GREY)
            msg2 = fs.render("(updates every 1.5s)", True, (60,60,90))
            panel_surf.blit(msg,  (PANEL_W//2-msg.get_width()//2,  WIN_H//2-14))
            panel_surf.blit(msg2, (PANEL_W//2-msg2.get_width()//2, WIN_H//2+8))

        # Blit both to window
        ox, oy = shake.offset()
        win.fill((0,0,0))
        win.blit(game_surf,  (ox, oy))
        win.blit(panel_surf, (GAME_W, 0))
        pygame.draw.line(win, (40,40,100), (GAME_W,0),(GAME_W,WIN_H), 2)
        pygame.display.flip()

    pygame.quit()

# ══════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════
if __name__ == "__main__":
    print("Turtle intro -- press ENTER in that window...")
    try:
        turtle_intro()
    except Exception as e:
        print(f"Turtle skipped: {e}")
    print("Launching game + live dashboard in one window...")
    run_game()
    print("Thanks for playing!")
