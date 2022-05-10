import pygame, os, sys, time, random
from PIL import Image
from pygame.locals import *
from settings import *

class Player():
    def __init__(self, id, health, speed, items, body, head=None,
        weapon=None, torso=None, hands=None, legs=None, belt=None, feet=None, behind=None,
        sword_skill=1, staff_skill=1):

        self.window = pygame.display.get_surface()
        self.stat_font = pygame.font.Font("freesansbold.ttf", 15)

        self.obj_type = "npc"
        self.skills = {"sword":sword_skill, "staff":staff_skill}
        self.armor = 0
        self.id = id
        self.health = health
        self.health_bar_width = health
        self.speed = speed
        self.attacking = False
        self.attack_time = None

        self.map = None
        self.screen = None
        self.camera_x, self.camera_y = 0, 0
        self.move_status = "left"
        self.anim_stage = 0
        self.idle_stage = 0
        self.images = {
            "bow":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}},
            "hurt":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}},
            "slash":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}},
            "spellcast":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}},
            "thrust":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}},
            "walkcycle":{"body":{}, "head":{}, "behind":{}, "belt":{}, "feet":{}, "hands":{}, "legs":{}, "torso":{}, "weapon":{}}}
        self.add_images()

        self.inventory_open = False
        self.inventory_map = []
        self.selected = {"head":head if type(head) == type(1) else None,
            "behind":behind, "belt":belt, "feet":feet, "hands":hands, "legs":legs, "torso":torso, "weapon":weapon}
        self.wear = {"body":body, "head":head if type(head) == type("") else None,
            "behind":None, "belt":None, "feet":None, "hands":None, "legs":None, "torso":None, "weapon":None}
        # Adding items when creating a player
        for i in items:
            for k in self.selected:
                if self.selected[k] != None and self.selected[k] == i.id:
                    self.inventory_map.append(i)
                    self.selected[k] = i
                    self.wear[k] = i.anim
                    if k != "weapon" and k != "behind":# Armor indicator
                        self.armor += i.armor

    def add_images(self):
        """For Player and NPCs"""
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
                        for k in self.images[folder]:
                            if k in img_big:
                                try:
                                    self.images[folder][k][img_big].append(img)
                                except KeyError:
                                    self.images[folder][k][img_big] = []
                                    self.images[folder][k][img_big].append(img)
                        c_i += 64
                    r_i += 64

    def draw_player(self, player):
        """For Player and NPCs"""
        def choose_animations(direction, anim_list):
            index1 = len(anim_list)//4
            if direction == "u":
                ready_anim_list = anim_list[0:index1]
            elif direction == "l":
                ready_anim_list = anim_list[index1:index1*2]
            elif direction == "d":
                ready_anim_list = anim_list[index1*2:index1*3]
            elif direction == "r":
                ready_anim_list = anim_list[index1*3:]
            elif direction == "1":
                ready_anim_list = anim_list
            return ready_anim_list
        def blit(direction, anim):
            # Merge images into one and blit on screen
            #pygame.draw.rect(self.window, white, ((self.map.x-player.camera_x, self.map.y-player.camera_y), self.map.size), 1)# Test
            image = None
            image_body = None
            image_belt = None
            for part in self.wear:
                if self.wear[part] != None and part == "body":
                    anim_list = choose_animations(direction, self.images[anim][part][self.wear[part]])
                    image_body = anim_list[int(self.anim_stage)]
                if self.wear[part] != None and part == "belt":
                    anim_list = choose_animations(direction, self.images[anim][part][self.wear[part]])
                    image_belt = anim_list[int(self.anim_stage)]
                elif self.wear[part] != None and part == "weapon":
                    if anim == "slash" or anim == "thrust":
                        anim_list = choose_animations(direction, self.images[anim][part][self.wear[part]])
                        image = Image.alpha_composite(image, anim_list[int(self.anim_stage)])
                elif self.wear[part] != None and "body_" not in self.wear[part]:
                    if image == None:
                        anim_list = choose_animations(direction, self.images[anim][part][self.wear[part]])
                        image = anim_list[int(self.anim_stage)]
                    else:
                        anim_list = choose_animations(direction, self.images[anim][part][self.wear[part]])
                        image = Image.alpha_composite(image, anim_list[int(self.anim_stage)])
            image = Image.alpha_composite(image_body, image)
            if image_belt != None:
                image = Image.alpha_composite(image, image_belt)
            img = pil_img_to_surface(image)
            self.screen = img.get_rect()
            self.screen.center = (self.map.centerx-player.camera_x, self.map.centery-6-player.camera_y)# ???
            self.window.blit(img, self.screen)
        def draw(direction , anim):
            try:# Periodically play idle animation
                if "spellcast" in anim and self.idle_stage < 30:
                    self.idle_stage += 0.1
                    self.anim_stage = 0
                elif "spellcast" in anim and self.idle_stage > 30:
                    self.anim_stage += 0.2
                    if self.anim_stage >= 7:
                        self.anim_stage = 0
                        self.idle_stage = 0
                else:# Other animations
                    self.anim_stage += 0.2
                    self.idle_stage = 0
                blit(direction, anim)
            except:# If image animations run out
                self.anim_stage = 0
                blit(direction, anim)
        # Player
        if self.health <= 0:
            try:
                self.anim_stage += 0.1
                blit("1", "hurt")
            except:
                self.anim_stage = 5
                blit("1", "hurt")
            return None
        elif self.attacking:
            if time.time() - self.attack_time >= self.selected["weapon"].cooldown_time:
                self.attacking = False
            if "sword" in self.selected["weapon"].anim:
                if self.move_status == "up":draw("u", "slash")
                elif self.move_status == "down":draw("d", "slash")
                elif self.move_status == "left":draw("l", "slash")
                elif self.move_status == "right":draw("r", "slash")
            elif "staff" in self.selected["weapon"].anim or "spear" in self.selected["weapon"].anim:
                if self.move_status == "up":draw("u", "thrust")
                elif self.move_status == "down":draw("d", "thrust")
                elif self.move_status == "left":draw("l", "thrust")
                elif self.move_status == "right":draw("r", "thrust")
        else:
            if self.move_status == "up":draw("u", "spellcast")
            elif self.move_status == "down":draw("d", "spellcast")
            elif self.move_status == "left":draw("l", "spellcast")
            elif self.move_status == "right":draw("r", "spellcast")

            if self.move_status == "up-go":draw("u", "walkcycle")
            elif self.move_status == "down-go":draw("d", "walkcycle")
            elif self.move_status == "left-go":draw("l", "walkcycle")
            elif self.move_status == "right-go":draw("r", "walkcycle")

    def attack(self, attacker, opponent):
        """For Player and NPCs"""
        def attack_1():
            skill = attacker.selected["weapon"].anim[7:-4]
            if attacker.skills[skill] >= attacker.selected["weapon"].damage:
                if attacker.selected["weapon"].damage - opponent.armor >= 0:
                    opponent.health -= attacker.selected["weapon"].damage - opponent.armor
                else:
                    opponent.health -= 0
            else:
                r_int = random.randint(attacker.skills[skill], attacker.selected["weapon"].damage)
                if r_int - opponent.armor  >= 0:
                    opponent.health -= r_int - opponent.armor
                else:
                    opponent.health -= 0
            attacker.attacking = True
            attacker.attack_time = time.time()
        if attacker.map.top == opponent.map.bottom and attacker.map.left >= opponent.map.left-scale and attacker.map.right <= opponent.map.right+scale:
            attacker.move_status = "up"
            attack_1()
        if attacker.map.bottom == opponent.map.top and attacker.map.left >= opponent.map.left-scale and attacker.map.right <= opponent.map.right+scale:
            attacker.move_status = "down"
            attack_1()
        if attacker.map.left == opponent.map.right and attacker.map.top >= opponent.map.top-scale and attacker.map.bottom <= opponent.map.bottom+scale:
            attacker.move_status = "left"
            attack_1()
        if attacker.map.right == opponent.map.left and attacker.map.top >= opponent.map.top-scale and attacker.map.bottom <= opponent.map.bottom+scale:
            attacker.move_status = "right"
            attack_1()

    def keyboard(self, sprites):
        """For Player only"""
        def move(direction):
            def handle_collisions(direction, object1, object2_list):
                for object2 in object2_list:
                    object2 = object2.map
                    if object1 != object2:
                        if object1.colliderect(object2):
                            if direction == "y-":
                                object1.top = object2.bottom
                            elif direction == "y+":
                                object1.bottom = object2.top
                            elif direction == "x-":
                                object1.left = object2.right
                            elif direction == "x+":
                                object1.right = object2.left
            if direction == "y-":
                self.map.y -= self.speed
            elif direction == "y+":
                self.map.y += self.speed
            elif direction == "x-":
                self.map.x -= self.speed
            elif direction == "x+":
                self.map.x += self.speed
            handle_collisions(direction, self.map, sprites)
        pressed = pygame.key.get_pressed()
        if self.attacking == False:
            if pressed[pygame.K_w]:
                move("y-")
                self.move_status = "up-go"
            elif pressed[pygame.K_s]:
                move("y+")
                self.move_status = "down-go"
            elif pressed[pygame.K_a]:
                move("x-")
                self.move_status = "left-go"
            elif pressed[pygame.K_d]:
                move("x+")
                self.move_status = "right-go"
            else:
                if "go" in self.move_status:
                    self.move_status = self.move_status[:-3]
            if pressed[pygame.K_i]:
                time.sleep(0.2)
                if self.inventory_open == False:
                    self.inventory_open = True
                elif self.inventory_open == True:
                    self.inventory_open = False
        # Attack
        if pressed[pygame.K_f] and self.selected["weapon"] != None and self.attacking == False and "go" not in self.move_status:
            for s in sprites:
                if s.obj_type == "npc":
                    if s.health > 0:
                        self.attack(self, s)

    def append_items(self, items):
        """For Player only"""
        for i in items:
            if i.map.x != 0:
                if i.map.colliderect(self.map):
                    if len(self.inventory_map) <= 25 and i not in self.inventory_map:
                        self.inventory_map.append(i)
                        i.map.x, i.map.y = 0, 0

    def draw_inventory(self, sprites):
        """For Player only"""
        def blit_item(item, pos):
            try:image = pil_img_to_surface(self.images["walkcycle"][item.obj_type][item.anim][18])
            except:image = item.image
            if item.image == None:item.image = image
            rect = image.get_rect()
            rect.center = pos.center
            self.window.blit(image, rect)
        def space_free():
            for s in sprites:
                if s.map.collidepoint(self.map.x-32, self.map.y-32):
                    return False
            return True
        # Stats
        pygame.draw.rect(self.window, red, (screen_width-scale*2, 10, self.health_bar_width, 17), 1)
        pygame.draw.rect(self.window, red, (screen_width-scale*2, 10, self.health, 17))
        armor_text = self.stat_font.render(f"Armor: {str(self.armor)}", True, white)
        self.window.blit(armor_text, (screen_width-scale*3, scale, 50, 17))
        armor_text = self.stat_font.render(f"Sword: {str(self.skills['sword'])}", True, white)
        self.window.blit(armor_text, (screen_width-scale*3, scale+21, 50, 17))
        armor_text = self.stat_font.render(f"Staff: {str(self.skills['staff'])}", True, white)
        self.window.blit(armor_text, (screen_width-scale*3, scale+42, 50, 17))
        # Inventory
        y_index, x_index, item_index = 1, 0, 0
        for i in self.inventory_map:
            # Draw inventory
            if i not in [self.selected[k] for k in self.selected]:
                if item_index >= 5:
                    y_index += 1
                    item_index = 0
                    x_index = 0
                y = y_index*scale
                x = x_index*scale
                item_pos = pygame.Rect((screen_width//2)+x, y, scale, scale)
                pygame.draw.rect(self.window, brown, item_pos)
                pygame.draw.rect(self.window, grey, item_pos, 1)
                blit_item(i, item_pos)
                # Use items
                if pygame.mouse.get_pressed()[0]:
                    time.sleep(0.1)
                    if item_pos.collidepoint(pygame.mouse.get_pos()):
                        if "_potion" in i.obj_type:
                            i.drink_potion(self)
                            self.inventory_map.remove(i)
                            del i
                        else:# Add items to selected
                            for k in self.selected:
                                if i.obj_type == k:
                                    self.selected[k] = i
                                    self.wear[k] = i.anim
                                    if k != "weapon" and k != "behind":# Armor bar
                                        self.armor += i.armor
                # Remove items from inventory
                if pygame.mouse.get_pressed()[2]:
                    time.sleep(0.1)
                    if item_pos.collidepoint(pygame.mouse.get_pos()):
                        if space_free():
                            i.map.x, i.map.y = self.map.x-scale, self.map.y-scale
                            self.inventory_map.remove(i)
                x_index += 1
                item_index += 1
            # Draw selected
            else:
                if i.obj_type == "weapon":
                    selected_pos = pygame.Rect(screen_width-scale,scale, scale, scale)
                elif i.obj_type == "behind":
                    selected_pos = pygame.Rect(screen_width-scale*2,scale*2, scale, scale)
                elif i.obj_type == "head":
                    selected_pos = pygame.Rect(screen_width-scale,scale*2, scale, scale)
                elif i.obj_type == "torso":
                    selected_pos = pygame.Rect(screen_width-scale,scale*3, scale, scale)
                elif i.obj_type == "hands":
                    selected_pos = pygame.Rect(screen_width-scale*3,scale*3, scale, scale)
                elif i.obj_type == "belt":
                    selected_pos = pygame.Rect(screen_width-scale*2,scale*3, scale, scale)
                elif i.obj_type == "legs":
                    selected_pos = pygame.Rect(screen_width-scale,scale*4, scale, scale)
                elif i.obj_type == "feet":
                    selected_pos = pygame.Rect(screen_width-scale*2,scale*4, scale, scale)
                pygame.draw.rect(self.window, brown, selected_pos)
                pygame.draw.rect(self.window, grey, selected_pos, 1)
                blit_item(i, selected_pos)
                # Remove items from selected
                if pygame.mouse.get_pressed()[0]:
                    time.sleep(0.1)
                    if selected_pos.collidepoint(pygame.mouse.get_pos()):
                        for k in self.selected:
                            if i == self.selected[k]:
                                    self.selected[k] = None
                                    self.wear[k] = None
                                    if k != "weapon" and k != "behind":# Armor indicator
                                        self.armor -= i.armor

    def camera(self, world_map_rect):
        """Move camera when player moved. For Player only"""
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

    def npc_plus(self, player):# ???
        """For NPCs only"""
        # Draw NPC health
        health_rect = pygame.Rect(0, 0, self.health_bar_width/5, scale/10)
        health_rect_i = pygame.Rect(0, 0, self.health/5, scale/10)
        health_rect.center = (self.map.centerx-player.camera_x, self.map.y-15-player.camera_y)
        health_rect_i.center = (self.map.centerx-player.camera_x, self.map.y-15-player.camera_y)
        pygame.draw.rect(self.window, red, health_rect, 1)
        pygame.draw.rect(self.window, red, health_rect_i)
        # NPC attack player
        if self.health > 0 and player.health > 0 and self.attacking == False:
            self.attack(self, player)