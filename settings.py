import pygame

def pil_img_to_surface(pil_img):
    return pygame.image.fromstring(pil_img.tobytes(), pil_img.size, pil_img.mode).convert_alpha()

screen_width, screen_height = 1200, 720
scale = 64

red = (255,0,0)
grey = (100,100,100)
green = (114,140,0)
white = (255,255,255)
brown = (222,184,135)