# written at an hour where thoughts move faster than syntax
# if it glows, its intentional

import cv2, pygame, random, math, numpy as np

# values chosen by instinct not math
w = 640
h = 480
too_bright = 238
spawn_rate = 60
particle_limit = 1500
angle_noise = 0.15
anti_gravity = -0.02

cam = cv2.VideoCapture(0)
pygame.init()
screen = pygame.display.set_mode((w, h))
clock = pygame.time.Clock()

class thing:
    def __init__(self, x, y, cx, cy):
        self.x = x
        self.y = y

        angle = math.atan2(y - cy, x - cx)
        angle += random.uniform(-angle_noise, angle_noise)

        speed = random.uniform(2.0, 8.0)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

        self.life = random.randint(30, 70)
        self.start_life = self.life
        self.size = random.choice([1, 1, 1, 2])

        self.color = random.choice([
            (255, 255, 255),
            (200, 245, 255),
            (255, 215, 245),
            (225, 210, 255),
            (255, 255, 210)
        ])

    def update(self):
        self.dx *= 0.95
        self.dy *= 0.95
        self.dy += anti_gravity

        self.x += self.dx
        self.y += self.dy
        self.life -= 1

    def draw(self, surf):
        alpha = int((self.life / self.start_life) * 255)
        dot = pygame.Surface((self.size, self.size))
        dot.fill(self.color)
        dot.set_alpha(alpha)
        surf.blit(dot, (int(self.x), int(self.y)))

particles = []
running = True

while running:
    ok, frame = cam.read()
    if not ok:
        break

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (w, h))
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, too_bright, 255, cv2.THRESH_BINARY)
    bright = np.argwhere(mask > 0)

    if len(bright) > 0:
        cy, cx = np.mean(bright, axis=0)
        count = min(spawn_rate, particle_limit - len(particles))

        for _ in range(count):
            y, x = bright[random.randint(0, len(bright) - 1)]
            particles.append(thing(float(x), float(y), cx, cy))

    frame_surface = pygame.surfarray.make_surface(rgb.swapaxes(0, 1))
    screen.blit(frame_surface, (0, 0))

    overlay = pygame.Surface((w, h), pygame.SRCALPHA)

    for p in particles[:]:
        p.update()
        if p.life <= 0:
            particles.remove(p)
        else:
            p.draw(overlay)

    screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(60)

cam.release()
pygame.quit()
