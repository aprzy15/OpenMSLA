
import numpy as np
import pygame
import os
import time


os.environ["DISPLAY"] = ":0"

pygame.display.init()
screen = pygame.display.set_mode()
pygame.display.toggle_fullscreen()
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()
print(screen.get_width())
print(screen.get_height())

screen.fill((255,255,255))
time.sleep(1)
def pulse():
    indices = list(range(0, 900, 4))
    for x in indices:
        pygame.draw.circle(screen, (255, 255, 255), (1000, 1800), x)
        pygame.display.flip()
        clock.tick(30)

    indices.reverse()
    for x in indices:
        screen.fill((0, 0, 0))
        pygame.draw.circle(screen, (255, 255, 255), (1000, 1800), x)
        pygame.display.flip()
        clock.tick(30)


# pygame.draw.circle(screen, (255, 255, 255), (960, 1800), 900)
# pygame.display.flip()
# time.sleep(2.5)

pygame.draw.line(screen, (0, 0, 255), (1001, 0), (1001, 3600), 1)  # H
pygame.draw.line(screen, (255, 0, 0), (1000, 0), (1000, 3600), 1)  # H
pygame.draw.line(screen, (255, 255, 255), (0, 2500), (1500, 2500), 1)  # V
pygame.display.flip()
time.sleep(1)

for i in range(1000):
    print(i)
    # pygame.draw.line(screen, (255, 255, 255), (0, 0), (1920, 3600), 1)
    pulse()
    # pygame.draw.circle(screen, (255, 255, 255), (960, 1800), 900)
    pygame.display.flip()
    clock.tick(1)