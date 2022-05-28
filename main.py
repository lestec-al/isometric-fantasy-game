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
            for i in s.inventory:
                persons_items.append(i)
    for obj in all_map_objects:
        with open(all_map_objects[obj]) as file:
            for y_index,row in enumerate(file):
                row = eval(row)
                y = y_index*scale
                for x_index,i in enumerate(row):# pygame.Rect(x,y,w,h)
                    x = x_index*scale
                    if "world_map_borders" in file.name:
                        if i == 0:
                            w = Object(id=0, map=pygame.Rect(x, y, scale, scale-10), obj_type="border")
                            sprites.append(w)
                    elif "world_map_trees" in file.name:
                        if i != -1:
                            if i in [202,203,250,251,253,254]:
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
                                if s.obj_type == "box" and s.map == None:
                                    s.map=pygame.Rect(x, y, scale, scale/2)
    persons_items.clear()

def draw_map():# ???
    window.blit(world_map_img, (0-player.camera_x, 0-player.camera_y))
    for d in dead_npcs:
        d.draw_person(player)
    for s in sorted(sprites, key=lambda s: s.map.centery):
        if s.obj_type == "npc" and s.health <= 0 and s not in dead_npcs:
            dead_npcs.append(s)
        elif s.obj_type == "player" or s.obj_type == "npc" and s.health > 0:
            s.draw_person(player)
            s.add_sounds(sounds)
        elif s.obj_type == "tree":
            window.blit(s.image, (s.map.x-player.camera_x, s.map.y-5-player.camera_y))
        elif s.obj_type == "box":
            box_image = s.image_open if player.box == s else s.image
            window.blit(box_image, (s.map.x-player.camera_x, s.map.y-5-player.camera_y))
        #pygame.draw.rect(window, white, ((s.map.x-player.camera_x, s.map.y-player.camera_y), s.map.size), 1)# Test
    for i in items:
        if i not in player.inventory and i.map.x != 0:
            if i.image == None:# ???
                window.blit(item_img, (i.map.x-player.camera_x, i.map.y-player.camera_y))
            else:
                window.blit(i.image, (i.map.x-player.camera_x, i.map.y-player.camera_y))
        #pygame.draw.rect(window, white, ((i.map.x-player.camera_x, i.map.y-player.camera_y), i.map.size), 1)# Test
    for t in treetops:
        window.blit(t.image, (t.map.x-player.camera_x, t.map.y-5-player.camera_y))

if __name__ == "__main__":
    pygame.init()
    window = pygame.display.set_mode((screen_width,screen_height), vsync=1)
    pygame.display.set_caption("Game")
    clock = pygame.time.Clock()
    # Map graphics
    world_map_img = pygame.image.load("graphics/map/world_map.png").convert()
    world_map_rect = world_map_img.get_rect()
    item_img = pygame.image.load("graphics/item.png").convert_alpha()# ???
    # Items, Images, Player, NPCs
    items = []
    sprites = []
    treetops = []
    sounds = Sounds()
    images = Images()
    for key in items_dict:
        i = items_dict[key]
        if "weapon" in key:
            item = Weapon(i["id"], i["name"], i["obj_type"], images.load(i["image"]), i["anim"], i["damage"], i["cooldown_time"])
        elif "outfit" in key:
            item = Outfit(i["id"], i["name"], i["obj_type"], None, i["anim"], i["armor"])
        elif "potion" in key:
            item = Potion(i["id"], i["name"], i["obj_type"], images.load(i["image"]), i["for_adding"])
        items.append(item)
    i = player_dict
    player = Person(i["id"], i["health"], i["speed"], items, images, i["body"], i["head"],
        i["weapon"], i["torso"], i["hands"], i["legs"], i["belt"], i["feet"], i["behind"], i["sword_skill"], i["spear_skill"])
    player.obj_type = "player"
    sprites.append(player)
    for key in npcs_dict:
        i = npcs_dict[key]
        sprites.append(Person(i["id"], i["health"], i["speed"], items, images, i["body"], i["head"],
        i["weapon"], i["torso"], i["hands"], i["legs"], i["belt"], i["feet"], i["behind"], i["sword_skill"], i["spear_skill"]))
    for key in boxes_dict:
        i = boxes_dict[key]
        box = Box(i["id"], None, i["obj_type"], images.load(i["image"]), images.load(i["image_open"]))
        for item in items:
            if item.id in i["containce"]:
                box.inventory.append(item)
        sprites.append(box)
    create_map()
    dead_npcs = []
    # Main loop
    game = True
    while game:
        for event in pygame.event.get():
            if event.type == QUIT:
                game = False
        draw_map()
        # NPCs methods
        for s in sprites:
            if s.obj_type == "npc" and s.health > 0:
                s.stats_restoration()
                s.draw_npc_stats(player)
                s.npc_movement_attack(player, sprites)
        # Player methods
        if player.health <= 0:
            player.inventory_open = False
            dead_text = pygame.font.Font("freesansbold.ttf", 40).render("PLAYER DEAD", True, red)
            window.blit(dead_text, (screen_width//2-100, screen_height//2-100, 200, 100))
        else:
            player.stats_restoration()
            player.camera(world_map_rect)
            player.keyboard(sprites)
            player.append_items_from_map()
            if player.inventory_open:player.draw_inventory(sprites)
            player.draw_player_stats()
        pygame.display.flip()
        clock.tick(60)# FPS
    pygame.quit()
    sys.exit()