import pygame, os, time
from PIL import Image

screen_width, screen_height = 1200, 720
scale = 32

red = (255,0,0)
orange = (255,165,0)
grey = (100,100,100)
white = (255,255,255)
brown = (222,184,135)

persons_s = {
    "player":{"id":1, "health":100, "speed":2, "body":'body_male.png', "hair":"head_hair_blonde.png",
                "head":None, "weapon":2, "torso":11, "hands":None, "legs":16, "belt":19, "feet":21, "behind":None, "shield":None,
                "sword_skill":1, "spear_skill":1, "inventory":[25,26]},

    "enemy":{"id":2, "health":50, "speed":1, "body":'body_skeleton.png', "hair":None,
                "head":None, "weapon":0, "torso":None, "hands":None, "legs":None, "belt":None, "feet":None, "behind":None, "shield":None,
                "sword_skill":1, "spear_skill":1, "inventory":[27]},

    "trader":{"id":3, "health":150, "speed":2, "body":'body_male.png', "hair":None,
                "head":8, "weapon":5, "torso":12, "hands":None, "legs":17, "belt":20, "feet":21, "behind":None, "shield":None,
                "sword_skill":5, "spear_skill":1, "inventory":[27,1,3,4,5,6,25,26,8,10,12,14,15,17,18,20,22,24], "dialogs":["Trade ?"]},
}
boxes_s = {
    "box":{"id":1, "inventory":[25,26,27,14], "obj_type":"box", "image":"graphics/box_closed.png", "image_open":"graphics/box_opened.png"},
}
items_s = {
    "weapon00":{"id":0, "name":"Steel sword", "obj_type":"weapon", "image":"graphics/sword.png", "anim":"weapon_sword.png", "damage":10, "cooldown":2, "radius":20},
    "weapon01":{"id":1, "name":"Great sword", "obj_type":"weapon", "image":"graphics/sword2.png", "anim":"weapon_sword.png", "damage":15, "cooldown":2, "radius":20},
    "weapon02":{"id":2, "name":"Short staff", "obj_type":"weapon", "image":"graphics/staff.png", "anim":"weapon_staff.png", "damage":10, "cooldown":3, "radius":20},
    "weapon03":{"id":3, "name":"Short spear", "obj_type":"weapon", "image":"graphics/spear.png", "anim":"weapon_spear.png", "damage":15, "cooldown":3, "radius":20},
    "weapon04":{"id":4, "name":"Long sword", "obj_type":"weapon", "image":"graphics/sword_long.png", "anim":"weapon_longsword.png", "damage":20, "cooldown":3, "radius":32},
    "weapon05":{"id":5, "name":"Long rapier", "obj_type":"weapon", "image":"graphics/rapier.png", "anim":"weapon_rapier.png", "damage":20, "cooldown":3, "radius":32},
    "weapon06":{"id":6, "name":"Long spear", "obj_type":"weapon", "image":"graphics/spear_long.png", "anim":"weapon_long_spear.png", "damage":25, "cooldown":4, "radius":42},
    "outfit00":{"id":7, "name":"Robe hood", "obj_type":"head", "image":None, "anim":"head_robe_hood.png", "armor":0.1},
    "outfit01":{"id":8, "name":"Leather hat", "obj_type":"head", "image":None, "anim":"head_leather_armor_hat.png", "armor":0.2},
    "outfit02":{"id":9, "name":"Chain helmet", "obj_type":"head", "image":None, "anim":"head_chain_armor_helmet.png", "armor":0.4},
    "outfit03":{"id":10, "name":"Plate helmet", "obj_type":"head", "image":None, "anim":"head_plate_armor_helmet.png", "armor":0.5},
    "outfit06":{"id":11, "name":"Robe shirt", "obj_type":"torso", "image":None, "anim":"torso_robe_shirt_brown.png", "armor":0.5},
    "outfit07":{"id":12, "name":"Leather armor", "obj_type":"torso", "image":None, "anim":"torso_leather_armor_torso.png", "armor":1.0},
    "outfit08":{"id":13, "name":"Chain armor", "obj_type":"torso", "image":None, "anim":"torso_chain_armor_torso.png", "armor":1.5},
    "outfit09":{"id":14, "name":"Plate armor", "obj_type":"torso", "image":None, "anim":"torso_plate_armor_torso.png", "armor":2.0},
    "outfit10":{"id":15, "name":"Armor gloves", "obj_type":"hands", "image":None, "anim":"hands_plate_armor_gloves.png", "armor":0.2},
    "outfit11":{"id":16, "name":"Robe skirt", "obj_type":"legs", "image":None, "anim":"legs_robe_skirt.png", "armor":0.1},
    "outfit12":{"id":17, "name":"Green pants", "obj_type":"legs", "image":None, "anim":"legs_pants_greenish.png", "armor":0.3},
    "outfit13":{"id":18, "name":"Plate pants", "obj_type":"legs", "image":None, "anim":"legs_plate_armor_pants.png", "armor":0.5},
    "outfit14":{"id":19, "name":"Rope belt", "obj_type":"belt", "image":None, "anim":"belt_rope.png", "armor":0.1},
    "outfit15":{"id":20, "name":"Leather belt", "obj_type":"belt", "image":None, "anim":"belt_leather.png", "armor":0.2},
    "outfit16":{"id":21, "name":"Brown shoes", "obj_type":"feet", "image":None, "anim":"feet_shoes_brown.png", "armor":0.1},
    "outfit17":{"id":22, "name":"Plate shoes", "obj_type":"feet", "image":None, "anim":"feet_plate_armor_shoes.png", "armor":0.3},
    "outfit18":{"id":23, "name":"Quiver", "obj_type":"behind", "image":None, "anim":"behind_quiver.png", "armor":0.3},
    "outfit19":{"id":24, "name":"Wood shield", "obj_type":"shield", "image":None, "anim":"shield_cutout_body.png", "armor":0.5},
    "potion01":{"id":25, "name":"Health potion", "obj_type":"potion", "image":"graphics/potion_h.png", "for_adding":50},
    "potion02":{"id":26, "name":"Energy potion", "obj_type":"potion", "image":"graphics/potion_e.png", "for_adding":50},
    "coins001":{"id":27, "name":"Coins", "obj_type":"coins", "image":"graphics/coin.png", "amount":1000},
}

class Sounds():
    def __init__(self):
        self.sound_status = {"nature":None, "ocean":None}
        self.sounds = []
        self.add_sounds()

    def add_sounds(self):
        for file in os.listdir("sounds/"):
            self.sounds.append(pygame.mixer.Sound(f"sounds/{file}"))

    def play_map_sounds(self):
        if self.sound_status["nature"] == None:
            pygame.mixer.Sound.set_volume(self.sounds[7], 0.5)
            self.sounds[7].play()
            self.sound_status["nature"] = time.time()
        else:
            if time.time() - self.sound_status["nature"] >= self.sounds[7].get_length():
                self.sound_status["nature"] = None
        if self.sound_status["ocean"] == None:
            pygame.mixer.Sound.set_volume(self.sounds[6], 0.05)
            self.sounds[6].play()
            self.sound_status["ocean"] = time.time()
        else:
            if time.time() - self.sound_status["ocean"] >= self.sounds[6].get_length():
                self.sound_status["ocean"] = None

class Images():
    def __init__(self):
        self.trees_images = []
        self.player_images = {
            "bow":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}, "shield":{}},
            "hurt":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}, "shield":{}},
            "slash":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}, "shield":{}},
            "spellcast":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}, "shield":{}},
            "thrust":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}, "shield":{}},
            "walkcycle":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}, "shield":{}}}
        self.add_player_images()
        self.add_images(self.trees_images, "graphics/map/wood_tileset.png", 32)

    def add_images(self, result:list, path:str, img_scale:int):
        i = Image.open(path)
        width, height = i.width, i.height
        w, h = int(width/img_scale), int(height/img_scale)
        left, upper, right, lower = 0, 0, img_scale, img_scale
        r_i = 0
        for _ in range(h):
            c_i = 0
            for _ in range(w):
                image = i.crop((left+c_i, upper+r_i, right+c_i, lower+r_i))
                img = self.pil_img_to_surface(image)
                result.append(img)
                c_i += img_scale
            r_i += img_scale

    def add_player_images(self):
        for folder in os.listdir("graphics/player/"):
            for img_big in os.listdir(f"graphics/player/{folder}/"):
                i = Image.open(f"graphics/player/{folder}/{img_big}")
                width, height = i.width, i.height
                img_scale = 192 if img_big in "weapon_longsword.png/weapon_rapier.png/weapon_long_spear.png" else 64
                w, h = int(width/img_scale), int(height/img_scale)
                left, upper, right, lower = 0, 0, img_scale, img_scale
                r_i = 0
                for _ in range(h):
                    c_i = 0
                    for _ in range(w):
                        img = i.crop((left+c_i, upper+r_i, right+c_i, lower+r_i))
                        for k in self.player_images[folder]:
                            if k in img_big:
                                try:
                                    self.player_images[folder][k][img_big].append(img)
                                except KeyError:
                                    self.player_images[folder][k][img_big] = []
                                    self.player_images[folder][k][img_big].append(img)
                        c_i += img_scale
                    r_i += img_scale

    def pil_img_to_surface(self, pil_img):
        return pygame.image.fromstring(pil_img.tobytes(), pil_img.size, pil_img.mode).convert_alpha()

    def load(self, image_path):
        return pygame.image.load(image_path).convert_alpha()