import pygame, sys
from pygame.locals import *
from settings import *
from stuff import *
from person import *

def create_map():
    all_map_objects = {
        "world_map_borders":"graphics/map/world_map_borders.csv",
        "world_map_trees":"graphics/map/world_map_trees.csv",
        "world_map_obj":"graphics/map/world_map_obj.csv",}
    persons_items = []
    for s in sprites:
        if s.obj_type == "player" or s.obj_type == "npc":
            for i in s.inventory_map:
                persons_items.append(i)
    for obj in all_map_objects:
        with open(all_map_objects[obj]) as file:
            for y_index,row in enumerate(file):
                row = eval(row)
                y = y_index*scale
                for x_index,i in enumerate(row):# pygame.Rect(x,y,w,h)
                    x = x_index*scale
                    #test.append(pygame.Rect(x, y, scale, scale))# Test
                    if "world_map_borders" in file.name:
                        if i == 0:
                            w = Object(id=0, map=pygame.Rect(x, y, scale, scale-10), obj_type="border")
                            sprites.append(w)
                    elif "world_map_trees" in file.name:
                        if i != -1:
                            if i in [202,203,250,251,253,254,237,238]:
                                t = Object(id=i, map=pygame.Rect(x, y, scale, scale-10), obj_type="tree")
                                t.image = images.terrain_images[i]
                                sprites.append(t)
                            else:
                                t = Object(id=i, map=pygame.Rect(x, y, scale, scale-10), obj_type="tree_up")
                                t.image = images.terrain_images[i]
                                treetops.append(t)
                    elif "world_map_obj" in file.name:
                        if i == 1 and player.map == None:
                            player.map = pygame.Rect(x, y, scale/2, scale/2)
                        elif i == 2:
                            for item in items:
                                if item not in persons_items and item.map.x == 0 and item.map.y == 0:
                                    item.map.x, item.map.y = x, y
                                    break
                        elif i == 3:
                            for s in sprites:
                                if s.obj_type == "npc" and s.map == None:
                                    s.map = pygame.Rect(x, y, scale/2, scale/2)
                                    break
                        elif i == 4:
                            for s in sprites:
                                if s.obj_type == "storage" and s.map == None:
                                    s.map=pygame.Rect(x, y, scale, scale/2)
    persons_items.clear()

def draw_map():
    window.blit(world_map_img, (0-player.camera_x, 0-player.camera_y))
    #for t in test:
    #    pygame.draw.rect(window, grey, ((t.x-player.camera_x, t.y-player.camera_y), t.size), 1)
    for s in sorted(sprites, key=lambda s: s.map.centery):
        if s.obj_type == "player" or s.obj_type == "npc":
            s.draw_person(player)
            #pygame.draw.rect(window, white, ((s.map.x-player.camera_x, s.map.y-player.camera_y), s.map.size), 1)# Test
        elif s.obj_type == "tree":
            window.blit(s.image, (s.map.x-player.camera_x, s.map.y-5-player.camera_y))
            #pygame.draw.rect(window, white, ((s.map.x-player.camera_x, s.map.y-player.camera_y), s.map.size), 1)# Test
        elif s.obj_type == "storage":
            window.blit(s.image, (s.map.x-player.camera_x, s.map.y-5-player.camera_y))
            #pygame.draw.rect(window, white, ((s.map.x-player.camera_x, s.map.y-player.camera_y), s.map.size), 1)# Test
    for i in items:
        if i not in player.inventory_map and i.map.x != 0:
            if i.image == None:# ???
                window.blit(item_img, (i.map.x-player.camera_x, i.map.y-player.camera_y))
            else:
                window.blit(i.image, (i.map.x-player.camera_x, i.map.y-player.camera_y))
            #pygame.draw.rect(window, white, ((i.map.x-player.camera_x, i.map.y-player.camera_y), i.map.size), 1)# Test
    for t in treetops:
        window.blit(t.image, (t.map.x-player.camera_x, t.map.y-5-player.camera_y))

def add_armor_labels():# ???
    for i in items:
        if i.image == None:
            if "plate" in i.anim:
                a = "4"
            elif "leather" in i.anim:
                a = "2"
            elif "chain" in i.anim:
                a = "3"
            elif "robe" in i.anim:
                a = "1"
            if i.obj_type == "head":
                i.image = images.label_armor_images[a][0]
            elif i.obj_type == "torso":
                i.image = images.label_armor_images[a][1]
            elif i.obj_type == "hands":
                i.image = images.label_armor_images[a][2]
            elif i.obj_type == "legs":
                i.image = images.label_armor_images[a][3]
            elif i.obj_type == "feet":
                i.image = images.label_armor_images[a][4]

def load_image(image_path):
    return pygame.image.load(image_path).convert_alpha()

def add_items_storage():# ???
    persons_items = []
    for s in sprites:
        if s.obj_type == "player" or s.obj_type == "npc":
            for i in s.inventory_map:
                persons_items.append(i)
    for item in items:
        for s in sprites:
            if s.obj_type == "storage":
                if item not in persons_items and item.map.x == 0 and item.map.y == 0 and item not in s.inventory_map:
                    s.inventory_map.append(item)
    persons_items.clear()

if __name__ == "__main__":
    pygame.init()
    window = pygame.display.set_mode((screen_width,screen_height), vsync=1)
    pygame.display.set_caption("Game")
    clock = pygame.time.Clock()
    # Map graphics
    world_map_img = pygame.image.load("graphics/map/world_map.png").convert()
    world_map_rect = world_map_img.get_rect()
    item_img = pygame.image.load("graphics/item.png").convert_alpha()# ??????
    # Items, Images, Player, NPCs
    items = []
    sprites = []
    treetops = []
    for key in items_dict:
        i = items_dict[key]
        if "weapon" in key:
            item = Weapon(i["id"], i["name"], i["obj_type"], load_image(i["image"]), i["anim"], i["damage"], i["cooldown_time"])
        elif "outfit" in key:
            item = Outfit(i["id"], i["name"], i["obj_type"], None, i["anim"], i["armor"])
        elif "potion" in key:
            item = Potion(i["id"], i["name"], i["obj_type"], load_image(i["image"]), i["for_adding"])
        items.append(item)
    images = Images()
    add_armor_labels()# ???
    player = Person(id=1, health=100, speed=2, items=items, images=images, body="body_male.png", head="head_hair_blonde.png",
        weapon=300, torso=320, hands=324, legs=321, belt=322, feet=323)
    player.obj_type = "player"
    sprites.append(player)
    for key in npcs_dict:
        i = npcs_dict[key]
        sprites.append(Person(i["id"], i["health"], i["speed"], items, images, i["body"], i["head"],
            i["weapon"], i["torso"], i["hands"], i["legs"], i["belt"], i["feet"], i["behind"], i["sword_skill"], i["spear_skill"]))
    for key in chests_dict:
        i = chests_dict[key]
        sprites.append(Storage(i["id"], None, i["obj_type"], load_image(i["image"])))
    #test = []
    create_map()
    add_items_storage()
    # Main loop
    game = True
    while game:
        for event in pygame.event.get():
            if event.type == QUIT:
                game = False
        draw_map()
        # NPCs methods
        for s in sprites:
            if s.obj_type == "npc":
                s.health_energy_restoration()
                s.draw_npc_stats(player)
                s.npc_movement_attack(player, sprites)
        # Player methods
        if player.health <= 0:
            player.inventory_open = False
            player.draw_person(player)
            dead_text = pygame.font.Font("freesansbold.ttf", 40).render("PLAYER DEAD", True, red)
            window.blit(dead_text, (screen_width//2-100, screen_height//2-100, 200, 100))
        else:
            player.draw_player_stats()
            player.health_energy_restoration()
            player.camera(world_map_rect)
            player.keyboard(sprites)
            player.append_items()
            if player.inventory_open:player.draw_inventory(sprites)
        pygame.display.flip()
        clock.tick(60)# FPS
    pygame.quit()
    sys.exit()