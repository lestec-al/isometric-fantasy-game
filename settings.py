import pygame, os
from PIL import Image

screen_width, screen_height = 1200, 720
scale = 32

red = (255,0,0)
orange = (255,165,0)
grey = (100,100,100)
green = (114,140,0)
white = (255,255,255)
brown = (222,184,135)

npcs_dict = {
    "person1":{"id":200, "health":25, "speed":1, "body":'body_skeleton.png', "head":None, "weapon":301, "torso":None, "hands":None,
                "legs":None, "belt":None, "feet":None, "behind":None, "sword_skill":1, "spear_skill":1},
}
items_dict = {
    "weapon1":{"id":300, "name":"Sword", "obj_type":"weapon", "image":"graphics/sword.png", "anim":"weapon_sword.png", "damage":10, "cooldown_time":2},
    "weapon2":{"id":301, "name":"Good sword", "obj_type":"weapon", "image":"graphics/sword2.png", "anim":"weapon_sword.png", "damage":15, "cooldown_time":2},
    "weapon3":{"id":302, "name":"Staff", "obj_type":"weapon", "image":"graphics/staff.png", "anim":"weapon_staff.png", "damage":10, "cooldown_time":4},
    "weapon4":{"id":303, "name":"Spear", "obj_type":"weapon", "image":"graphics/spear.png", "anim":"weapon_spear.png", "damage":20, "cooldown_time":4},
    "outfit1":{"id":320, "name":"Brown shirt", "obj_type":"torso", "image":None, "anim":"torso_robe_shirt_brown.png", "armor":0.5},
    "outfit2":{"id":321, "name":"Brown skirt", "obj_type":"legs", "image":None, "anim":"legs_robe_skirt.png", "armor":0.2},
    "outfit3":{"id":322, "name":"Robe belt", "obj_type":"belt", "image":None, "anim":"belt_rope.png", "armor":0.2},
    "outfit4":{"id":323, "name":"Brown shoes", "obj_type":"feet", "image":None, "anim":"feet_shoes_brown.png", "armor":0.2},
    "outfit5":{"id":324, "name":"Armor gloves", "obj_type":"hands", "image":None, "anim":"hands_plate_armor_gloves.png", "armor":0.2},
    "outfit6":{"id":325, "name":"Chain armor", "obj_type":"torso", "image":None, "anim":"torso_chain_armor_torso.png", "armor":1.0},
    "potion1":{"id":360, "name":"Health potion 50", "obj_type":"health_potion", "image":"graphics/potion_h.png", "for_adding":50},
    "potion2":{"id":361, "name":"Energy potion 50", "obj_type":"energy_potion", "image":"graphics/potion_e.png", "for_adding":50},
}
chests_dict = {
    "storage1":{"id":500, "obj_type":"storage", "image":"graphics/chest.png"},
}

class Images():
    def __init__(self):
        self.terrain_images = []
        self.label_armor_images = {}# ???
        self.player_images = {
            "bow":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}},
            "hurt":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}},
            "slash":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}},
            "spellcast":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}},
            "thrust":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}},
            "walkcycle":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}}}
        self.add_player_images()
        self.add_label_armor_images()# ???
        self.add_terrain_images()

    def add_terrain_images(self):
        i = Image.open(f"graphics/map/wood_tileset.png")
        width, height = i.width, i.height
        w, h = int(width/32), int(height/32)
        left, upper, right, lower = 0, 0, 32, 32
        r_i = 0
        for _ in range(h):
            c_i = 0
            for _ in range(w):
                image = i.crop((left+c_i, upper+r_i, right+c_i, lower+r_i))
                img = self.pil_img_to_surface(image)
                self.terrain_images.append(img)
                c_i += 32
            r_i += 32

    def add_player_images(self):
        for folder in os.listdir("graphics/player/"):
            for img_big in os.listdir(f"graphics/player/{folder}/"):
                i = Image.open(f"graphics/player/{folder}/{img_big}")
                width, height = i.width, i.height
                w, h = int(width/64), int(height/64)
                left, upper, right, lower = 0, 0, 64, 64
                r_i = 0
                for _ in range(h):
                    c_i = 0
                    for _ in range(w):
                        img = i.crop((left+c_i, upper+r_i, right+c_i, lower+r_i))
                        #img = img.resize((128,128))
                        for k in self.player_images[folder]:
                            if k in img_big:
                                try:
                                    self.player_images[folder][k][img_big].append(img)
                                except KeyError:
                                    self.player_images[folder][k][img_big] = []
                                    self.player_images[folder][k][img_big].append(img)
                        c_i += 64
                    r_i += 64

    def add_label_armor_images(self):# ???
        i = Image.open(f"graphics/armor.png")
        width, height = i.width, i.height
        w, h = int(width/64), int(height/64)
        left, upper, right, lower = 0, 0, 64, 64
        r_i = 0
        for i_h in range(h):
            c_i = 0
            for _ in range(w):
                image = i.crop((left+c_i, upper+r_i, right+c_i, lower+r_i))
                image = image.resize((32,32))
                img = self.pil_img_to_surface(image)
                try:
                    self.label_armor_images[f"{i_h}"].append(img)
                except KeyError:
                    self.label_armor_images[f"{i_h}"] = []
                    self.label_armor_images[f"{i_h}"].append(img)
                c_i += 64
            r_i += 64

    def pil_img_to_surface(self, pil_img):
        return pygame.image.fromstring(pil_img.tobytes(), pil_img.size, pil_img.mode).convert_alpha()