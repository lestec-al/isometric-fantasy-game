import pygame, random, os, time, threading, socket, json, sys, platform, tkinter as tk
from pygame.locals import *
from PIL import Image


# MAIN ASSETS

class Sounds():
    """This module provide all sounds in the game"""
    def __init__(self):
        self.sound_status = {"nature":None, "ocean":None}
        self.all = []
        # Add all sounds
        for file in os.listdir("sounds/"):
            self.all.append(pygame.mixer.Sound(f"sounds/{file}"))

    def play_map_sounds(self):
        if self.sound_status["nature"] == None:
            pygame.mixer.Sound.set_volume(self.all[7], 0.5)
            self.all[7].play()
            self.sound_status["nature"] = time.time()
        else:
            if time.time() - self.sound_status["nature"] >= self.all[7].get_length():
                self.sound_status["nature"] = None
        if self.sound_status["ocean"] == None:
            pygame.mixer.Sound.set_volume(self.all[6], 0.05)
            self.all[6].play()
            self.sound_status["ocean"] = time.time()
        else:
            if time.time() - self.sound_status["ocean"] >= self.all[6].get_length():
                self.sound_status["ocean"] = None


class Images():
    """This module provide all images (sprites) in the game"""
    def __init__(self):
        self.trees = []
        self.player = {
            "bow":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}, "shield":{}},
            "hurt":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}, "shield":{}},
            "slash":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}, "shield":{}},
            "spellcast":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}, "shield":{}},
            "thrust":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}, "shield":{}},
            "walkcycle":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}, "shield":{}}}
        self.add_player_images()
        self.add_images(self.trees, "graphics/map/wood_tileset.png", 32)

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
                        for k in self.player[folder]:
                            if k in img_big:
                                try:
                                    self.player[folder][k][img_big].append(img)
                                except KeyError:
                                    self.player[folder][k][img_big] = []
                                    self.player[folder][k][img_big].append(img)
                        c_i += img_scale
                    r_i += img_scale

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

    def pil_img_to_surface(self, pil_img):
        return pygame.image.fromstring(pil_img.tobytes(), pil_img.size, pil_img.mode).convert_alpha()

    def load(self, image_path):
        return pygame.image.load(image_path).convert_alpha()


# DIFFERENT OBJECTS

class Object():
    def __init__(self, id, map, obj_type):
        self.id = id
        self.map = map
        self.obj_type = obj_type
        self.image = None


class Box(Object):
    def __init__(self, id, map, obj_type, image, image_open):
        super().__init__(id, map, obj_type)
        self.image = image
        self.image_open = image_open
        self.inventory = []
        self.capacity = 30


class Item():
    def __init__(self, id, name, obj_type, image):
        self.id = id
        self.name = name
        self.obj_type = obj_type
        self.image = image
        self.map = pygame.Rect(0, 0, SCALE, SCALE)


class Weapon(Item):
    def __init__(self, id, name, obj_type, image, anim, damage, cooldown, radius):
        super().__init__(id, name, obj_type, image)
        self.anim = anim
        self.damage = damage
        self.cooldown = cooldown
        self.radius = radius


class Outfit(Item):
    def __init__(self, id, name, obj_type, image, anim, armor):
        super().__init__(id, name, obj_type, image)
        self.anim = anim
        self.armor = armor


class Potion(Item):
    def __init__(self, id, name, obj_type, image, for_adding):
        super().__init__(id, name, obj_type, image)
        self.for_adding = for_adding

    def drink_potion(self, person):
        if "health" in self.name.lower():
            if person.health + self.for_adding > person.health_bar_width:
                person.health = person.health_bar_width
            else:
                person.health += self.for_adding
        elif "energy" in self.name.lower():
            if person.energy + self.for_adding > person.energy_bar_width:
                person.energy = person.energy_bar_width
            else:
                person.energy += self.for_adding


class Coins(Item):
    def __init__(self, id, name, obj_type, image, amount):
        super().__init__(id, name, obj_type, image)
        self.amount = amount


# PLAYERS / NPCs

class Person():
    """Class for representing players and NPCs. Handles all sorts of things like stats, movement, attacks, inventory, etc."""
    def __init__(self, health, speed, body, sword_skill=1, spear_skill=1,
        hair=None, head=None, weapon=None, torso=None, hands=None, legs=None, belt=None, feet=None, behind=None, shield=None):
        # Stats
        self.obj_type = "npc-enemy"
        self.id = None
        self.health = health
        self.health_bar_width = health
        self.speed = speed
        self.skills = {"sword":sword_skill, "spear":spear_skill}
        self.armor = 0
        self.energy = 100
        self.energy_bar_width = 100
        self.dialogs = []
        # Attack
        self.attack_time = None
        self.attack_stop = False
        self.attack_anim_stop = False
        self.under_attack_time = None
        # Sounds
        self.sound_status = {"attack":False, "under_attack":False, "drink_potion":False, "inventory_items":False, "box":False}
        self.sound_stage = 0
        # Map
        self.map = None
        self.screen = None
        self.camera_x, self.camera_y = 0, 0
        # Movement, Animations
        self.move_status = "right"
        self.anim_stage = 0
        self.idle_stage = 0
        self.movement = None # npc
        self.direction = "y" # npc
        # Inventory
        self.inventory = []
        self.capacity = 20
        self.inventory_open = False
        self.box = None
        self.trader = None
        self.showing_item = None
        self.show_pos = None
        self.show_item = False
        self.selected = {
            "head":head,
            "behind":behind,
            "belt":belt,
            "feet":feet,
            "hands":hands,
            "legs":legs,
            "torso":torso,
            "weapon":weapon,
            "shield":shield}
        self.wear = {
            "body":body,
            "head":hair,
            "behind":None,
            "belt":None,
            "feet":None,
            "hands":None,
            "legs":None,
            "torso":None,
            "weapon":None,
            "shield":None}
        self.hair = hair
        # Add selected items to inventory and to wearing (id -> item)
        for i in ITEMS:
            for k in self.selected:
                if self.selected[k] != None and self.selected[k] == i.id:
                    if i not in self.inventory:
                        self.inventory.append(i)
                    self.selected[k] = i
                    self.wear[k] = i.anim
        self.count_armor()

    def count_armor(self):
        self.armor = 0
        for k in self.selected:
            if self.selected[k] != None and k != "weapon" and k != "behind":
                if k == "head":
                    try:self.armor += self.selected[k].armor
                    except:pass
                else:
                    self.armor += self.selected[k].armor

    def draw_person(self):
        def choose_animations(direction, anim_list):
            index = len(anim_list)//4
            if direction == "u":
                ready_anim_list = anim_list[0:index]
            elif direction == "l":
                ready_anim_list = anim_list[index:index*2]
            elif direction == "d":
                ready_anim_list = anim_list[index*2:index*3]
            elif direction == "r":
                ready_anim_list = anim_list[index*3:]
            elif direction == "hurt":
                ready_anim_list = anim_list
            return ready_anim_list

        def draw(direction, anim):
            # Merge (body-clothes-belt-behind-shield) images into one + weapon separately
            image_body = choose_animations(direction, IMAGES.player[anim]["body"][self.wear["body"]])[int(self.anim_stage)]
            if self.wear["belt"] != None:
                image_belt = choose_animations(direction, IMAGES.player[anim]["belt"][self.wear["belt"]])[int(self.anim_stage)]
            else:
                image_belt = None
            if self.wear["behind"] != None:
                image_behind = choose_animations(direction, IMAGES.player[anim]["behind"][self.wear["behind"]])[int(self.anim_stage)]
            else:
                image_behind = None
            if (self.wear["shield"] != None and anim == "slash" or self.wear["shield"] != None and anim == "thrust" or
                self.wear["shield"] != None and anim == "walkcycle"):
                image_shield = choose_animations(direction, IMAGES.player[anim]["shield"][self.wear["shield"]])[int(self.anim_stage)]
            else:
                image_shield = None
            if anim == "slash" or anim == "thrust":
                image_weapon = choose_animations(direction, IMAGES.player[anim]["weapon"][self.wear["weapon"]])[int(self.anim_stage)]
            else:
                image_weapon = None
            image = None
            for part in self.wear:
                if (self.wear[part] != None and
                    part != "body" and part != "belt" and part != "weapon" and part != "behind" and part != "shield"):
                    if image == None:
                        anim_list = choose_animations(direction, IMAGES.player[anim][part][self.wear[part]])
                        image = anim_list[int(self.anim_stage)]
                    else:
                        anim_list = choose_animations(direction, IMAGES.player[anim][part][self.wear[part]])
                        image = Image.alpha_composite(image, anim_list[int(self.anim_stage)])
            if image != None:
                image = Image.alpha_composite(image_body, image)
            else:
                image = image_body
            if image_belt != None:
                image = Image.alpha_composite(image, image_belt)
            if image_behind != None:
                image = Image.alpha_composite(image, image_behind)
            if image_shield != None:
                image = Image.alpha_composite(image, image_shield)
            # Draw on screen
            img = IMAGES.pil_img_to_surface(image)
            self.screen = img.get_rect()
            self.screen.center = (self.map.centerx-PLAYER.camera_x, self.map.centery-20-PLAYER.camera_y)
            WINDOW.blit(img, self.screen)
            if image_weapon != None:
                img_weapon = IMAGES.pil_img_to_surface(image_weapon)
                screen_weapon = img_weapon.get_rect()
                screen_weapon.center = (self.map.centerx-PLAYER.camera_x, self.map.centery-20-PLAYER.camera_y)
                WINDOW.blit(img_weapon, screen_weapon)

        def animate(direction , anim):
            # Periodically play idle(spellcast) animation
            try:
                # If person stands
                if "go" not in self.move_status and anim == "walkcycle" and self.idle_stage < 50:
                    self.idle_stage += 0.1
                    self.anim_stage = 0
                # If person stands some time
                elif "go" not in self.move_status and anim == "walkcycle" and self.idle_stage > 50:
                    anim = "spellcast"
                    self.anim_stage += 0.2
                    if self.anim_stage >= 7:
                        self.anim_stage = 0
                        self.idle_stage = 0
                        anim = "walkcycle"
                # Other animations (if person not stands)
                else:
                    self.anim_stage += 0.2
                    self.idle_stage = 0
                draw(direction, anim)
            # If image animations run out
            except:
                if "slash" in anim or "thrust" in anim:
                    self.attack_anim_stop = True
                self.anim_stage = 0
                draw(direction, anim)

        # Drawing logic
        if self.health <= 0:
            self.under_attack_time = None
            try:
                self.anim_stage += 0.1
                draw("hurt", "hurt")
            except:
                self.anim_stage = 5
                draw("hurt", "hurt")
        elif self.under_attack_time != None:
            if "go" in self.move_status:
                self.move_status = self.move_status[:-3]
            self.anim_stage = 2
            if self.move_status == "up":draw("u", "spellcast")
            elif self.move_status == "down":draw("d", "spellcast")
            elif self.move_status == "left":draw("l", "spellcast")
            elif self.move_status == "right":draw("r", "spellcast")
        elif self.attack_time != None and self.attack_anim_stop == False:
            if "sword" in self.wear["weapon"] or "rapier" in self.wear["weapon"]:
                if self.move_status == "up":animate("u", "slash")
                elif self.move_status == "down":animate("d", "slash")
                elif self.move_status == "left":animate("l", "slash")
                elif self.move_status == "right":animate("r", "slash")
            elif "staff" in self.wear["weapon"] or "spear" in self.wear["weapon"]:
                if self.move_status == "up":animate("u", "thrust")
                elif self.move_status == "down":animate("d", "thrust")
                elif self.move_status == "left":animate("l", "thrust")
                elif self.move_status == "right":animate("r", "thrust")
        else:
            if self.move_status == "up":animate("u", "walkcycle")
            elif self.move_status == "down":animate("d", "walkcycle")
            elif self.move_status == "left":animate("l", "walkcycle")
            elif self.move_status == "right":animate("r", "walkcycle")
            # Moving
            if self.move_status == "up-go":animate("u", "walkcycle")
            elif self.move_status == "down-go":animate("d", "walkcycle")
            elif self.move_status == "left-go":animate("l", "walkcycle")
            elif self.move_status == "right-go":animate("r", "walkcycle")

    def play_sounds(self):
        if self.under_attack_time != None and self.sound_status["under_attack"] == False:
            pygame.mixer.Sound.set_volume(SOUNDS.all[0], 0.4)
            pygame.mixer.Sound.set_volume(SOUNDS.all[4], 0.4)
            SOUNDS.all[0].play()
            SOUNDS.all[4].play()
            self.sound_status["under_attack"] = True
        elif self.attack_time != None and self.attack_anim_stop == False and self.sound_status["attack"] == False:
            pygame.mixer.Sound.set_volume(SOUNDS.all[9], 0.4)
            SOUNDS.all[9].play()
            self.sound_status["attack"] = True
        else:
            if "go" in self.move_status:
                if self.sound_stage < 2:
                    self.sound_stage = 2
                elif self.sound_stage > 3:
                    self.sound_stage = 2
                if self.sound_stage == 2:
                    s = SOUNDS.all[self.sound_stage]
                    pygame.mixer.Sound.set_volume(s, 0.05)
                    s.play()
                self.sound_stage += 0.04
        if self.sound_status["drink_potion"] == True:
            pygame.mixer.Sound.set_volume(SOUNDS.all[1], 0.4)
            SOUNDS.all[1].play()
            self.sound_status["drink_potion"] = False
        if self.sound_status["inventory_items"] == True:
            pygame.mixer.Sound.set_volume(SOUNDS.all[5], 0.4)
            SOUNDS.all[5].play()
            self.sound_status["inventory_items"] = False
        if self.sound_status["box"] == True:
            if self.box != None and self.box.obj_type == "box":
                pygame.mixer.Sound.set_volume(SOUNDS.all[8], 0.4)
                SOUNDS.all[8].play()
            self.sound_status["box"] = False

    def stats_restoration(self):
        if self.health < self.health_bar_width and self.health > 0:
            if "go" in self.move_status:
                self.health += 0.001
            else:
                self.health += 0.002
        if self.energy < self.energy_bar_width and self.health > 0:
            if "go" in self.move_status:
                self.energy += 0.01
            else:
                self.energy += 0.02
        try:
            cooldown = self.selected["weapon"].cooldown
        except:
            cooldown = 2
        if self.attack_time != None and time.time() - self.attack_time >= cooldown:
            self.attack_time = None
            self.attack_anim_stop = False
            self.sound_status["attack"] = False
        cooldown_under_attack_time = 0.5
        if self.under_attack_time != None and time.time() - self.under_attack_time >= cooldown_under_attack_time:
            self.under_attack_time = None
            self.sound_status["under_attack"] = False

    def attack(self):
        map_weapon = pygame.Rect((self.map.x,self.map.y),(self.selected["weapon"].radius,self.selected["weapon"].radius))
        map_weapon.center = self.map.center
        if "up" in self.move_status:
            map_weapon.bottom = self.map.top
        elif "down" in self.move_status:
            map_weapon.top = self.map.bottom
        elif "left" in self.move_status:
            map_weapon.right = self.map.left
        elif "right" in self.move_status:
            map_weapon.left = self.map.right
        for o in HUMAN_PERSONS+NPC_PERSONS:
            if self != o:
                if o.obj_type == "player" or o.obj_type == "online_player" or "npc" in o.obj_type and o.health > 0:
                    if map_weapon.colliderect(o.map):
                        skill = self.selected["weapon"].anim[7:-4]
                        if "spear" in skill or skill == "staff": skill = "spear"
                        elif skill == "longsword" or skill == "rapier": skill = "sword"
                        wd = self.selected["weapon"].damage
                        min_damage = (int(self.skills[skill])/10)*wd if (int(self.skills[skill])/10)*wd < wd else wd
                        randomize_damage = random.randint(min_damage, self.selected["weapon"].damage)
                        damage = randomize_damage - o.armor if randomize_damage - o.armor > 0 else 0
                        o.health -= damage
                        o.under_attack_time = time.time()
                        self.skills[skill] += 0.01
                        if ONLINE != None:
                            DAMAGES.append((o.id, damage, o.under_attack_time))

    def move(self, direction:str):
        if direction == "up":
            self.map.centery -= self.speed
            self.move_status = "up-go"
        elif direction == "down":
            self.map.centery += self.speed
            self.move_status = "down-go"
        elif direction == "left":
            self.map.centerx -= self.speed
            self.move_status = "left-go"
        elif direction == "right":
            self.map.centerx += self.speed
            self.move_status = "right-go"
        # Collisions
        for s in SPRITES:
            if self != s and self.map.colliderect(s.map):
                if "up" in self.move_status:
                    self.map.top = s.map.bottom
                elif "down" in self.move_status:
                    self.map.bottom = s.map.top
                elif "left" in self.move_status:
                    self.map.left = s.map.right
                elif "right" in self.move_status:
                    self.map.right = s.map.left

    # Methods only for Player

    def append_items_from_map(self):
        for i in ITEMS:
            if i.map.x != 0 and i.map != None:
                if i.map.colliderect(self.map):
                    if len(self.inventory) <= self.capacity and i not in self.inventory:
                        self.inventory.append(i)
                        i.map.x, i.map.y = 0, 0
                        self.sound_status["inventory_items"] = True

    def draw_player_stats(self):
        # Health, energy, cooldown indicator
        pygame.draw.rect(WINDOW, RED, (10, 10, self.health_bar_width, 17), 1)
        pygame.draw.rect(WINDOW, RED, (10, 10, self.health, 17))
        pygame.draw.rect(WINDOW, ORANGE, (10, 30, self.energy_bar_width, 17), 1)
        pygame.draw.rect(WINDOW, ORANGE, (10, 30, self.energy, 17))
        if self.attack_time != None:
            WINDOW.blit(STAT_FONT.render("!!!", True, WHITE), (10, 50, 20, 20))
        # Inventory
        if self.inventory_open:
            # Draw inventory info
            inventory_text = STAT_FONT.render(f"Player Items", True, WHITE)
            WINDOW.blit(inventory_text, (SCREEN_WIDTH//2, 32, 50, 17))
            # Boxes
            if self.box != None or self.trader != None:
                if self.box != None:
                    text = "NPC Items" if "npc" in self.box.obj_type else "Box Items"
                elif self.trader != None:
                    text = "Trader Items"
                WINDOW.blit(STAT_FONT.render(text, True, WHITE), (SCREEN_WIDTH//5, 32, 50, 17))
            # Info about single item
            if self.showing_item != None and self.show_pos != None:
                show_pos1 = (self.show_pos[0]-150, self.show_pos[1]+10)
                show_pos2 = (self.show_pos[0]-155, self.show_pos[1]+5)
                if "weapon" in self.showing_item.obj_type:
                    t1 = str(self.showing_item.damage)
                    t2 = str(self.showing_item.cooldown)
                    text = f"{t1} {t2}"
                elif "potion" in self.showing_item.obj_type:
                    text = str(self.showing_item.for_adding)
                elif "coins" in self.showing_item.obj_type:
                    text = str(self.showing_item.amount)
                else:
                    text = str(self.showing_item.armor)
                text_name = self.showing_item.name
                pygame.draw.rect(WINDOW, GREY, (show_pos2, (155, 25)))
                WINDOW.blit(STAT_FONT.render(f"{text_name} {text}", True, WHITE), (show_pos1, (50, 17)))
            # Damage, armor, skills
            if self.selected["weapon"] != None:
                weapon_damage = self.selected["weapon"].damage
                weapon_text = STAT_FONT.render(f"Damage: {str(weapon_damage)}", True, WHITE)
                WINDOW.blit(weapon_text, (SCREEN_WIDTH-120, SCREEN_HEIGHT//2, 50, 17))
            armor_text = STAT_FONT.render(f"Armor: {str(self.armor)}", True, WHITE)
            WINDOW.blit(armor_text, (SCREEN_WIDTH-120, SCREEN_HEIGHT//2+20, 50, 17))
            WINDOW.blit(STAT_FONT.render("Skills:", True, WHITE), (SCREEN_WIDTH-120, SCREEN_HEIGHT//2+60, 50, 17))
            sword_text = STAT_FONT.render(f"Sword: {str(int(self.skills['sword']))}", True, WHITE)
            WINDOW.blit(sword_text, (SCREEN_WIDTH-120, SCREEN_HEIGHT//2+80, 50, 17))
            spear_text = STAT_FONT.render(f"Spear: {str(int(self.skills['spear']))}", True, WHITE)
            WINDOW.blit(spear_text, (SCREEN_WIDTH-120, SCREEN_HEIGHT//2+100, 50, 17))

    def keyboard(self):
        pressed = pygame.key.get_pressed()
        if self.attack_time == None and self.under_attack_time == None:
            if pressed[pygame.K_w] and not self.inventory_open and self.trader == None:
                self.move("up")
            elif pressed[pygame.K_s] and not self.inventory_open and self.trader == None:
                self.move("down")
            elif pressed[pygame.K_a] and not self.inventory_open and self.trader == None:
                self.move("left")
            elif pressed[pygame.K_d] and not self.inventory_open and self.trader == None:
                self.move("right")
            else:
                if "go" in self.move_status:
                    self.move_status = self.move_status[:-3]
            if pressed[pygame.K_i]:
                time.sleep(0.5)
                if self.inventory_open == False:
                    self.inventory_open = True
                elif self.inventory_open == True:
                    self.inventory_open = False
                self.sound_status["box"] = True
                self.sound_status["inventory_items"] = True
                if self.trader == None:
                    radius = pygame.Rect((self.map.x,self.map.y),(75,75))
                    radius.center = self.map.center
                    for o in NPC_PERSONS:
                        if "trader" in o.obj_type and o.health > 0:
                            if radius.colliderect(o.map):
                                self.trader = o
                else:
                    self.trader = None
            if pressed[pygame.K_e]:
                self.append_items_from_map()
        if (pressed[pygame.K_f] and self.selected["weapon"] != None and self.under_attack_time == None and
            self.attack_time == None and "go" not in self.move_status and not self.inventory_open and self.trader == None and
            self.energy >= self.selected["weapon"].cooldown*5):
            self.attack()
            self.energy -= self.selected["weapon"].cooldown*5
            self.attack_time = time.time()

    def draw_inventory(self):
        def calc_coins(inventory):
            coins_objs = []
            coins = 0
            for i in inventory:
                if i.obj_type == "coins":
                    coins_objs.append(i)
                    coins += i.amount
            if len(coins_objs) > 1:
                for i in coins_objs[1:]:
                    inventory.remove(i)
                    del i
            if len(coins_objs) == 1:
                coins_objs[0].amount = coins
            if coins == 0:
                for i in coins_objs:
                    inventory.remove(i)
                    del i

        def draw_item(item, pos):
            # If image doesn't exist, take from anim
            if item.image == None:
                item.image = IMAGES.pil_img_to_surface(IMAGES.player["walkcycle"][item.obj_type][item.anim][18])
                image = item.image
            else:
                image = item.image
            rect = image.get_rect()
            rect.center = pos.center
            WINDOW.blit(image, rect)

        self.show_item = False
        # Boxes
        self.box = None
        for s in SPRITES:
            if "npc" in s.obj_type and s.health <= 0 or s.obj_type == "box": # No online_player
                if self.map.top == s.map.bottom and self.map.left >= s.map.left-SCALE and self.map.right <= s.map.right+SCALE:
                    self.box = s
                elif self.map.bottom == s.map.top and self.map.left >= s.map.left-SCALE and self.map.right <= s.map.right+SCALE:
                    self.box = s
                elif self.map.left == s.map.right and self.map.top >= s.map.top-SCALE and self.map.bottom <= s.map.bottom+SCALE:
                    self.box = s
                elif self.map.right == s.map.left and self.map.top >= s.map.top-SCALE and self.map.bottom <= s.map.bottom+SCALE:
                    self.box = s
        # Draw box
        if self.box != None or self.trader != None:
            y_index, x_index, item_index = 1, 0, 0
            if self.box != None:
                inventory = self.box.inventory
            elif self.trader != None:
                inventory = []
                for i in self.trader.inventory:
                    if i not in [self.trader.selected[k] for k in self.trader.selected]:
                        inventory.append(i)
            for i in inventory:
                if item_index >= 5:
                    y_index += 1
                    item_index = 0
                    x_index = 0
                y = y_index*64
                x = x_index*64
                item_pos = pygame.Rect((SCREEN_WIDTH//5)+x, y, 64, 64)
                pygame.draw.rect(WINDOW, BROWN, item_pos)
                pygame.draw.rect(WINDOW, GREY, item_pos, 1)
                draw_item(i, item_pos)
                x_index += 1
                item_index += 1
                if item_pos.collidepoint(pygame.mouse.get_pos()):
                    self.show_item = True
                    # Show item info
                    self.show_pos = pygame.mouse.get_pos()
                    self.showing_item = i
                    if pygame.mouse.get_pressed()[2]:
                        self.sound_status["inventory_items"] = True
                        time.sleep(0.5)
                        # Append items to player inventory from box
                        if self.box != None:
                            if len(self.inventory) <= self.capacity and i not in self.inventory:
                                self.inventory.append(i)
                                self.box.inventory.remove(i)
                        # Buying items ???
                        elif self.trader != None:
                            if len(self.inventory) <= self.capacity and i not in self.inventory and i.obj_type != "coins":
                                for ic in self.inventory:
                                    if ic.obj_type == "coins":
                                        if ic.amount >= 100:# Universal price ???
                                            self.inventory.append(i)
                                            self.trader.inventory.remove(i)
                                            ic.amount -= 100
                                            coins_found = False
                                            for ict in self.trader.inventory:
                                                if ict.obj_type == "coins":
                                                    coins_found = True
                                                    ict.amount += 100
                                            if coins_found == False:
                                                self.trader.inventory.append(Coins(602, "Coins", "coins", ic.image, 100))
                            calc_coins(self.trader.inventory)
                        calc_coins(self.inventory)
        # Draw inventory
        y_index, x_index, item_index = 1, 0, 0
        for i in self.inventory:
            # Draw inventory item
            if i not in [self.selected[k] for k in self.selected]:
                if item_index >= 5:
                    y_index += 1
                    item_index = 0
                    x_index = 0
                y, x = y_index*64, x_index*64
                item_pos = pygame.Rect((SCREEN_WIDTH//2)+x, y, 64, 64)
                pygame.draw.rect(WINDOW, BROWN, item_pos)
                pygame.draw.rect(WINDOW, GREY, item_pos, 1)
                draw_item(i, item_pos)               
                # Use items
                if item_pos.collidepoint(pygame.mouse.get_pos()):
                    self.show_item = True
                    # Show item info
                    self.show_pos = pygame.mouse.get_pos()
                    self.showing_item = i
                    # Use items
                    if pygame.mouse.get_pressed()[0]:
                        time.sleep(0.5)
                        if "potion" in i.obj_type:
                            self.sound_status["drink_potion"] = True
                            i.drink_potion(self)
                            self.inventory.remove(i)
                            del i
                        # Add items to selected
                        elif "coins" not in i.obj_type:
                            self.sound_status["inventory_items"] = True
                            for k in self.selected:
                                if i.obj_type == k:
                                    self.selected[k] = i
                                    self.wear[k] = i.anim
                                    self.count_armor()
                    # Move items from player inventory
                    if pygame.mouse.get_pressed()[2]:
                        self.sound_status["inventory_items"] = True
                        time.sleep(0.5)
                        if self.box != None:# Add item to the box
                            if len(self.box.inventory) <= self.box.capacity and i not in self.box.inventory:
                                self.inventory.remove(i)
                                self.box.inventory.append(i)
                        elif self.trader != None:# Sell item to trader ???
                            if len(self.trader.inventory) <= self.trader.capacity and i not in self.trader.inventory:
                                if i.obj_type != "coins":
                                    for ic in self.trader.inventory:
                                        if ic.obj_type == "coins":
                                            if ic.amount >= 100:# Universal price ???
                                                self.inventory.remove(i)
                                                self.trader.inventory.append(i)
                                                ic.amount -= 100
                                                coins_found = False
                                                for ict in self.inventory:
                                                    if ict.obj_type == "coins":
                                                        coins_found = True
                                                        ict.amount += 100
                                                if coins_found == False:
                                                    self.inventory.append(Coins(602, "Coins", "coins", ic.image, 100))
                            calc_coins(self.trader.inventory)
                        else:# Remove item to map
                            collide = False
                            for s in SPRITES:
                                if s.map.collidepoint(self.map.x-SCALE, self.map.y-SCALE):
                                    collide = True
                            if collide == False:
                                i.map.x, i.map.y = self.map.x-SCALE, self.map.y-SCALE
                                self.inventory.remove(i)
                        calc_coins(self.inventory)
                x_index += 1
                item_index += 1
            # Draw selected item
            else:
                if i.obj_type == "weapon":
                    selected_pos = pygame.Rect(SCREEN_WIDTH-64,64,64,64)
                elif i.obj_type == "behind":
                    selected_pos = pygame.Rect(SCREEN_WIDTH-64*2,64*2,64,64)
                elif i.obj_type == "head":
                    selected_pos = pygame.Rect(SCREEN_WIDTH-64,64*2,64,64)
                elif i.obj_type == "torso":
                    selected_pos = pygame.Rect(SCREEN_WIDTH-64,64*3,64,64)
                elif i.obj_type == "hands":
                    selected_pos = pygame.Rect(SCREEN_WIDTH-64*3,64*3,64,64)
                elif i.obj_type == "shield":
                    selected_pos = pygame.Rect(SCREEN_WIDTH-64*3,64*4,64,64)
                elif i.obj_type == "belt":
                    selected_pos = pygame.Rect(SCREEN_WIDTH-64*2,64*3,64,64)
                elif i.obj_type == "legs":
                    selected_pos = pygame.Rect(SCREEN_WIDTH-64,64*4,64,64)
                elif i.obj_type == "feet":
                    selected_pos = pygame.Rect(SCREEN_WIDTH-64*2,64*4,64,64)
                pygame.draw.rect(WINDOW, BROWN, selected_pos)
                pygame.draw.rect(WINDOW, GREY, selected_pos, 1)
                draw_item(i, selected_pos)
                if selected_pos.collidepoint(pygame.mouse.get_pos()):
                    self.show_item = True
                    # Show item info
                    self.show_pos = pygame.mouse.get_pos()
                    self.showing_item = i
                    # Move items from selected
                    if pygame.mouse.get_pressed()[0]:
                        self.sound_status["inventory_items"] = True
                        time.sleep(0.5)
                        for k in self.selected:
                            if i == self.selected[k]:
                                if k == "head" and self.hair != None:
                                    self.selected[k] = None
                                    self.wear[k] = self.hair
                                else:
                                    self.selected[k] = None
                                    self.wear[k] = None
                                self.count_armor()

    def clean_showing_item(self):
        if not self.inventory_open and self.box != None:
            self.box = None
        if self.show_item == False:
            if self.showing_item != None:
                self.showing_item = None
            if self.show_pos != None:
                self.show_pos = None

    def camera(self):
        right_border = WORLD_MAP_RECT.width - SCREEN_WIDTH
        down_border = WORLD_MAP_RECT.height - SCREEN_HEIGHT
        if self.screen.x < SCREEN_WIDTH//2:
            num1 = SCREEN_WIDTH//2 - self.screen.x
            if self.camera_x - num1 < 0:
                self.camera_x == 0
            else:
                self.camera_x -= num1
        elif self.screen.x > SCREEN_WIDTH//2:
            num1 = self.screen.x - SCREEN_WIDTH//2
            if self.camera_x + num1 > right_border:
                self.camera_x = right_border
            else:
                self.camera_x += num1
        if self.screen.y < SCREEN_HEIGHT//2:
            num1 = SCREEN_HEIGHT//2 - self.screen.y
            if self.camera_y - num1 < 0:
                self.camera_y == 0
            else:
                self.camera_y -= num1
        elif self.screen.y > SCREEN_HEIGHT//2:
            num1 = self.screen.y - SCREEN_HEIGHT//2
            if self.camera_y + num1 > down_border:
                self.camera_y = down_border
            else:
                self.camera_y += num1

    # Methods only for NPCs

    def draw_npc_stats(self):
        health_rect = pygame.Rect(0, 0, self.health_bar_width/5, SCALE/10)
        health_rect_i = pygame.Rect(0, 0, self.health/5, SCALE/10)
        health_rect.center = (self.map.centerx-PLAYER.camera_x, self.map.y-32-PLAYER.camera_y)
        health_rect_i.center = (self.map.centerx-PLAYER.camera_x, self.map.y-32-PLAYER.camera_y)
        pygame.draw.rect(WINDOW, RED, health_rect, 1)
        pygame.draw.rect(WINDOW, RED, health_rect_i)

    def draw_npc_dialogs(self):
        if self.health > 0 and PLAYER.health > 0 and self.attack_time == None and self.under_attack_time == None:
            x_distance, y_distance, _ = self.calc_distance(person_map=PLAYER.map, x=self.map.centerx, y=self.map.centery)
            if x_distance < 40 and y_distance < 40:
                # Change move status on player direction when player in radius
                test = pygame.Rect((self.map.x, self.map.y),(40, 40))
                test.center = self.map.center
                for status in ["up","down","left","right"]:
                    if "up" in status:
                        test.bottom = self.map.top
                    elif "down" in status:
                        test.top = self.map.bottom
                    elif "left" in status:
                        test.right = self.map.left
                    elif "right" in status:
                        test.left = self.map.right
                    if test.colliderect(PLAYER.map):
                        self.move_status = status
                # Draw dialogs
                rect_pos = (self.map.x-30-PLAYER.camera_x, self.map.y-60-PLAYER.camera_y)
                text = self.dialogs[0]
                pygame.draw.rect(WINDOW, GREY, (rect_pos, (50, 17)))
                WINDOW.blit(STAT_FONT.render(text, True, WHITE), (rect_pos, (50, 17)))

    def npc_move_attack(self):
        if self.health > 0 and self.attack_time == None and self.under_attack_time == None:
            # NPC seen radius
            seen_radius = pygame.Rect((0,0),(300,300))
            seen_radius.center = (self.map.centerx, self.map.centery)
            # Specify enemies for NPC and calculate distance to them
            distances = []
            for p in HUMAN_PERSONS:
                if p.health > 0:
                    if seen_radius.colliderect(p.map):
                        x, y, d = self.calc_distance(person_map=p.map, x=self.map.centerx, y=self.map.centery)
                        distances.append([p, x, y, d])

            # If player/s in NPC seen radius
            if len(distances) > 0:
                distances.sort(key=lambda s:s[3])
                player = distances[0][0]

                # When NPC close to the player
                if (distances[0][1] < self.selected["weapon"].radius and distances[0][2] < 10 or
                    distances[0][2] < self.selected["weapon"].radius and distances[0][1] < 10):
                    # Stop anim
                    if "go" in self.move_status:
                        self.move_status = self.move_status[:-3]
                    # Turn to the player - testing all sides
                    test = pygame.Rect((self.map.x,self.map.y),(self.selected["weapon"].radius,self.selected["weapon"].radius))
                    test.center = self.map.center
                    for status in ["up","down","left","right"]:
                        if "up" in status:
                            test.bottom = self.map.top
                        elif "down" in status:
                            test.top = self.map.bottom
                        elif "left" in status:
                            test.right = self.map.left
                        elif "right" in status:
                            test.left = self.map.right
                        if test.colliderect(player.map):
                            self.move_status = status
                    # Attack player
                    if self.selected["weapon"] != None and self.energy >= self.selected["weapon"].cooldown*5:
                        self.attack()
                        self.energy -= self.selected["weapon"].cooldown*5
                        self.attack_time = time.time()

                # When the NPC is away from the player
                else:
                    # Calculate possible moves
                    possible_moves = {"up":0, "down":0, "left":0, "right":0}
                    o1 = self.map

                    # Checking obstacles
                    for o2 in SPRITES:
                        if o1 != o2:
                            o2 = o2.map
                            if (o1.top == o2.bottom and o1.left >= o2.left-15 and o1.right <= o2.right+15 and
                                o1.right >= o2.left and o1.left <= o2.right):
                                if "up" in possible_moves:
                                    possible_moves.pop("up")
                            if (o1.bottom == o2.top and o1.left >= o2.left-15 and o1.right <= o2.right+15 and
                                o1.right >= o2.left and o1.left <= o2.right):
                                if "down" in possible_moves:
                                    possible_moves.pop("down")
                            if (o1.left == o2.right and o1.top >= o2.top-15 and o1.bottom <= o2.bottom+15 and
                                o1.bottom >= o2.top and o1.top <= o2.bottom):
                                if "left" in possible_moves:
                                    possible_moves.pop("left")
                            if (o1.right == o2.left and o1.top >= o2.top-15 and o1.bottom <= o2.bottom+15 and
                                o1.bottom >= o2.top and o1.top <= o2.bottom):
                                if "right" in possible_moves:
                                    possible_moves.pop("right")
                    if "up" in possible_moves:
                        possible_moves["up"] = self.calc_distance(person_map=player.map, y=self.map.centery-self.speed)
                    if "down" in possible_moves:
                        possible_moves["down"] = self.calc_distance(person_map=player.map, y=self.map.centery+self.speed)
                    if "left" in possible_moves:
                        possible_moves["left"] = self.calc_distance(person_map=player.map, x=self.map.centerx-self.speed)
                    if "right" in possible_moves:
                        possible_moves["right"] = self.calc_distance(person_map=player.map, x=self.map.centerx+self.speed)

                    # Moving
                    if self.movement == None:
                        if ("up" not in possible_moves and self.map.centery > player.map.centery or
                            "down" not in possible_moves and self.map.centery < player.map.centery):
                            if "left" in possible_moves:
                                self.movement = {"left":40}
                                self.direction = "y"
                            elif "right" in possible_moves:
                                self.movement = {"right":40}
                                self.direction = "y"
                        if ("left" not in possible_moves and self.map.centerx > player.map.centerx or
                            "right" not in possible_moves and self.map.centerx < player.map.centerx):
                            if "up" in possible_moves:
                                self.movement = {"up":40}
                                self.direction = "x"
                            elif "down" in possible_moves:
                                self.movement = {"down":40}
                                self.direction = "x"
                        else:
                            if "x" in self.direction:
                                if self.map.centerx > player.map.centerx:
                                    self.move("left")
                                elif self.map.centerx < player.map.centerx:
                                    self.move("right")
                                elif self.map.centery > player.map.centery:
                                    self.move("up")
                                elif self.map.centery < player.map.centery:
                                    self.move("down")
                            elif "y" in self.direction:
                                if self.map.centery > player.map.centery:
                                    self.move("up")
                                elif self.map.centery < player.map.centery:
                                    self.move("down")
                                elif self.map.centerx > player.map.centerx:
                                    self.move("left")
                                elif self.map.centerx < player.map.centerx:
                                    self.move("right")

                    elif self.movement != None:
                        for i in self.movement:
                            if i in possible_moves:
                                if self.movement[i] >= 0:
                                    self.move(i)
                                    self.movement[i] -= self.speed
                                if self.movement[i] <= 0:
                                    self.movement = None
                                else: break
                            else: self.movement = None

            # If the NPC did not see the player/s -> stop
            else:
                if "go" in self.move_status:
                    self.move_status = self.move_status[:-3]

    def calc_distance(self, person_map:pygame.Rect, x:int=None, y:int=None):
        """Calculate distance from Person.map to 'x' and/or 'y'"""
        if x != None:
            if x < person_map.centerx:
                x_distance = person_map.centerx - x
            elif x > person_map.centerx:
                x_distance = x - person_map.centerx
            else:
                x_distance = 0
        if y != None:
            if y < person_map.centery:
                y_distance = person_map.centery - y
            elif y > person_map.centery:
                y_distance = y - person_map.centery
            else:
                y_distance = 0
        if x != None and y != None:
            eu_distance = ((x - person_map.centerx)**2 + (y - person_map.centery)**2)**0.5
            return x_distance, y_distance, eu_distance
        elif x != None:
            return x_distance
        elif y != None:
            return y_distance


# ONLINE GAMEPLAY

class OnlineUpdateThread(threading.Thread):
    """This module provides communication between the player (host) and the player/s (client/s)"""
    def run(self):
        global HOST
        if HOST == True:
            conn, address = ONLINE.accept()

        self.last_receive_time = None
        self.thread_player_id = None

        self.running = True
        while self.running:
            time.sleep(0.01)

            if HOST == True:
                time_r, player_id = self.receive_updata_data(conn)
                if conn:
                    self.send_data(conn)

            elif HOST == False:
                self.send_data(ONLINE)
                time_r, player_id = self.receive_updata_data(ONLINE)

            # If online player do not responds 2 min - close thread
            if time_r != None:
                self.last_receive_time = time_r
                self.thread_player_id = player_id
            if self.last_receive_time != None:
                if time.time() - self.last_receive_time > 120.0:
                    self.running = False

        # If thread stops - delete online players
        if self.thread_player_id != None:
            HOST = True
            for s in HUMAN_PERSONS:
                if s.id == self.thread_player_id:
                    SPRITES.remove(s)
                    HUMAN_PERSONS.remove(s)

    def stop(self):
        self.running = False

    def send_data(self, source):
        sending_data = []
        for s in HUMAN_PERSONS+NPC_PERSONS:
            if s.obj_type != "npc-trader":
                if HOST == True or (HOST == False and s.id == PLAYER.id):
                    s_data = {
                        "player_id":s.id,
                        "health":s.health,
                        "attack_stop":s.attack_stop,
                        "attack_anim_stop":s.attack_anim_stop,
                        "attack_time":s.attack_time if s.attack_time != None else "None",
                        "under_attack_time":s.under_attack_time if s.under_attack_time != None else "None",
                        "map_x":s.map.x,
                        "map_y":s.map.y,
                        "move_status":s.move_status,
                    }
                    if s == PLAYER:
                        s_data["wear"] = s.wear
                        s_data["armor"] = s.armor
                sending_data.append(s_data)
        sending_data.append({"damages":DAMAGES})
        data_to_send = json.dumps(sending_data)
        try:
            source.sendall(bytes(data_to_send,encoding="utf-8"))
        except:
            pass
        DAMAGES.clear()

    def receive_updata_data(self, source):
        def update_person_info(person:Person, url_person:dict):
            person.move_status = d["move_status"]
            person.health = url_person["health"]
            person.attack_stop = url_person["attack_stop"]
            person.attack_anim_stop = url_person["attack_anim_stop"]
            try:
                person.attack_time = float(url_person["attack_time"])
            except:
                person.attack_time = None
            try:
                person.under_attack_time = float(url_person["under_attack_time"])
            except:
                person.under_attack_time = None

        try:
            received_data = source.recv(10000)
            received_data = received_data.decode("utf-8")
            received_data = json.loads(received_data)
            for d in received_data:
                if len(d) == 1:
                    for i in d["damages"]: # [(person.id, damage, under_attack_time), (person.id, damage, under_attack_time)]
                        for s in HUMAN_PERSONS+NPC_PERSONS:
                            if s.id == i[0]:
                                s.health -= i[1]
                                s.under_attack_time = i[2]
                    continue
                # Check if person already exist
                found = False
                for s in HUMAN_PERSONS+NPC_PERSONS:
                    if s.id == d["player_id"]:
                            found = True
                            # Update person info
                            if (HOST == True and d["player_id"] != PLAYER.id and d["player_id"] < 99) or (HOST == False and d["player_id"] != PLAYER.id):
                                s.map.x = d["map_x"]
                                s.map.y = d["map_y"]
                                update_person_info(s, d)
                                if s in HUMAN_PERSONS:
                                    s.wear = d["wear"]
                                    s.armor = d["armor"]
                                    player_id = d["player_id"]
                # If person not found, create new
                if found == False:
                    new = create_person("player")
                    new.obj_type = "online_player"
                    new.id = d["player_id"]
                    new.map = pygame.Rect(d["map_x"], d["map_y"], SCALE/2, SCALE/2)
                    new.wear = d["wear"]
                    new.armor = d["armor"]
                    update_person_info(new, d)

            return time.time(), player_id
        except:
            return None, None


# UTILS FUNCTIONS (for start/exit and load game)

def exit_game():
    if ONLINE != None:
        for t in THREADS:
            t.stop()
        try:
            ONLINE.shutdown(socket.SHUT_RDWR)
        except:pass
        ONLINE.close()
    pygame.quit()
    sys.exit()


def create_unique_id(objs_list:list, start_id=1):
    new_id = start_id
    test = False
    while test == False:
        test = True
        for i in objs_list:
            if new_id == i.id:
                new_id += 1
                test = False
    return new_id


def persons_boxes_items():
    p = []
    for s in SPRITES:
        if s.obj_type == "player" or "npc" in s.obj_type or s.obj_type == "box":
            for i in s.inventory:
                p.append(i)
    return p


def create_item_copy(item):
    new_id = create_unique_id(ITEMS, len(ITEMS))
    if "weapon" in item.obj_type:
        c_item = Weapon(new_id, item.name, item.obj_type, item.image, item.anim, item.damage, item.cooldown, item.radius)
    elif item.obj_type in ["head", "weapon", "torso", "hands", "legs", "belt", "feet", "behind", "shield"]:
        c_item = Outfit(new_id, item.name, item.obj_type, None, item.anim, item.armor)
    elif "potion" in item.obj_type:
        c_item = Potion(new_id, item.name, item.obj_type, item.image, item.for_adding)
    elif "coins" in item.obj_type:
        c_item = Coins(new_id, item.name, item.obj_type, item.image, item.amount)
    ITEMS.append(c_item)
    return new_id, c_item


def create_person(person_type:str):
    for i1 in PERSONS_STATS:
        if i1["obj_type"] == person_type:
            i = i1
    # Create person items copy (assign new id)
    for key in i:
        if key not in ["health", "speed", "sword_skill", "spear_skill"]:
            for p_item in persons_boxes_items():
                if key == "inventory":
                    for index,inventory_item_id in enumerate(i["inventory"]):
                        if inventory_item_id == p_item.id:
                            i["inventory"][index], _ = create_item_copy(p_item)
                elif type(i[key]) == int and i[key] == p_item.id:
                    i[key], _ = create_item_copy(p_item)
    # Create person
    person = Person(i["health"], i["speed"], i["body"], i["sword_skill"], i["spear_skill"],
        i["hair"], i["head"], i["weapon"], i["torso"], i["hands"], i["legs"], i["belt"], i["feet"], i["behind"], i["shield"])
    # Add items to inventory
    for item in ITEMS:
        if item.id in i["inventory"]:
            if item.obj_type == "coins":
                item.amount = random.randint(10,item.amount) # Randomize coins amount
            person.inventory.append(item)
    #
    if "player" in person_type:
        person.obj_type = "player"
        person.id = PLAYER_ID
        HUMAN_PERSONS.append(person)
    else:
        person.id = create_unique_id(HUMAN_PERSONS+NPC_PERSONS, 100)
        NPC_PERSONS.append(person)
        if "trader" in person_type:
            person.obj_type = "npc-trader"
            person.dialogs = i["dialogs"]
    SPRITES.append(person)
    return person


def load_main_menu():
    """Load Tkinter screen like game Main Menu"""

    def server(option):
        """Create or connect to a server. option = 'create' or 'connect'"""
        global ONLINE, HOST, PLAYER_ID, THREADS_NUMBER
        try:
            ONLINE = socket.socket()
            if option == "create":
                ONLINE.bind((HOST_IP, int(port_server_entry.get())))
                ONLINE.listen(int(players_entry.get()))
                THREADS_NUMBER = int(players_entry.get())
                HOST = True
            elif option == "connect":
                ONLINE.connect((url_entry.get(), int(port_entry.get())))
                HOST = False
            PLAYER_ID = int(player_id.get())
            root.destroy()
        except Exception as e:
            output.insert("end", f"{str(e)}\n")
            output.pack(side="bottom", fill="both", expand=1)

    # Screen
    root = tk.Tk()
    root.title(GAME_NAME)
    root.resizable(True, True)
    root.configure(bg="white")
    root.iconphoto(False, tk.PhotoImage(file="graphics/sword.png"))
    win = tk.Frame(root, border=20, bg="white")
    win.pack(side="top")

    # Row
    f0 = tk.Frame(win, border=1, bg="white")
    f0.pack(side="top", fill="x", expand=1, pady=10)
    new_online_b = tk.Button(f0, text="Create new online game", bg="peru", font=("Arial", 12), relief="groove", command=lambda:server("create"))
    new_online_b.pack(side="left", padx=10)
    url_server_label = tk.Label(f0, text=f"{HOST_IP}", font=("Arial", 12), border=2, bg="white")
    url_server_label.pack(side="left", padx=10)
    port_server_entry = tk.Entry(f0, font=("Arial", 12), border=2, bg="white", width=10, relief="groove", justify="center")
    port_server_entry.pack(side="left", padx=10)
    port_server_entry.insert("end", "5000")
    players_label = tk.Label(f0, text="Online players", font=("Arial", 12), border=2, bg="white")
    players_label.pack(side="left", padx=10)
    players_entry = tk.Entry(f0, font=("Arial", 12), border=2, bg="white", width=5, relief="groove", justify="center")
    players_entry.pack(side="left", padx=10)
    players_entry.insert("end", "2")

    # Row
    f1 = tk.Frame(win, border=1, bg="white")
    f1.pack(side="top", fill="x", expand=1, pady=10)
    connect_b = tk.Button(f1, text="Connect to online game", bg="peru", font=("Arial", 12), relief="groove", border=2, padx=5, command=lambda:server("connect"))
    connect_b.pack(side="left", padx=10)
    url_entry = tk.Entry(f1, font=("Arial", 12), border=2, bg="white", relief="groove", justify="center")
    url_entry.pack(side="left", padx=10)
    url_entry.insert("end", HOST_IP)
    port_entry = tk.Entry(f1, font=("Arial", 12), border=2, bg="white", width=10, relief="groove", justify="center")
    port_entry.pack(side="left", padx=10)
    port_entry.insert("end", "5000")

    # Row
    f2 = tk.Frame(win, border=1, bg="white")
    f2.pack(side="top", fill="x", expand=1, pady=10)
    new_game_b = tk.Button(f2, text="Start single-player game", bg="peru", font=("Arial", 12), relief="groove", command=root.destroy)
    new_game_b.pack(side="left", padx=10)
    player_id = tk.Entry(f2, font=("Arial", 12), border=2, bg="white", width=5, relief="groove", justify="center")
    player_id.pack(side="right", padx=10)
    player_id.insert("end", f"{str(PLAYER_ID)}")
    player_id_label = tk.Label(f2, text="Player Online ID", font=("Arial", 12), border=2, bg="white")
    player_id_label.pack(side="right", padx=10)

    output = tk.Text(root, height=15, width=15)
    root.protocol("WM_DELETE_WINDOW", sys.exit)
    root.mainloop()


# START APP -> LOAD RESOURCES, SETTINGS -> GAMEPLAY

if __name__ == "__main__":
    # Online
    PLAYER_ID = 1 # Must be unique among other players on the network
    HOST_IP = socket.gethostbyname(socket.gethostname())
    ONLINE, HOST = None, True
    THREADS_NUMBER, THREADS = 1, []
    DAMAGES = []

    SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 720
    SCALE = 32 # Height and width one tile on map
    GAME_NAME = "Adventurer's Path"

    load_main_menu()

    # Colors
    RED = (255,0,0)
    ORANGE = (255,165,0)
    GREY = (100,100,100)
    WHITE = (255,255,255)
    BROWN = (222,184,135)

    # Create pygame screen
    pygame.init()
    pygame.display.set_icon(pygame.image.load("graphics/sword.png"))
    WINDOW = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), vsync=1)
    pygame.display.set_caption(GAME_NAME)
    CLOCK = pygame.time.Clock()

    # Load assets for map, objects
    MESSAGE_FONT = pygame.font.Font("freesansbold.ttf", 30)
    STAT_FONT = pygame.font.Font("freesansbold.ttf", 15)
    WORLD_MAP_IMG = pygame.image.load("graphics/map/world_map.png").convert()
    WORLD_MAP_RECT = WORLD_MAP_IMG.get_rect()
    SOUNDS, IMAGES = Sounds(), Images()
    ITEMS, SPRITES, TREETOPS, DEAD_NPCS = [], [], [], []
    ITEM_IMG = IMAGES.load("graphics/item.png")
    HUMAN_PERSONS, NPC_PERSONS = [], []

    # Stats for object creation
    PERSONS_STATS = [
        {"obj_type":"player", "health":100, "speed":2, "body":'body_male.png', "hair":"head_hair_blonde.png", "sword_skill":1, "spear_skill":1,
        "head":None, "weapon":2, "torso":11, "hands":None, "legs":16, "belt":19, "feet":21, "behind":None, "shield":None, "inventory":[25,26,27]}, # Numbers point to items ids below

        {"obj_type":"enemy", "health":50, "speed":1, "body":'body_skeleton.png', "hair":None, "sword_skill":1, "spear_skill":1,
        "head":None, "weapon":0, "torso":None, "hands":None, "legs":None, "belt":None, "feet":None, "behind":None, "shield":None, "inventory":[27]}, # Numbers point to items ids below

        {"obj_type":"trader", "health":150, "speed":2, "body":'body_male.png', "hair":None, "sword_skill":5, "spear_skill":1,
        "head":8, "weapon":5, "torso":12, "hands":None, "legs":17, "belt":20, "feet":21, "behind":None, "shield":None, "inventory":[27,1,3,4,5,6,25,26,8,10,12,14,15,17,18,20,22,24], # Numbers point to items ids below
        "dialogs":["Trade ?", "How about trade"]}
    ]
    ITEMS_STATS = [
        # Weapons
        {"id":0, "obj_type":"weapon", "name":"Steel sword", "image":"graphics/sword.png", "anim":"weapon_sword.png", "damage":10, "cooldown":2, "radius":20},
        {"id":1, "obj_type":"weapon", "name":"Great sword", "image":"graphics/sword2.png", "anim":"weapon_sword.png", "damage":15, "cooldown":2, "radius":20},
        {"id":2, "obj_type":"weapon", "name":"Short staff", "image":"graphics/staff.png", "anim":"weapon_staff.png", "damage":10, "cooldown":3, "radius":20},
        {"id":3, "obj_type":"weapon", "name":"Short spear", "image":"graphics/spear.png", "anim":"weapon_spear.png", "damage":15, "cooldown":3, "radius":20},
        {"id":4, "obj_type":"weapon", "name":"Long sword", "image":"graphics/sword_long.png", "anim":"weapon_longsword.png", "damage":20, "cooldown":3, "radius":32},
        {"id":5, "obj_type":"weapon", "name":"Long rapier", "image":"graphics/rapier.png", "anim":"weapon_rapier.png", "damage":20, "cooldown":3, "radius":32},
        {"id":6, "obj_type":"weapon", "name":"Long spear", "image":"graphics/spear_long.png", "anim":"weapon_long_spear.png", "damage":25, "cooldown":4, "radius":42},
        # Outfits
        {"id":7, "obj_type":"head", "name":"Robe hood", "image":None, "anim":"head_robe_hood.png", "armor":0.1},
        {"id":8, "obj_type":"head", "name":"Leather hat", "image":None, "anim":"head_leather_armor_hat.png", "armor":0.2},
        {"id":9, "obj_type":"head", "name":"Chain helmet", "image":None, "anim":"head_chain_armor_helmet.png", "armor":0.4},
        {"id":10, "obj_type":"head", "name":"Plate helmet", "image":None, "anim":"head_plate_armor_helmet.png", "armor":0.5},
        {"id":11, "obj_type":"torso", "name":"Robe shirt", "image":None, "anim":"torso_robe_shirt_brown.png", "armor":0.5},
        {"id":12, "obj_type":"torso", "name":"Leather armor", "image":None, "anim":"torso_leather_armor_torso.png", "armor":1.0},
        {"id":13, "obj_type":"torso", "name":"Chain armor", "image":None, "anim":"torso_chain_armor_torso.png", "armor":1.5},
        {"id":14, "obj_type":"torso", "name":"Plate armor", "image":None, "anim":"torso_plate_armor_torso.png", "armor":2.0},
        {"id":15, "obj_type":"hands", "name":"Armor gloves", "image":None, "anim":"hands_plate_armor_gloves.png", "armor":0.2},
        {"id":16, "obj_type":"legs", "name":"Robe skirt", "image":None, "anim":"legs_robe_skirt.png", "armor":0.1},
        {"id":17, "obj_type":"legs", "name":"Green pants", "image":None, "anim":"legs_pants_greenish.png", "armor":0.3},
        {"id":18, "obj_type":"legs", "name":"Plate pants", "image":None, "anim":"legs_plate_armor_pants.png", "armor":0.5},
        {"id":19, "obj_type":"belt", "name":"Rope belt", "image":None, "anim":"belt_rope.png", "armor":0.1},
        {"id":20, "obj_type":"belt", "name":"Leather belt", "image":None, "anim":"belt_leather.png", "armor":0.2},
        {"id":21, "obj_type":"feet", "name":"Brown shoes", "image":None, "anim":"feet_shoes_brown.png", "armor":0.1},
        {"id":22, "obj_type":"feet", "name":"Plate shoes", "image":None, "anim":"feet_plate_armor_shoes.png", "armor":0.3},
        {"id":23, "obj_type":"behind", "name":"Quiver", "image":None, "anim":"behind_quiver.png", "armor":0.3},
        {"id":24, "obj_type":"shield", "name":"Wood shield", "image":None, "anim":"shield_cutout_body.png", "armor":0.5},
        # Potions, Coins
        {"id":25, "obj_type":"potion", "name":"Health potion", "image":"graphics/potion_h.png", "for_adding":50},
        {"id":26, "obj_type":"potion", "name":"Energy potion", "image":"graphics/potion_e.png", "for_adding":50},
        {"id":27, "obj_type":"coins", "name":"Coins", "image":"graphics/coin.png", "amount":1000}
    ]
    BOXES_STATS = [
        {"id":1, "obj_type":"box", "image":"graphics/box_closed.png", "image_open":"graphics/box_opened.png", "inventory":[25,26,27,14]}
    ]

    # Create items
    for i in ITEMS_STATS:
        if "weapon" in i["obj_type"]:
            item = Weapon(i["id"], i["name"], i["obj_type"], IMAGES.load(i["image"]), i["anim"], i["damage"], i["cooldown"], i["radius"])
        elif "potion" in i["obj_type"]:
            item = Potion(i["id"], i["name"], i["obj_type"], IMAGES.load(i["image"]), i["for_adding"])
        elif "coins" in i["obj_type"]:
            item = Coins(i["id"], i["name"], i["obj_type"], IMAGES.load(i["image"]), i["amount"])
        else:
            item = Outfit(i["id"], i["name"], i["obj_type"], None, i["anim"], i["armor"])
        ITEMS.append(item)

    # Create boxes
    created_boxes = []
    for i in BOXES_STATS:
        # Create box items copy
        for p_item in persons_boxes_items():
            for index,inventory_item in enumerate(i["inventory"]):
                if inventory_item == p_item.id:
                    i["inventory"][index], _ = create_item_copy(p_item)
        # Create box
        box = Box(i["id"], None, i["obj_type"], IMAGES.load(i["image"]), IMAGES.load(i["image_open"]))
        for item in ITEMS:
            if item.id in i["inventory"]:
                if item.obj_type == "coins":
                    item.amount = random.randint(10,item.amount) # Randomize coins amount
                box.inventory.append(item)
        created_boxes.append(box)

    # Create world (map + objects + persons)
    for file_path in ["graphics/map/world_map_borders.csv", "graphics/map/world_map_trees.csv", "graphics/map/world_map_obj.csv"]:
        with open(file_path) as file:
            for y_index,row in enumerate(file):
                row = eval(row)
                y = y_index*SCALE
                for x_index,i in enumerate(row):
                    x = x_index*SCALE
                    if "world_map_borders" in file.name:
                        if i == 0:
                            w = Object(id=0, map=pygame.Rect(x, y, SCALE, SCALE), obj_type="border")
                            SPRITES.append(w)
                    elif "world_map_trees" in file.name:
                        if i != -1:
                            if i in [202,203,250,251,253,254]:
                                t = Object(id=i, map=pygame.Rect(x, y, SCALE, SCALE-10), obj_type="tree")
                                t.image = IMAGES.trees[i]
                                SPRITES.append(t)
                            else:
                                t = Object(id=i, map=pygame.Rect(x, y, SCALE, SCALE), obj_type="tree_up")
                                t.image = IMAGES.trees[i]
                                TREETOPS.append(t)
                    elif "world_map_obj" in file.name:
                        if i == 1:
                            PLAYER = create_person("player")
                            PLAYER.map = pygame.Rect(x, y, SCALE/2, SCALE/2)
                        elif i == 2:
                            ri = random.randint(0,len(ITEMS)-1)
                            item = ITEMS[ri]
                            if item in persons_boxes_items():
                                _ , c_item = create_item_copy(item)
                                c_item.map.x, c_item.map.y = x, y
                            else:
                                item.map.x, item.map.y = x, y
                        elif i == 3:
                            enemy = create_person("enemy")
                            enemy.map = pygame.Rect(x, y, SCALE/2, SCALE/2)
                        elif i == 4:
                            for s in created_boxes:
                                if s.map == None:
                                    s.map = pygame.Rect(x, y, SCALE, SCALE)
                                    s.map.inflate_ip(0,-10)
                                    SPRITES.append(s)
                        elif i == 5:
                            trader = create_person("trader")
                            trader.map = pygame.Rect(x, y, SCALE/2, SCALE/2)
                            trader.capacity = 30

    # On host - create threads for other players. On client - only one thread
    if ONLINE != None:
        for _ in range(THREADS_NUMBER):
            t = OnlineUpdateThread()
            t.start()
            THREADS.append(t)


    # GAMEPLAY
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit_game()

        SOUNDS.play_map_sounds()
        WINDOW.blit(WORLD_MAP_IMG, (0-PLAYER.camera_x, 0-PLAYER.camera_y)) # Draw map

        # Draw objects
        for d in DEAD_NPCS:
            d.draw_person()
        for i in ITEMS:
            if i not in PLAYER.inventory and i.map.x != 0:
                if i.image == None:
                    WINDOW.blit(ITEM_IMG, (i.map.x-PLAYER.camera_x, i.map.y-PLAYER.camera_y))
                else:
                    WINDOW.blit(i.image, (i.map.x-PLAYER.camera_x, i.map.y-PLAYER.camera_y))
        for s in sorted(SPRITES, key=lambda s: s.map.centery):
            if s not in DEAD_NPCS and (s.obj_type == "online_player" or "npc" in s.obj_type) and s.health <= 0:
                DEAD_NPCS.append(s)
            elif s.obj_type == "player" or s.obj_type == "online_player" or "npc" in s.obj_type and s.health > 0:
                s.draw_person()
                s.play_sounds()
            elif s.obj_type == "tree":
                WINDOW.blit(s.image, (s.map.x-PLAYER.camera_x, s.map.y-5-PLAYER.camera_y))
            elif s.obj_type == "box":
                box_image = s.image_open if PLAYER.box == s else s.image
                WINDOW.blit(box_image, (s.map.x-PLAYER.camera_x, s.map.y-5-PLAYER.camera_y))
        for t in TREETOPS:
            WINDOW.blit(t.image, (t.map.x-PLAYER.camera_x, t.map.y-5-PLAYER.camera_y))

        # NPCs
        for s in NPC_PERSONS:
            if s.health > 0:
                s.stats_restoration()
                s.draw_npc_stats()
                if "enemy" in s.obj_type:
                    if HOST == True:
                        s.npc_move_attack()
                elif "trader" in s.obj_type:
                    s.draw_npc_dialogs()
                    if s.under_attack_time != None:
                        s.obj_type = "npc-enemy"

        # Player
        if PLAYER.health > 0:
            PLAYER.clean_showing_item()
            PLAYER.keyboard()
            if PLAYER.inventory_open:
                PLAYER.draw_inventory()
            PLAYER.draw_player_stats()
            PLAYER.stats_restoration()
            PLAYER.camera()
        else:
            PLAYER.inventory_open = False
            if ONLINE == None:
                exit_game()

        pygame.display.flip()
        CLOCK.tick(60) # FPS