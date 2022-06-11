import pygame, sys, random
from pygame.locals import *
from settings import *
from stuff import *
from person import *

def persons_boxes_items():
    p = []
    for s in sprites:
        if s.obj_type == "player" or "npc" in s.obj_type or s.obj_type == "box":
            for i in s.inventory:
                p.append(i)
    return p

def create_copy_item(item):
    var = False
    while var == False:
        var = True
        ri = random.randint(1,200)
        for i in items:
            if item.id + ri == i.id:
                var = False
    if var == True:
        if "weapon" in item.obj_type:
            c_item = Weapon(item.id+ri, item.name, item.obj_type, item.image, item.anim, item.damage, item.cooldown, item.radius)
        elif item.obj_type in ["head", "weapon", "torso", "hands", "legs", "belt", "feet", "behind", "shield"]:
            c_item = Outfit(item.id+ri, item.name, item.obj_type, None, item.anim, item.armor)
        elif "potion" in item.obj_type:
            c_item = Potion(item.id+ri, item.name, item.obj_type, item.image, item.for_adding)
        elif "coins" in item.obj_type:
            c_item = Coins(item.id+ri, item.name, item.obj_type, item.image, item.amount)
        items.append(c_item)
        return item.id+ri, c_item

def create_person(person_type):
    i = persons_s[person_type]
    # Create copy person items
    for key in i:
        if key not in ["id", "health", "speed", "sword_skill", "spear_skill"]:
            for p_item in persons_boxes_items():
                if key == "inventory":
                    for index,inventory_item in enumerate(i["inventory"]):
                        if inventory_item == p_item.id:
                            i["inventory"][index], c_item = create_copy_item(p_item)
                elif type(i[key]) == type(1) and i[key] == p_item.id:
                    i[key], c_item = create_copy_item(p_item)
    # Create copy person (with id)
    for s in sprites:
        if "npc" in s.obj_type and s.id == i["id"]:
                var = False
                while var == False:
                    var = True
                    ri = random.randint(1,20)
                    for s1 in sprites:
                        if "npc" in s.obj_type and s1.id == i["id"] + ri:
                            var = False
                if var == True:
                    i["id"] += ri
    # Create person
    person = Person(i["id"], i["health"], i["speed"], items, images, i["body"], i["hair"], i["head"], i["weapon"],
        i["torso"], i["hands"], i["legs"], i["belt"], i["feet"], i["behind"], i["shield"],
        i["sword_skill"], i["spear_skill"])
    for item in items:
        if item.id in i["inventory"]:
            if item.obj_type == "coins": item.amount = random.randint(10,item.amount)# Randomize coins amount
            person.inventory.append(item)
    sprites.append(person)
    if "player" in person_type:
        person.obj_type = "player"
    elif "trader" in person_type:
        person.obj_type = "npc-trader" 
        person.dialogs = i["dialogs"]
    return person

def create_objects(objects: list):
    for dict in objects:
        for key in dict:
            i = dict[key]
            if dict == items_s:
                if "weapon" in key:
                    item = Weapon(i["id"], i["name"], i["obj_type"], images.load(i["image"]), i["anim"], i["damage"],
                                i["cooldown"], i["radius"])
                elif "outfit" in key:
                    item = Outfit(i["id"], i["name"], i["obj_type"], None, i["anim"], i["armor"])
                elif "potion" in key:
                    item = Potion(i["id"], i["name"], i["obj_type"], images.load(i["image"]), i["for_adding"])
                elif "coins" in key:
                    item = Coins(i["id"], i["name"], i["obj_type"], images.load(i["image"]), i["amount"])
                items.append(item)
            elif dict == boxes_s:
                # Create copy box items
                for p_item in persons_boxes_items():
                    for index,inventory_item in enumerate(i["inventory"]):
                        if inventory_item == p_item.id:
                            i["inventory"][index], c_item = create_copy_item(p_item)
                # Create box
                box = Box(i["id"], None, i["obj_type"], images.load(i["image"]), images.load(i["image_open"]))
                for item in items:
                    if item.id in i["inventory"]:
                        if item.obj_type == "coins": item.amount = random.randint(200,item.amount)# Randomize coins amount
                        box.inventory.append(item)
                sprites.append(box)

def create_map():
    all_map_objects = {
        "world_map_borders":"graphics/map/world_map_borders.csv",
        "world_map_trees":"graphics/map/world_map_trees.csv",
        "world_map_obj":"graphics/map/world_map_obj.csv",}
    for obj in all_map_objects:
        with open(all_map_objects[obj]) as file:
            for y_index,row in enumerate(file):
                row = eval(row)
                y = y_index*scale
                for x_index,i in enumerate(row):
                    x = x_index*scale
                    if "world_map_borders" in file.name:
                        if i == 0:
                            w = Object(id=0, map=pygame.Rect(x, y, scale, scale), obj_type="border")
                            sprites.append(w)
                    elif "world_map_trees" in file.name:
                        if i != -1:
                            if i in [202,203,250,251,253,254]:
                                t = Object(id=i, map=pygame.Rect(x, y, scale, scale-10), obj_type="tree")
                                t.image = images.trees_images[i]
                                sprites.append(t)
                            else:
                                t = Object(id=i, map=pygame.Rect(x, y, scale, scale), obj_type="tree_up")
                                t.image = images.trees_images[i]
                                treetops.append(t)
                    elif "world_map_obj" in file.name:
                        if i == 1:
                            player = create_person("player")
                            player.map = pygame.Rect(x, y, scale/2, scale/2)
                        elif i == 2:
                            ri = random.randint(0,len(items)-1)
                            item = items[ri]
                            if item in persons_boxes_items():
                                id_item, c_item = create_copy_item(item)
                                c_item.map.x, c_item.map.y = x, y
                            else:
                                item.map.x, item.map.y = x, y
                        elif i == 3:
                            enemy = create_person("enemy")
                            enemy.map = pygame.Rect(x, y, scale/2, scale/2)
                        elif i == 4:
                            for s in sprites:
                                if s.obj_type == "box" and s.map == None:
                                    s.map = pygame.Rect(x, y, scale, scale)
                                    s.map.inflate_ip(0,-10)
                        elif i == 5:
                            trader = create_person("trader")
                            trader.map = pygame.Rect(x, y, scale/2, scale/2)
                            trader.capacity = 30
    return player

def draw_map():
    sounds.play_map_sounds()
    window.blit(world_map_img, (0-player.camera_x, 0-player.camera_y))
    for d in dead_npcs:
        d.draw_person(player)
    for i in items:
        if i not in player.inventory and i.map.x != 0:
            if i.image == None:
                window.blit(item_img, (i.map.x-player.camera_x, i.map.y-player.camera_y))
            else:
                window.blit(i.image, (i.map.x-player.camera_x, i.map.y-player.camera_y))
    for s in sorted(sprites, key=lambda s: s.map.centery):
        if s not in dead_npcs and "npc" in s.obj_type and s.health <= 0:
            dead_npcs.append(s)
        elif s.obj_type == "player" or "npc" in s.obj_type and s.health > 0:
            s.draw_person(player)
            s.play_sounds(sounds)
        elif s.obj_type == "tree":
            window.blit(s.image, (s.map.x-player.camera_x, s.map.y-5-player.camera_y))
        elif s.obj_type == "box":
            box_image = s.image_open if player.box == s else s.image
            window.blit(box_image, (s.map.x-player.camera_x, s.map.y-5-player.camera_y))
    for t in treetops:
        window.blit(t.image, (t.map.x-player.camera_x, t.map.y-5-player.camera_y))

if __name__ == "__main__":
    pygame.init()
    window = pygame.display.set_mode((screen_width,screen_height), vsync=1)
    pygame.display.set_caption("Game")
    clock = pygame.time.Clock()
    # Map, objects
    world_map_img = pygame.image.load("graphics/map/world_map.png").convert()
    world_map_rect = world_map_img.get_rect()
    sounds, images = Sounds(), Images()
    item_img = images.load("graphics/item.png")
    items, sprites, treetops, dead_npcs = [], [], [], []
    create_objects([items_s, boxes_s])
    player = create_map()
    # Main loop
    game = True
    while game:
        for event in pygame.event.get():
            if event.type == QUIT:
                game = False
        draw_map()
        # NPCs
        for s in sprites:
            if "npc" in s.obj_type and s.health > 0:
                s.stats_restoration()
                s.draw_npc_stats(player)
                if "enemy" in s.obj_type:
                    s.npc_move_attack(player, sprites)
                elif "trader" in s.obj_type:
                    s.draw_npc_dialogs(player)
                    if s.under_attack_time != None:
                        s.obj_type = "npc-enemy"
        # Player
        if player.health <= 0:
            player.inventory_open = False
            dead_text = pygame.font.Font("freesansbold.ttf", 40).render("PLAYER DEAD", True, red)
            window.blit(dead_text, (screen_width//2-100, screen_height//2-100, 200, 100))
        else:
            player.clean_showing_item()
            player.keyboard(sprites)
            if player.inventory_open:
                player.draw_inventory(sprites)
            player.draw_player_stats()
            player.stats_restoration()
            player.camera(world_map_rect)
        pygame.display.flip()
        clock.tick(60)# FPS
    pygame.quit()
    sys.exit()