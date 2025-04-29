import pygame as pg
import sys
import math
import random
from settings import *

def load_assets():
    bg      = pg.image.load("Resources/Sky.png").convert_alpha()
    earth   = pg.image.load("Resources/earth.png").convert_alpha()
    grass   = pg.image.load("Resources/grass.png").convert_alpha()
    bunker  = pg.image.load("Resources/bunker.png").convert_alpha()
    fence   = pg.image.load("Resources/fence.png").convert_alpha()
    aim     = pg.image.load("Resources/aim.png").convert_alpha()
    aim_c   = pg.image.load("Resources/aimClick.png").convert_alpha()
    gun     = pg.image.load("Resources/gun.png").convert_alpha()
    bomber_img = pg.image.load("Resources/bomber.png").convert_alpha()
    return bg, earth, grass, bunker, fence, aim, aim_c, gun, bomber_img


def draw_dotted_line(surf, color, p1, p2, width, spacing):
    start, end = pg.Vector2(p1), pg.Vector2(p2)
    direction = (end - start).normalize() if (end - start).length() else pg.Vector2()
    length = (end - start).length()
    for i in range(0, int(length), spacing * 2):
        seg_s = start + direction * i
        seg_e = start + direction * min(i + spacing, length)
        pg.draw.line(surf, color, seg_s, seg_e, width)


def draw_reload_bar(screen, rt):
    x, y = SCREEN_WIDTH - 120, SCREEN_HEIGHT - 30
    pg.draw.rect(screen, (50, 50, 50), (x, y, 100, 10))
    fill = 100 if rt <= 0 else 100 * (1 - rt / RELOAD_TIME)
    pg.draw.rect(screen, (0, 255, 0), (x, y, fill, 10))


def draw_health_bar(scr, h):
    x, y = 20, 20
    pg.draw.rect(scr, HEALTH_COLOR_BG, (x, y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
    pg.draw.rect(scr, HEALTH_COLOR_FILL, (x, y, HEALTH_BAR_WIDTH * (h / 100), HEALTH_BAR_HEIGHT))


def draw_score(scr, sc):
    f = pg.font.Font(None, 36)
    t = f.render(f"Score: {sc}", True, (255, 255, 255))
    scr.blit(t, (20, SCREEN_HEIGHT - 40))


class Particle:
    def __init__(self, pos):
        self.pos = pg.Vector2(pos)
        angle = random.uniform(0, math.tau)
        speed = random.uniform(PARTICLE_SPEED_MIN, PARTICLE_SPEED_MAX)
        self.vel = pg.Vector2(math.cos(angle), math.sin(angle)) * speed
        self.lifetime = PARTICLE_LIFETIME

    def update(self, dt):
        self.pos += self.vel * dt
        self.lifetime -= dt

    def draw(self, screen):
        alpha = max(0, min(255, int(255 * (self.lifetime / PARTICLE_LIFETIME))))
        surf = pg.Surface((PARTICLE_RADIUS*2, PARTICLE_RADIUS*2), pg.SRCALPHA)
        pg.draw.circle(surf, (255, 150, 0, alpha), (PARTICLE_RADIUS, PARTICLE_RADIUS), PARTICLE_RADIUS)
        screen.blit(surf, (self.pos.x - PARTICLE_RADIUS, self.pos.y - PARTICLE_RADIUS))


class SmokeParticle:
    def __init__(self, pos):
        self.pos = pg.Vector2(pos)
        angle = random.uniform(0, math.tau)
        speed = random.uniform(SMOKE_SPEED_MIN, SMOKE_SPEED_MAX)
        self.vel = pg.Vector2(math.cos(angle), math.sin(angle)) * speed
        self.lifetime = SMOKE_LIFETIME

    def update(self, dt):
        self.pos += self.vel * dt
        self.lifetime -= dt

    def draw(self, screen):
        alpha = max(0, min(200, int(200 * (self.lifetime / SMOKE_LIFETIME))))
        radius = SMOKE_RADIUS
        surf = pg.Surface((radius*2, radius*2), pg.SRCALPHA)
        pg.draw.circle(surf, (*SMOKE_COLOR, alpha), (radius, radius), radius)
        screen.blit(surf, (self.pos.x - radius, self.pos.y - radius))


class Bomber:
    def __init__(self, speed, kind, image):
        self.original_image = image
        self.image = image
        self.smoke_timer = 0.0

        if random.choice([True, False]):
            # left to right
            self.image = self.original_image
            x = -self.image.get_width()
            self.vel = pg.Vector2(speed, 0)
            self.direction = "right"
        else:
            # right to left
            self.image = pg.transform.flip(self.original_image, True, False)
            x = SCREEN_WIDTH + self.image.get_width()
            self.vel = pg.Vector2(-speed, 0)
            self.direction = "left"


        y = random.randint(0, SCREEN_HEIGHT//2 - self.image.get_height())
        self.rect = self.image.get_rect(topleft=(x, y))

        self.drop_timer = random.uniform(BOMB_DROP_TIME_MIN, BOMB_DROP_TIME_MAX)
        self.alive = True
        self.exploding = False
        self.explosion_timer = 0.0
        self.particles = []
        
    def update(self, dt, smoke_list):
        if self.alive:
            self.rect.x += int(self.vel.x * dt)
            self.rect.y += int(self.vel.y * dt)

            # Emit smoke trail at intervals
            self.smoke_timer -= dt
            if self.smoke_timer <= 0:
                if self.direction == "right":
                    smoke_list.append(SmokeParticle(self.rect.midleft))
                else:
                    smoke_list.append(SmokeParticle(self.rect.midright))

                self.smoke_timer = 0.05  # emit every 0.05 seconds

            # Only decrease drop timer if within drop zone
            if 200 <= self.rect.centerx <= 800:
                self.drop_timer -= dt

        elif self.exploding:
            if not self.particles:
                for _ in range(PARTICLE_COUNT):
                    self.particles.append(Particle(self.rect.center))

            for p in self.particles:
                p.update(dt)

            self.explosion_timer += dt
            if self.explosion_timer >= EXPLOSION_DURATION:
                self.exploding = False


    def draw(self, screen):
        if self.alive:
            screen.blit(self.image, self.rect)
        elif self.exploding:
            for p in self.particles:
                if p.lifetime > 0:
                    p.draw(screen)

    def drop_bomb(self):
        x = self.rect.centerx
        y = self.rect.bottom
        return pg.Vector2(x, y)


class Bomb:
    def __init__(self, pos, speed):
        self.pos = pg.Vector2(pos)
        self.vel = pg.Vector2(0, speed)

    def update(self, dt):
        self.pos += self.vel * dt

    def draw(self, screen):
        pg.draw.circle(screen, (0, 0, 0), (int(self.pos.x), int(self.pos.y)), BOMB_RADIUS)


def show_game_over(scr):
    ov = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
    ov.fill((0, 0, 0, 180))
    scr.blit(ov, (0, 0))
    f = pg.font.Font(None, 72)
    t = f.render("GAME OVER", True, (200, 50, 50))
    r = t.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
    scr.blit(t, r)
    bf = pg.font.Font(None, 48)
    bt = bf.render("Play Again", True, (255, 255, 255))
    br = bt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
    pg.draw.rect(scr, (50, 50, 50), br.inflate(20, 20))
    scr.blit(bt, br)
    pg.display.flip()
    return br


def draw_scene(scr, bg, earth, grass, bunker, fence, aim_img, gun_rot,
               bg_r, earth_r, grass_r, bunker_r, fence_r, aim_r, gun_r,
               pivot, aim_end, proj, bmbs, bms, rt, sc, hl, parts, smoke):
    # draw background layers
    scr.blit(bg, bg_r)
    scr.blit(earth, earth_r)
    scr.blit(grass, grass_r)

    # draw aiming line and gun
    draw_dotted_line(scr, AIM_LINE_COLOR, pivot, aim_end, AIM_LINE_WIDTH, DOT_SPACING)
    scr.blit(gun_rot, gun_r)
    scr.blit(bunker, bunker_r)
    scr.blit(fence, fence_r)
    scr.blit(aim_img, aim_r)

    # draw projectiles
    for pos, vel in proj:
        pg.draw.circle(scr, PROJECTILE_COLOR, (int(pos.x), int(pos.y)), PROJECTILE_RADIUS)

    # draw bombers
    for b in bmbs:
        b.draw(scr)

    # draw bombs
    for bm in bms:
        bm.draw(scr)

    # draw explosion particles
    for p in parts:
        p.draw(scr)

    # draw smoke
    for s in smoke:
        s.draw(scr)

    # draw UI (reload, score, health)
    draw_reload_bar(scr, rt)
    draw_score(scr, sc)
    draw_health_bar(scr, hl)

    # flip to screen
    pg.display.flip()



def main():
    pg.init()
    pg.mixer.init()

    scr = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("Hit It")
    clk = pg.time.Clock()

    health = 100
    score = 0
    rt = 0.0
    st = 0.0
    proj = []
    bmbs = []
    bms = []
    parts = []
    smoke = []

    pg.mouse.set_visible(False)

    bg, earth, grass, bunker, fence, aim, aim_c, gun, bomber_img = load_assets()

    pg.mixer.music.load("Resources/background_music.mp3")  # adjust the path if needed
    pg.mixer.music.set_volume(0.3)  # volume: 0.0 to 1.0
    pg.mixer.music.play(-1)  # -1 loops the music forever

    shoot_sound = pg.mixer.Sound("Resources/shooting_sound.mp3")
    explode_sound = pg.mixer.Sound("Resources/explosion.mp3")
    bomb_drop_sound = pg.mixer.Sound("Resources/falling.mp3")



    bg_r = bg.get_rect()
    earth_r = earth.get_rect(topleft=(0, 0))
    grass_r = grass.get_rect()
    bunker_r = bunker.get_rect(topleft=(SCREEN_WIDTH//2 - 75, 675))
    fence_r = fence.get_rect()
    fence_r.bottom = SCREEN_HEIGHT
    ground_y = bunker_r.bottom - 30   # changes
    pivot = pg.Vector2(SCREEN_WIDTH//2, 735)

    running = True
    game_over = False

    while running:
        dt = clk.tick(FPS) / 1000.0
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            elif game_over and e.type == pg.MOUSEBUTTONDOWN and e.button == 1 and play_btn.collidepoint(e.pos):
                health = 100
                score = 0
                rt = 0.0
                st = 0.0
                proj.clear()
                bmbs.clear()
                bms.clear()
                parts.clear()
                smoke.clear()
                game_over = False
                pg.mouse.set_visible(False)
        
        if not game_over:
            rt = max(0, rt - dt)
            st = max(0, st - dt)

            if health <= 0:
                pg.mixer.music.stop()

            if not game_over:
                rt = max(0, rt - dt)
                st = max(0, st - dt)

            # spawn bombers using correct speed
            if st <= 0:
                kind = random.randint(1, 5)
                bmbs.append(Bomber(BOMBER_SPEED + kind * 10, kind, bomber_img))
                st = max(1.0, BOMBER_SPAWN_TIME - score * 0.02)

            mb = pg.mouse.get_pressed()
            aim_img = aim_c if mb[0] else aim
            aim_r = aim_img.get_rect(center=pg.mouse.get_pos())

            mx, my = pg.mouse.get_pos()
            raw_angle = math.degrees(math.atan2(-(mx - pivot.x), -(my - pivot.y)))
            ga = max(-90, min(90, raw_angle))
            gun_rend = pg.transform.rotozoom(gun, ga, 1.0)
            off = pg.Vector2(0, 50).rotate(-ga)
            gun_r = gun_rend.get_rect(center=(pivot - off))
            aim_end = pivot + pg.Vector2(0, -1).rotate(-ga) * AIM_LINE_LENGTH

            if mb[0] and rt <= 0:
                proj.append((pg.Vector2(pivot), pg.Vector2(0, -1).rotate(-ga) * PROJECTILE_SPEED))
                rt = RELOAD_TIME
                shoot_sound.play()  # Play shoot sound

            # update projectiles & smoke
            new_proj = []
            for pos, vel in proj:
                pos += vel * dt
                new_proj.append((pos, vel))
                smoke.append(SmokeParticle(pos.copy()))
            proj = [p for p in new_proj if 0 <= p[0].x <= SCREEN_WIDTH and 0 <= p[0].y <= SCREEN_HEIGHT]

            # update bombers & drop bombs
            for b in bmbs:
                b.update(dt, smoke)
                # drop when timer expires
                if b.alive and b.drop_timer <= 0:
                    speed = BOMB_INITIAL_SPEED + score * BOMB_SPEED_FACTOR
                    bms.append(Bomb(b.drop_bomb(), speed))
                    bomb_drop_sound.play()
                    b.drop_timer = random.uniform(BOMB_DROP_TIME_MIN, BOMB_DROP_TIME_MAX)

            # update bombs & collisions
            new_bms = []
            for bm in bms:
                bm.update(dt)
                smoke.append(SmokeParticle(bm.pos.copy()))

                hit = False
                for i, (p_pos, _) in enumerate(proj):
                    if p_pos.distance_to(bm.pos) < PROJECTILE_RADIUS + BOMB_RADIUS:
                        hit = True
                        explode_sound.play()
                        for _ in range(PARTICLE_COUNT):
                            parts.append(Particle(bm.pos))
                        del proj[i]
                        break
                if hit:
                    continue

                if bm.pos.y >= ground_y:
    # spawn ground-impact particles at (bomb.x, ground_y)
                    for _ in range(PARTICLE_COUNT):
                        parts.append(Particle((bm.pos.x, ground_y)))
                        explode_sound.play()
                    health -= random.randint(1, 20)
                    if health <= 0:
                        game_over = True
                        pg.mouse.set_visible(True)
                else:
                    new_bms.append(bm)
            bms = new_bms

            # projectile hits bomber
            for b in bmbs:
                if b.alive:
                    for i, (p_pos, _) in enumerate(proj):
                        if b.rect.collidepoint(p_pos):
                            explode_sound.play()
                            b.alive = False
                            for _ in range(PARTICLE_COUNT):
                                parts.append(Particle(b.rect.center))
                            score += 1
                            del proj[i]
                            break
            bmbs = [b for b in bmbs if b.alive or b.exploding]

            # update particles & smoke
            for p in parts:
                p.update(dt)
            parts = [p for p in parts if p.lifetime > 0]

            for s in smoke:
                s.update(dt)
            smoke = [s for s in smoke if s.lifetime > 0]

            draw_scene(scr, bg, earth, grass, bunker, fence, aim_img, gun_rend,
                       bg_r, earth_r, grass_r, bunker_r, fence_r, aim_r, gun_r,
                       pivot, aim_end, proj, bmbs, bms, rt, score, health, parts, smoke)
        else:
            play_btn = show_game_over(scr)

    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()
