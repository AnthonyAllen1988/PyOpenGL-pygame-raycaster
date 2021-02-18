from math import radians, sin, cos, tan, sqrt

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *


# ------------ Global Variables----------------
mapX = 8
mapY = 8
mapS = 64

px, py, pa, pdx, pdy = 0, 0, 0, 0, 0

screenX = 1024
screenY = 510

level_map = [
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 1, 0, 0, 1, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 1, 0, 0, 1, 0, 1,
    1, 0, 0, 1, 1, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 1,
    1, 1, 1, 1, 1, 1, 1, 1
]


# ----------------- Utility function -----------------
def fix_angle(angle):
    a = angle
    if angle>359:
        a -= 360
    elif angle<0:
        a += 360
    return a


# ---------------- Player ------------------
def draw_player_2d():
    glColor3f(1, 1, 0)
    glPointSize(8)
    glLineWidth(4)

    # Draw Player Point
    glBegin(GL_POINTS)
    glVertex2f(px, py)
    glEnd()

    # Draw Player Direction Line
    glBegin(GL_LINES)
    glVertex2f(px, py)
    glVertex2f(px+pdx*20, py+pdy*20)
    glEnd()


def buttons():
    global px, py, pdx, pdy, pa

    events = pygame.event.get()

    keys = pygame.key.get_pressed()

    for event in events:

        # Quit Game
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # Keyboard input
    # W key
    if keys[K_w]:
        px += pdx*5
        py += pdy*5
    # S key
    if keys[K_s]:
        px -= pdx * 5
        py -= pdy * 5
    # A key
    if keys[K_a]:
        pa += 5
        pa = fix_angle(pa)
        pdx = cos(radians(pa))
        pdy = -sin(radians(pa))
    # D key
    if keys[K_d]:
        pa -= 5
        pa = fix_angle(pa)
        pdx = cos(radians(pa))
        pdy = -sin(radians(pa))


# --------------- Draw Map ---------------------------
def draw_map_2d():
    x, y = 0, 0

    while y < mapY:
        while x < mapX:
            if level_map[y*mapX+x] == 1:
                glColor3f(1, 1, 1)
            else:
                glColor3f(0, 0, 0)
            xo = x*mapS
            yo = y*mapS
            glBegin(GL_QUADS)
            glVertex2i(0 + xo + 1, 0 + yo + 1)
            glVertex2i(0 + xo + 1, mapS + yo - 1)
            glVertex2i(mapS + xo - 1, mapS + yo - 1)
            glVertex2i(mapS + xo - 1, 0 + yo + 1)
            glEnd()
            x += 1
        y += 1
        x = 0


def distance(ax, ay, bx, by, angle):
    return cos(radians(angle))*(bx-ax)-sin(radians(angle))*(by-ay)


# --------------- Raycasting ----------------
def draw_rays_2d():
    # Draw ceiling color
    glColor3f(0, 1, 1)
    glBegin(GL_QUADS)
    glVertex(526, 0)
    glVertex(1006, 0)
    glVertex(1006, 160)
    glVertex(526, 160)
    glEnd()

    # Draw floor color
    glColor3f(0, 0, 1)
    glBegin(GL_QUADS)
    glVertex2i(526, 160)
    glVertex2i(1006, 160)
    glVertex2i(1006, 320)
    glVertex2i(526, 320)
    glEnd()

    r, mx, my, mp, dof, side = 0, 0, 0, 0, 0, 0
    vx, vy, rx, ry, ra, xo, yo, disV, disH = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    # ra is the ray angle
    ra = fix_angle(pa + 30)

    for r in range(0, 60):  # We are drawing total 60 rays, for a 60 degree field of view

        # Vertical
        dof, side, disV = 0, 0, 100000

        Tan = tan(radians(ra))
        if cos(radians(ra)) > 0.001:  # Looking left
            rx = ((int(px) >> 6) << 6) + 64
            ry = (px - rx) * Tan + py
            xo = 64
            yo = -xo * Tan
        elif cos(radians(ra)) < -0.001:  # Looking right
            rx = ((int(px) >> 6) << 6) - 0.001
            ry = (px - rx) * Tan + py
            xo = -64
            yo = -xo * Tan
        else:  # No hit
            rx = px
            ry = py
            dof = 8
        while dof < 8:
            mx = int(rx) >> 6
            my = int(ry) >> 6
            mp = my * mapX + mx
            if mp > 0 and mp < mapX * mapY and level_map[mp] == 1:
                dof = 8
                disV = cos(radians(ra))*(rx-px)-sin(radians(ra))*(ry-py)
            else:
                rx += xo
                ry += yo
                dof += 1
        vx = rx
        vy = ry

        # Horizontal

        dof = 0
        disH = 100000

        # Fix divide by zero
        if Tan == 0:
            Tan += 0.000000000001

        Tan = 1.0 / Tan
        if sin(radians(ra)) > 0.001:  # Looking up
            ry = ((int(py) >> 6) << 6) - 0.0001
            rx = (py - ry) * Tan + px
            yo = -64
            xo = -yo * Tan
        elif sin(radians(ra)) < -0.001:  # Looking down
            ry = ((int(py) >> 6) << 6) + 64
            rx = (py - ry) * Tan + px
            yo = 64
            xo = -yo * Tan
        else: # No hit
            rx = px
            ry = py
            dof = 8

        while dof < 8:
            mx = int(rx) >> 6
            my = int(ry) >> 6
            mp = my * mapX + mx
            if mp > 0 and mp < mapX * mapY and level_map[mp] == 1:
                dof = 8
                disH = cos(radians(ra)) * (rx-px) - sin(radians(ra))*(ry-py)
            else:
                rx += xo
                ry += yo
                dof += 1
        hx, hy = rx, ry

        glColor3f(0, 0.8, 0)
        if (disV < disH):  # If a Vertical wall is hit first
            rx = vx
            ry = vy
            disH = disV
            glColor3f(0, 0.6, 0)

        # Drawing 2D rays
        glLineWidth(2)
        glBegin(GL_LINES)
        glVertex(px, py)
        glVertex(rx, ry)
        glEnd()

        # Drawing 3D scene
        ca = fix_angle(pa - ra)  # Correct fisheye
        disH = disH * cos(radians(ca))
        lineH = mapS * 320 / disH
        if (lineH > 320):
            lineH = 320
        lineOff = 160 - (int(lineH) >> 1)

        glLineWidth(8)
        glBegin(GL_LINES)
        glVertex(r * 8 + 530, lineOff)
        glVertex(r * 8 + 530, lineOff + lineH)
        glEnd()
        # Start next ray
        ra = fix_angle(ra - 1)


# -------------- Initialisation ---------------------------------------
def init():
    glClearColor(0.3, 0.3, 0.3, 0)
    gluOrtho2D(0, screenX, screenY, 0)
    global px, py, pa, pdx, pdy
    px = 150
    py = 400
    pa = 90
    pdx = cos(radians(pa))
    pdy = -sin(radians(pa))


def main():
    pygame.init()
    display = (screenX, screenY)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    init()

    while True:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        buttons()
        draw_map_2d()
        draw_player_2d()
        draw_rays_2d()
        pygame.display.flip()
        pygame.time.wait(10)


main()
