# -coding utf-8 -
# import pygame and sys
import pygame as pg
import math
import sys

# Initialize Pygame
pg.init()

# Set up the screen
screen = pg.display.set_mode((800, 500))  # Fixed screen size
pg.display.set_caption("Billiards", "4.0")

# Color definitions
white = (236, 240, 241)
gray = (123, 125, 125)
stage = (51, 51, 51)
colors = ["yellow", "blue", "red", "purple", "orange", "green", "brown", "black", 
          "yellow", "blue", "red", "purple", "orange", "green", "brown", "white"]

# Ball class
class Ball:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vx = 0
        self.vy = 0
        self.mass = 1

    def apply_force(self, fx, fy):
        # Update velocity based on applied force
        self.vx += fx / self.mass
        self.vy += fy / self.mass

    def update(self):
        # Update position based on velocity
        self.x += self.vx
        self.y += self.vy
        # Simulate friction
        self.vx *= 0.99
        self.vy *= 0.99

        # Boundary detection and reflection
        if self.x - self.radius < 10 or self.x + self.radius > 790:
            self.vx = -self.vx * 0.9  # Reflect and reduce velocity
            self.x = max(self.radius + 10, min(self.x, 790 - self.radius))
        if self.y - self.radius < 10 or self.y + self.radius > 490:
            self.vy = -self.vy * 0.9  # Reflect and reduce velocity
            self.y = max(self.radius + 10, min(self.y, 490 - self.radius))

    def draw(self, screen):
        # Draw the ball on the screen
        pg.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# Create balls and holes
balls = []
holes = [(20, 20), (400, 20), (780, 20), (20, 480), (400, 480), (780, 480)]

def create_balls():
    global balls
    start_x, start_y = 150, 250
    spacing = 20
    rows = 5
    for row in range(rows):
        for i in range(row + 1):
            x = start_x + row * spacing
            y = start_y - row * spacing / 2 + i * spacing
            color = pg.Color(colors[len(balls)])
            balls.append(Ball(x, y, 10, color))
    # Add the white ball
    balls.append(Ball(450, 250, 10, pg.Color("white")))

create_balls()

# Detect if balls fall into holes
def check_holes():
    global balls
    for hole in holes:
        for ball in balls[:]:
            dx = ball.x - hole[0]
            dy = ball.y - hole[1]
            if math.sqrt(dx**2 + dy**2) < 20:
                balls.remove(ball)

# Detect collision between two balls
def detect_collision(ball1, ball2):
    dx = ball2.x - ball1.x
    dy = ball2.y - ball1.y
    distance = math.sqrt(dx**2 + dy**2)
    return distance <= ball1.radius + ball2.radius

# Resolve collision between two balls
def resolve_collision(ball1, ball2):
    dx = ball2.x - ball1.x
    dy = ball2.y - ball1.y
    distance = math.sqrt(dx**2 + dy**2)
    if distance == 0:
        return

    # Normal vector
    nx = dx / distance
    ny = dy / distance

    # Relative velocity
    rvx = ball2.vx - ball1.vx
    rvy = ball2.vy - ball1.vy

    # Velocity along the normal
    vel_along_normal = rvx * nx + rvy * ny
    if vel_along_normal > 0:
        return

    # Compute impulse
    restitution = 0.9
    impulse = -(1 + restitution) * vel_along_normal
    impulse /= (1 / ball1.mass + 1 / ball2.mass)

    # Apply impulse
    ball1.vx -= impulse * nx / ball1.mass
    ball1.vy -= impulse * ny / ball1.mass
    ball2.vx += impulse * nx / ball2.mass
    ball2.vy += impulse * ny / ball2.mass

# Draw the cue stick
def cue():
    # Check if the white ball is stationary
    staticFlag = 1
    for ball in balls:
        if abs(ball.vx) > 0.1 or abs(ball.vy) > 0.1:
            staticFlag = 0
    
    # Show the cue stick if the white ball is stationary
    white_ball = balls[-1]
    if staticFlag == 1:
        mPos = pg.mouse.get_pos()
        dx = mPos[0] - white_ball.x
        dy = mPos[1] - white_ball.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            # Calculate the back end of the cue stick
            angle = math.atan2(dy, dx)
            cue_length = min(150, distance)
            cue_x = white_ball.x - math.cos(angle) * cue_length
            cue_y = white_ball.y - math.sin(angle) * cue_length
            # Draw the cue stick
            pg.draw.line(screen, (249, 231, 159), (cue_x, cue_y), (white_ball.x, white_ball.y), 5)

        # Apply force to the white ball on mouse click
        if pg.mouse.get_pressed()[0]:
            force = min(distance / 10, 10)
            white_ball.apply_force(-force * dx / distance, -force * dy / distance)

# Main loop
fps = pg.time.Clock()
running = True

while running:
    dt = fps.tick(60) / 1000
    mouse_pos = pg.mouse.get_pos()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    # Update the positions of the balls
    for ball in balls:
        ball.update()

    # Detect collisions
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            if detect_collision(balls[i], balls[j]):
                resolve_collision(balls[i], balls[j])

    # Check if balls fall into holes
    check_holes()

    # Draw the scene
    screen.fill(white)
    pg.draw.line(screen, gray, (0, 250), (800, 250), 500)
    pg.draw.line(screen, stage, (20, 250), (780, 250), 460)
    for hole in holes:
        pg.draw.circle(screen, gray, hole, 20)
    for ball in balls:
        ball.draw(screen)

    # Draw the cue stick
    cue()

    # Update the display
    pg.display.flip()

pg.quit()
sys.exit()
