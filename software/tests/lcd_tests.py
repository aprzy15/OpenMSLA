
import numpy as np
import pygame
import os
import time
from software.config.config_machine import MachineConfig
from pubsub import pub
from software.controller_display import Display
from PIL import Image

# os.environ["DISPLAY"] = ":0"
#
# pygame.display.init()
# screen = pygame.display.set_mode()
# pygame.display.toggle_fullscreen()
# pygame.mouse.set_visible(False)
# clock = pygame.time.Clock()
# print(screen.get_width())
# print(screen.get_height())
#
# screen.fill((255,255,255))
# time.sleep(1)
# screen.fill((0,0,0))
# time.sleep(1)


d = Display(None)
# im = np.full((5760, 3600), 255)
# print(im.shape)
# d.show(im)
# t = 0.5
# time.sleep(t)
im_path ='LCD_test_im.png'
img = np.array(Image.open(im_path)) * 255
img = img.astype('uint8')
print(img.shape)
res = d.show(img)
time.sleep(1)
print(res)
time.sleep(3)
im = np.full((5760, 3600), 0)
print(im.shape)
d.show(im)

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

# screen.fill((0,0,0))
# for i in range(1000):
#     print(i)
#     # pygame.draw.line(screen, (255, 255, 255), (0, 0), (1920, 3600), 1)
#     pulse()
#     # pygame.draw.circle(screen, (255, 255, 255), (960, 1800), 900)
#     pygame.display.flip()
#     clock.tick(1)