import pygame, sys, os, time, re, copy, csv
from pygame.locals import *
from PIL import Image
from settings import *
from stuff import *
from player import Player

def create_map():
    with open("graphics/map/world_map_borders.csv") as world_map_borders:
        for y_index,row in enumerate(world_map_borders):
            row = eval(row)
            y = y_index*scale
            for x_index,i in enumerate(row):# i = map[y_index][x_index] pygame.Rect(x,y,w,h)
                x = x_index*scale
                #test.append(pygame.Rect(x, y, scale, scale))# Test
                if i == 56:
                    w = Object(id=56, map=pygame.Rect(x, y, scale, scale-10), obj_type="border")
                    sprites.append(w)

    with open("graphics/map/world_map_objs.csv") as world_map_objects:
        for y_index,row in enumerate(world_map_objects):
            row = eval(row)
            y = y_index*scale
            for x_index,i in enumerate(row):# i = map[y_index][x_index] pygame.Rect(x,y,w,h)
                x = x_index*scale
                if i == 59:
                    t = Object(id=59, map=pygame.Rect(x, y, scale, scale-10), obj_type="tree")
                    sprites.append(t)
                elif i == 111 and player.map == None:
                    player.map = pygame.Rect(x, y, scale/3, scale/3)
                elif str(i).startswith("3"):
                    for item in items:
                        if i == item.id:
                            item.map.x, item.map.y = x, y
                elif str(i).startswith("2"):
                    for s in sprites:
                        if s.obj_type == "npc":
                            if i == s.id:
                                s.map = pygame.Rect(x, y, scale/2, scale/2)

def draw_map():
    window.blit(world_map_img, (0-player.camera_x, 0-player.camera_y))
    #for t in test:
    #    pygame.draw.rect(window, grey, ((t.x-player.camera_x, t.y-player.camera_y), t.size), 1)
    for s in sorted(sprites, key=lambda s: s.map.centery):
        if s.obj_type == "player" or s.obj_type == "npc":
            s.draw_player(player)
        elif s.obj_type == "tree":
            window.blit(tree_img, (s.map.x-player.camera_x, s.map.y-5-player.camera_y))
            #pygame.draw.rect(window, white, ((s.map.x-player.camera_x, s.map.y-player.camera_y), s.map.size), 1)# Test
    for i in items:
        if i not in player.inventory_map and i.map.x != 0:
            if i.image == None:# ???
                window.blit(item_img, (i.map.x-player.camera_x, i.map.y-player.camera_y))
            else:
                window.blit(i.image, (i.map.x-player.camera_x, i.map.y-player.camera_y))
            #pygame.draw.rect(window, white, ((i.map.x-player.camera_x, i.map.y-player.camera_y), i.map.size), 1)# Test

if __name__ == "__main__":
    pygame.init()
    window = pygame.display.set_mode((screen_width,screen_height), vsync=1)
    pygame.display.set_caption("Game")
    clock = pygame.time.Clock()
    #
    world_map_img = pygame.image.load("graphics/map/world_map.png").convert()
    world_map_rect = world_map_img.get_rect()
    tree_img = pygame.image.load("graphics/map/tiles/arvorinha.png").convert_alpha()
    item_img = pygame.image.load("graphics/item.png").convert_alpha()
    health_potion_img = pygame.image.load("graphics/potion.png").convert_alpha()
    #
    items = []
    with open("items.txt", "r") as file_items:
        for item in file_items:
            items.append(eval(item))
    sprites = []
    player = Player(id=1, health=100, speed=2,
        items=items, body="body_male.png", head="head_hair_blonde.png",
        weapon=301, torso=304, hands=308, legs=305, belt=306, feet=307)
    player.obj_type = "player"
    sprites.append(player)
    with open("npcs.txt", "r") as file_npcs:
        for npc in file_npcs:
            n = eval(npc)
            sprites.append(eval(npc))
    #test = []
    create_map()
    game = True
    while game:
        for event in pygame.event.get():
            if event.type == QUIT:
                game = False
        draw_map()
        if player.health <= 0:
            player.draw_player()
            dead_player_font = pygame.font.Font("freesansbold.ttf", 40)
            dead_text = dead_player_font.render("PLAYER DEAD", True, red)
            window.blit(dead_text, (screen_width//2-100, screen_height//2-100, 200, 100))
        else:
            player.camera(world_map_rect)
            player.keyboard(sprites)
            player.append_items(items)
            if player.inventory_open:player.draw_inventory(sprites)
            for s in sprites:
                if s.obj_type == "npc":
                    s.npc_plus(player)
        pygame.display.flip()
        clock.tick(60)# FPS
    pygame.quit()
    sys.exit()