import pygame, time, random
from PIL import Image
from pygame.locals import *
from settings import *
from stuff import Coins

class Person():
    def __init__(self, id, health, speed, items, images, body, hair=None, head=None,
        weapon=None, torso=None, hands=None, legs=None, belt=None, feet=None, behind=None, shield=None,
        sword_skill=1, spear_skill=1):
        # Settings
        self.window = pygame.display.get_surface()
        self.stat_font = pygame.font.Font("freesansbold.ttf", 15)
        # Stats
        self.obj_type = "npc-enemy"
        self.id = id
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
        self.images = images.player_images
        self.images_methods = images
        self.movement = None
        self.direction = "y"
        # Inventory
        self.items = items
        self.inventory = []
        self.capacity = 20
        self.inventory_open = False
        self.box = None
        self.trader = None
        self.showing_item = None
        self.show_pos = None
        self.show_item = False
        self.selected = {"head":head, "behind":behind, "belt":belt, "feet":feet,
            "hands":hands, "legs":legs, "torso":torso, "weapon":weapon, "shield":shield}
        self.wear = {"body":body, "head":hair, "behind":None, "belt":None, "feet":None,
            "hands":None, "legs":None, "torso":None, "weapon":None, "shield":None}
        self.hair = hair
        self.add_items()

    def add_items(self):
        for i in self.items:
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

    def draw_person(self, player):
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
            # Merge (body-clothes-belt-behind-shield) images into one + weapon separately and draw on screen
            image_body = choose_animations(direction, self.images[anim]["body"][self.wear["body"]])[int(self.anim_stage)]
            if self.wear["belt"] != None:
                image_belt = choose_animations(direction, self.images[anim]["belt"][self.wear["belt"]])[int(self.anim_stage)]
            else:
                image_belt = None
            if self.wear["behind"] != None:
                image_behind = choose_animations(direction, self.images[anim]["behind"][self.wear["behind"]])[int(self.anim_stage)]
            else:
                image_behind = None
            if (self.wear["shield"] != None and anim == "slash" or self.wear["shield"] != None and anim == "thrust" or
                self.wear["shield"] != None and anim == "walkcycle"):
                image_shield = choose_animations(direction, self.images[anim]["shield"][self.wear["shield"]])[int(self.anim_stage)]
            else:
                image_shield = None
            if anim == "slash" or anim == "thrust":
                image_weapon = choose_animations(direction, self.images[anim]["weapon"][self.wear["weapon"]])[int(self.anim_stage)]
            else:
                image_weapon = None
            image = None
            for part in self.wear:
                if (self.wear[part] != None and
                    part != "body" and part != "belt" and part != "weapon" and part != "behind" and part != "shield"):
                    if image == None:
                        anim_list = choose_animations(direction, self.images[anim][part][self.wear[part]])
                        image = anim_list[int(self.anim_stage)]
                    else:
                        anim_list = choose_animations(direction, self.images[anim][part][self.wear[part]])
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
            img = self.images_methods.pil_img_to_surface(image)
            self.screen = img.get_rect()
            self.screen.center = (self.map.centerx-player.camera_x, self.map.centery-20-player.camera_y)
            self.window.blit(img, self.screen)
            if image_weapon != None:
                img_weapon = self.images_methods.pil_img_to_surface(image_weapon)
                screen_weapon = img_weapon.get_rect()
                screen_weapon.center = (self.map.centerx-player.camera_x, self.map.centery-20-player.camera_y)
                self.window.blit(img_weapon, screen_weapon)
        def animate(direction , anim):
            try:# Periodically play idle(spellcast) animation
                if "go" not in self.move_status and anim == "walkcycle" and self.idle_stage < 50:
                    self.idle_stage += 0.1
                    self.anim_stage = 0
                elif "go" not in self.move_status and anim == "walkcycle" and self.idle_stage > 50:
                    anim = "spellcast"
                    self.anim_stage += 0.2
                    if self.anim_stage >= 7:
                        self.anim_stage = 0
                        self.idle_stage = 0
                        anim = "walkcycle"
                else:# Other animations
                    self.anim_stage += 0.2
                    self.idle_stage = 0
                draw(direction, anim)
            except:# If image animations run out
                if "slash" in anim or "thrust" in anim:
                    self.attack_anim_stop = True
                self.anim_stage = 0
                draw(direction, anim)
        # Person
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
            if "sword" in self.selected["weapon"].anim or "rapier" in self.selected["weapon"].anim:
                if self.move_status == "up":animate("u", "slash")
                elif self.move_status == "down":animate("d", "slash")
                elif self.move_status == "left":animate("l", "slash")
                elif self.move_status == "right":animate("r", "slash")
            elif "staff" in self.selected["weapon"].anim or "spear" in self.selected["weapon"].anim:
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

    def play_sounds(self, sounds):
        if self.under_attack_time != None and self.sound_status["under_attack"] == False:
            pygame.mixer.Sound.set_volume(sounds.sounds[0], 0.4)
            pygame.mixer.Sound.set_volume(sounds.sounds[4], 0.4)
            sounds.sounds[0].play()
            sounds.sounds[4].play()
            self.sound_status["under_attack"] = True
        elif self.attack_time != None and self.attack_anim_stop == False and self.sound_status["attack"] == False:
            pygame.mixer.Sound.set_volume(sounds.sounds[9], 0.4)
            sounds.sounds[9].play()
            self.sound_status["attack"] = True
        else:
            if "go" in self.move_status:
                if self.sound_stage < 2:
                    self.sound_stage = 2
                elif self.sound_stage > 3:
                    self.sound_stage = 2
                if self.sound_stage == 2:
                    s = sounds.sounds[self.sound_stage]
                    pygame.mixer.Sound.set_volume(s, 0.05)
                    s.play()
                self.sound_stage += 0.04
        if self.sound_status["drink_potion"] == True:
            pygame.mixer.Sound.set_volume(sounds.sounds[1], 0.4)
            sounds.sounds[1].play()
            self.sound_status["drink_potion"] = False
        if self.sound_status["inventory_items"] == True:
            pygame.mixer.Sound.set_volume(sounds.sounds[5], 0.4)
            sounds.sounds[5].play()
            self.sound_status["inventory_items"] = False
        if self.sound_status["box"] == True:
            if self.box != None and self.box.obj_type == "box":
                pygame.mixer.Sound.set_volume(sounds.sounds[8], 0.4)
                sounds.sounds[8].play()
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

    def attack(self, sprites):
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
        for o in sprites:
            if self != o:
                if "npc" in o.obj_type and o.health > 0 or o.obj_type == "player" and o.health > 0:
                    if map_weapon.colliderect(o.map):
                        skill = self.selected["weapon"].anim[7:-4]
                        if "spear" in skill or skill == "staff": skill = "spear"
                        elif skill == "longsword" or skill == "rapier": skill = "sword"
                        r_int = random.randint(int(self.skills[skill]), self.selected["weapon"].damage)
                        if self.skills[skill] >= self.selected["weapon"].damage and self.selected["weapon"].damage - o.armor >= 0:
                            o.health -= self.selected["weapon"].damage - o.armor
                        elif self.skills[skill] < self.selected["weapon"].damage and r_int - o.armor >= 0:
                            o.health -= r_int - o.armor
                        self.skills[skill] += 0.01
                        o.under_attack_time = time.time()

    def move(self, direction, sprites):
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
        for s in sprites:
            if self != s and self.map.colliderect(s.map):
                if "up" in self.move_status:
                    self.map.top = s.map.bottom
                elif "down" in self.move_status:
                    self.map.bottom = s.map.top
                elif "left" in self.move_status:
                    self.map.left = s.map.right
                elif "right" in self.move_status:
                    self.map.right = s.map.left

    # Next methods only for Player

    def append_items_from_map(self):
        for i in self.items:
            if i.map.x != 0 and i.map != None:
                if i.map.colliderect(self.map):
                    if len(self.inventory) <= self.capacity and i not in self.inventory:
                        self.inventory.append(i)
                        i.map.x, i.map.y = 0, 0
                        self.sound_status["inventory_items"] = True

    def draw_player_stats(self):
        # Health, energy, cooldown indicator
        pygame.draw.rect(self.window, red, (10, 10, self.health_bar_width, 17), 1)
        pygame.draw.rect(self.window, red, (10, 10, self.health, 17))
        pygame.draw.rect(self.window, orange, (10, 30, self.energy_bar_width, 17), 1)
        pygame.draw.rect(self.window, orange, (10, 30, self.energy, 17))
        if self.attack_time != None:
            self.window.blit(self.stat_font.render("!!!", True, white), (10, 50, 20, 20))
        # Inventory
        if self.inventory_open:
            # Draw inventory info
            inventory_text = self.stat_font.render(f"Player Items", True, white)
            self.window.blit(inventory_text, (screen_width//2, 32, 50, 17))
            # Boxes
            if self.box != None or self.trader != None:
                if self.box != None:
                    text = "NPC Items" if "npc" in self.box.obj_type else "Box Items"
                elif self.trader != None:
                    text = "Trader Items"
                self.window.blit(self.stat_font.render(text, True, white), (screen_width//5, 32, 50, 17))
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
                pygame.draw.rect(self.window, grey, (show_pos2, (155, 25)))
                self.window.blit(self.stat_font.render(f"{text_name} {text}", True, white), (show_pos1, (50, 17)))
            # Damage, armor, skills
            if self.selected["weapon"] != None:
                weapon_damage = self.selected["weapon"].damage
                weapon_text = self.stat_font.render(f"Damage: {str(weapon_damage)}", True, white)
                self.window.blit(weapon_text, (screen_width-120, screen_height//2, 50, 17))
            armor_text = self.stat_font.render(f"Armor: {str(self.armor)}", True, white)
            self.window.blit(armor_text, (screen_width-120, screen_height//2+20, 50, 17))
            self.window.blit(self.stat_font.render("Skills:", True, white), (screen_width-120, screen_height//2+60, 50, 17))
            sword_text = self.stat_font.render(f"Sword: {str(int(self.skills['sword']))}", True, white)
            self.window.blit(sword_text, (screen_width-120, screen_height//2+80, 50, 17))
            spear_text = self.stat_font.render(f"Spear: {str(int(self.skills['spear']))}", True, white)
            self.window.blit(spear_text, (screen_width-120, screen_height//2+100, 50, 17))

    def keyboard(self, sprites):
        pressed = pygame.key.get_pressed()
        if self.attack_time == None and self.under_attack_time == None:
            if pressed[pygame.K_w] and not self.inventory_open and self.trader == None:
                self.move("up", sprites)
            elif pressed[pygame.K_s] and not self.inventory_open and self.trader == None:
                self.move("down", sprites)
            elif pressed[pygame.K_a] and not self.inventory_open and self.trader == None:
                self.move("left", sprites)
            elif pressed[pygame.K_d] and not self.inventory_open and self.trader == None:
                self.move("right", sprites)
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
                    for o in sprites:
                        if self != o:
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
            self.attack(sprites)
            self.energy -= self.selected["weapon"].cooldown*5
            self.attack_time = time.time()

    def draw_inventory(self, sprites):
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
                item.image = self.images_methods.pil_img_to_surface(self.images["walkcycle"][item.obj_type][item.anim][18])
                image = item.image
            else:
                image = item.image
            rect = image.get_rect()
            rect.center = pos.center
            self.window.blit(image, rect)
        self.show_item = False
        # Boxes
        self.box = None
        for s in sprites:
            if "npc" in s.obj_type and s.health <= 0 or s.obj_type == "box":
                if self.map.top == s.map.bottom and self.map.left >= s.map.left-scale and self.map.right <= s.map.right+scale:
                    self.box = s
                elif self.map.bottom == s.map.top and self.map.left >= s.map.left-scale and self.map.right <= s.map.right+scale:
                    self.box = s
                elif self.map.left == s.map.right and self.map.top >= s.map.top-scale and self.map.bottom <= s.map.bottom+scale:
                    self.box = s
                elif self.map.right == s.map.left and self.map.top >= s.map.top-scale and self.map.bottom <= s.map.bottom+scale:
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
                item_pos = pygame.Rect((screen_width//5)+x, y, 64, 64)
                pygame.draw.rect(self.window, brown, item_pos)
                pygame.draw.rect(self.window, grey, item_pos, 1)
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
        # Inventory
        y_index, x_index, item_index = 1, 0, 0
        for i in self.inventory:
            # Draw inventory
            if i not in [self.selected[k] for k in self.selected]:
                if item_index >= 5:
                    y_index += 1
                    item_index = 0
                    x_index = 0
                y, x = y_index*64, x_index*64
                item_pos = pygame.Rect((screen_width//2)+x, y, 64, 64)
                pygame.draw.rect(self.window, brown, item_pos)
                pygame.draw.rect(self.window, grey, item_pos, 1)
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
                            for s in sprites:
                                if s.map.collidepoint(self.map.x-scale, self.map.y-scale):
                                    collide = True
                            if collide == False:
                                i.map.x, i.map.y = self.map.x-scale, self.map.y-scale
                                self.inventory.remove(i)
                        calc_coins(self.inventory)
                x_index += 1
                item_index += 1
            # Draw selected
            else:
                if i.obj_type == "weapon":
                    selected_pos = pygame.Rect(screen_width-64,64,64,64)
                elif i.obj_type == "behind":
                    selected_pos = pygame.Rect(screen_width-64*2,64*2,64,64)
                elif i.obj_type == "head":
                    selected_pos = pygame.Rect(screen_width-64,64*2,64,64)
                elif i.obj_type == "torso":
                    selected_pos = pygame.Rect(screen_width-64,64*3,64,64)
                elif i.obj_type == "hands":
                    selected_pos = pygame.Rect(screen_width-64*3,64*3,64,64)
                elif i.obj_type == "shield":
                    selected_pos = pygame.Rect(screen_width-64*3,64*4,64,64)
                elif i.obj_type == "belt":
                    selected_pos = pygame.Rect(screen_width-64*2,64*3,64,64)
                elif i.obj_type == "legs":
                    selected_pos = pygame.Rect(screen_width-64,64*4,64,64)
                elif i.obj_type == "feet":
                    selected_pos = pygame.Rect(screen_width-64*2,64*4,64,64)
                pygame.draw.rect(self.window, brown, selected_pos)
                pygame.draw.rect(self.window, grey, selected_pos, 1)
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

    def camera(self, world_map_rect):
        right_border = world_map_rect.width - screen_width
        down_border = world_map_rect.height - screen_height
        if self.screen.x < screen_width//2:
            num1 = screen_width//2 - self.screen.x
            if self.camera_x - num1 < 0:
                self.camera_x == 0
            else:
                self.camera_x -= num1
        elif self.screen.x > screen_width//2:
            num1 = self.screen.x - screen_width//2
            if self.camera_x + num1 > right_border:
                self.camera_x = right_border
            else:
                self.camera_x += num1
        if self.screen.y < screen_height//2:
            num1 = screen_height//2 - self.screen.y
            if self.camera_y - num1 < 0:
                self.camera_y == 0
            else:
                self.camera_y -= num1
        elif self.screen.y > screen_height//2:
            num1 = self.screen.y - screen_height//2
            if self.camera_y + num1 > down_border:
                self.camera_y = down_border
            else:
                self.camera_y += num1

    # Next methods only for NPCs

    def calc_distance(self, player, x=None, y=None):
        if x != None:
            if x < player.centerx:
                x_distance = player.centerx - x
            elif x > player.centerx:
                x_distance = x - player.centerx
            else:
                x_distance = 0
        if y != None:
            if y < player.centery:
                y_distance = player.centery - y
            elif y > player.centery:
                y_distance = y - player.centery
            else:
                y_distance = 0
        if x != None and y != None:
            return x_distance, y_distance
        elif x != None:
            return x_distance
        elif y != None:
            return y_distance

    def draw_npc_stats(self, player):
        health_rect = pygame.Rect(0, 0, self.health_bar_width/5, scale/10)
        health_rect_i = pygame.Rect(0, 0, self.health/5, scale/10)
        health_rect.center = (self.map.centerx-player.camera_x, self.map.y-32-player.camera_y)
        health_rect_i.center = (self.map.centerx-player.camera_x, self.map.y-32-player.camera_y)
        pygame.draw.rect(self.window, red, health_rect, 1)
        pygame.draw.rect(self.window, red, health_rect_i)

    def draw_npc_dialogs(self, player):
        if self.health > 0 and player.health > 0 and self.attack_time == None and self.under_attack_time == None:
            x_distance, y_distance = self.calc_distance(player=player.map, x=self.map.centerx, y=self.map.centery)
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
                    if test.colliderect(player.map):
                        self.move_status = status
                # Draw dialogs
                rect_pos = (self.map.x-30-player.camera_x, self.map.y-60-player.camera_y)
                text = self.dialogs[0]
                pygame.draw.rect(self.window, grey, (rect_pos, (50, 17)))
                self.window.blit(self.stat_font.render(text, True, white), (rect_pos, (50, 17)))

    def npc_move_attack(self, player, sprites):
        # NPCs move to player when player in distance
        if self.health > 0 and player.health > 0 and self.attack_time == None and self.under_attack_time == None:
            x_distance, y_distance = self.calc_distance(player=player.map, x=self.map.centerx, y=self.map.centery)
            if x_distance < 200 and y_distance < 200:
                if (x_distance < self.selected["weapon"].radius and y_distance < 10 or
                    y_distance < self.selected["weapon"].radius and x_distance < 10):
                    # Change move status on player direction
                    if "go" in self.move_status:
                        self.move_status = self.move_status[:-3]
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
                    # NPCs attack player
                    if self.selected["weapon"] != None and self.energy >= self.selected["weapon"].cooldown*5:
                        self.attack(sprites)
                        self.energy -= self.selected["weapon"].cooldown*5
                        self.attack_time = time.time()
                else:
                    # Calculate possible moves
                    possible_moves = {"up":0, "down":0, "left":0, "right":0}
                    o1 = self.map
                    for o2 in sprites:#
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
                        possible_moves["up"] = self.calc_distance(player=player.map, y=self.map.centery-self.speed)
                    if "down" in possible_moves:
                        possible_moves["down"] = self.calc_distance(player=player.map, y=self.map.centery+self.speed)
                    if "left" in possible_moves:
                        possible_moves["left"] = self.calc_distance(player=player.map, x=self.map.centerx-self.speed)
                    if "right" in possible_moves:
                        possible_moves["right"] = self.calc_distance(player=player.map, x=self.map.centerx+self.speed)
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
                                    self.move("left", sprites)
                                elif self.map.centerx < player.map.centerx:
                                    self.move("right", sprites)
                                elif self.map.centery > player.map.centery:
                                    self.move("up", sprites)
                                elif self.map.centery < player.map.centery:
                                    self.move("down", sprites)
                            elif "y" in self.direction:
                                if self.map.centery > player.map.centery:
                                    self.move("up", sprites)
                                elif self.map.centery < player.map.centery:
                                    self.move("down", sprites)
                                elif self.map.centerx > player.map.centerx:
                                    self.move("left", sprites)
                                elif self.map.centerx < player.map.centerx:
                                    self.move("right", sprites)
                    elif self.movement != None:
                        for i in self.movement:
                            if i in possible_moves:
                                if self.movement[i] >= 0:
                                    self.move(i, sprites)
                                    self.movement[i] -= self.speed
                                if self.movement[i] <= 0:
                                    self.movement = None
                                else: break
                            else: self.movement = None
            else:
                if "go" in self.move_status:
                    self.move_status = self.move_status[:-3]