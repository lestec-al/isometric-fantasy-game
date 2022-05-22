import pygame, time, random
from PIL import Image
from pygame.locals import *
from settings import *

class Person():
    def __init__(self, id, health, speed, items, images, body, head=None,
        weapon=None, torso=None, hands=None, legs=None, belt=None, feet=None, behind=None,
        sword_skill=1, spear_skill=1):
        # Settings
        self.window = pygame.display.get_surface()
        self.stat_font = pygame.font.Font("freesansbold.ttf", 15)
        # Stats
        self.obj_type = "npc"
        self.id = id
        self.health = health
        self.health_bar_width = health
        self.speed = speed
        self.skills = {"sword":sword_skill, "spear":spear_skill}
        self.armor = 0
        self.energy = 100
        self.energy_bar_width = 100
        # Attack
        self.attacking = False
        self.attack_time = None
        self.attack_stop = False
        # Map
        self.map = None
        self.screen = None
        self.camera_x, self.camera_y = 0, 0
        # Movement, Animations
        self.move_status = "left"
        self.anim_stage = 0
        self.idle_stage = 0
        self.label_armor_images = images.label_armor_images
        self.images = images.player_images
        self.images_methods = images
        self.movement = None
        # Inventory
        self.items = items
        self.inventory_open = False
        self.inventory_map = []
        self.selected = {"head":head if type(head) == type(1) else None,
            "behind":behind, "belt":belt, "feet":feet, "hands":hands, "legs":legs, "torso":torso, "weapon":weapon}
        self.wear = {"body":body, "head":head if type(head) == type("") else None,
            "behind":None, "belt":None, "feet":None, "hands":None, "legs":None, "torso":None, "weapon":None}
        self.add_items()

    # Next methods for Player and NPCs

    def add_items(self):
        for i in self.items:
            for k in self.selected:
                if self.selected[k] != None and self.selected[k] == i.id:
                    self.inventory_map.append(i)
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
            elif direction == "1":
                ready_anim_list = anim_list
            return ready_anim_list
        def blit(direction, anim):# ???
            # Merge images into one (1- body, 2- all, 3- belt, behind, weapon) and blit on screen
            image_body = choose_animations(direction, self.images[anim]["body"][self.wear["body"]])[int(self.anim_stage)]
            if self.wear["belt"] != None:
                image_belt = choose_animations(direction, self.images[anim]["belt"][self.wear["belt"]])[int(self.anim_stage)]
            else:
                image_belt = None
            if self.wear["behind"] != None:
                image_behind = choose_animations(direction, self.images[anim]["behind"][self.wear["behind"]])[int(self.anim_stage)]
            else:
                image_behind = None
            if self.wear["weapon"] != None and anim == "slash" or anim == "thrust":
                image_weapon = choose_animations(direction, self.images[anim]["weapon"][self.wear["weapon"]])[int(self.anim_stage)]
            else:
                image_weapon = None
            image = None
            for part in self.wear:
                if self.wear[part] != None and part != "body" and part != "belt" and part != "weapon":
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
            if image_weapon != None:
                image = Image.alpha_composite(image, image_weapon)
            img = self.images_methods.pil_img_to_surface(image)
            self.screen = img.get_rect()
            self.screen.center = (self.map.centerx-player.camera_x, self.map.centery-6-player.camera_y)# ???
            self.window.blit(img, self.screen)
        def draw(direction , anim):
            try:# Periodically play idle(spellcast) animation
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
                if "slash" in anim or "thrust" in anim:
                    self.attack_stop = True
                self.anim_stage = 0
                blit(direction, anim)
        # Person
        if self.health <= 0:
            try:
                self.anim_stage += 0.1
                blit("1", "hurt")
            except:
                self.anim_stage = 5
                blit("1", "hurt")
            return None
        elif self.attacking and self.attack_stop == False:
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
            # Moving
            if self.move_status == "up-go":draw("u", "walkcycle")
            elif self.move_status == "down-go":draw("d", "walkcycle")
            elif self.move_status == "left-go":draw("l", "walkcycle")
            elif self.move_status == "right-go":draw("r", "walkcycle")
        # Cooldown
        try: cooldown_time = self.selected["weapon"].cooldown_time
        except: cooldown_time = 2
        if self.attack_time != None and time.time() - self.attack_time >= cooldown_time:
            self.attacking = False
            self.attack_stop = False

    def health_energy_restoration(self):# ???
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

    def attack(self, attacker, opponent):
        def attack_1():
            skill = attacker.selected["weapon"].anim[7:-4]
            if skill == "staff": skill = "spear"
            r_int = random.randint(int(attacker.skills[skill]), attacker.selected["weapon"].damage)
            if attacker.skills[skill] >= attacker.selected["weapon"].damage and attacker.selected["weapon"].damage - opponent.armor >= 0:
                opponent.health -= attacker.selected["weapon"].damage - opponent.armor
                attacker.skills[skill] += 0.01
            elif attacker.skills[skill] < attacker.selected["weapon"].damage and r_int - opponent.armor >= 0:
                opponent.health -= r_int - opponent.armor
                attacker.skills[skill] += 0.01
            else:
                opponent.health -= 0
        if attacker.map.top == opponent.map.bottom and attacker.map.left >= opponent.map.left-scale and attacker.map.right <= opponent.map.right+scale:
            attacker.move_status = "up"
            attack_1()
        elif attacker.map.bottom == opponent.map.top and attacker.map.left >= opponent.map.left-scale and attacker.map.right <= opponent.map.right+scale:
            attacker.move_status = "down"
            attack_1()
        elif attacker.map.left == opponent.map.right and attacker.map.top >= opponent.map.top-scale and attacker.map.bottom <= opponent.map.bottom+scale:
            attacker.move_status = "left"
            attack_1()
        elif attacker.map.right == opponent.map.left and attacker.map.top >= opponent.map.top-scale and attacker.map.bottom <= opponent.map.bottom+scale:
            attacker.move_status = "right"
            attack_1()

    def move(self, direction, sprites):
        def handle_collisions(obj1, obj2_list):
            for obj2 in obj2_list:
                if obj1 != obj2:
                    if obj1.map.colliderect(obj2.map):
                        if "up" in obj1.move_status:
                            obj1.map.top = obj2.map.bottom
                        elif "down" in obj1.move_status:
                            obj1.map.bottom = obj2.map.top
                        elif "left" in obj1.move_status:
                            obj1.map.left = obj2.map.right
                        elif "right" in obj1.move_status:
                            obj1.map.right = obj2.map.left
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
        handle_collisions(self, sprites)

    # Next methods only for Player

    def append_items(self):
        for i in self.items:
            if i.map.x != 0:
                if i.map.colliderect(self.map):
                    if len(self.inventory_map) <= 25 and i not in self.inventory_map:
                        self.inventory_map.append(i)
                        i.map.x, i.map.y = 0, 0

    def draw_player_stats(self):
        pygame.draw.rect(self.window, red, (10, 10, self.health_bar_width, 17), 1)
        pygame.draw.rect(self.window, red, (10, 10, self.health, 17))
        pygame.draw.rect(self.window, orange, (10, 30, self.energy_bar_width, 17), 1)
        pygame.draw.rect(self.window, orange, (10, 30, self.energy, 17))
        if self.inventory_open:
            if self.selected["weapon"] != None:
                weapon_damage = self.selected["weapon"].damage
                weapon_text = self.stat_font.render(f"Weapon damage: {str(weapon_damage)}", True, white)
                self.window.blit(weapon_text, (screen_width-180, screen_height//2, 50, 17))
            armor_text = self.stat_font.render(f"Armor protection: {str(self.armor)}", True, white)
            self.window.blit(armor_text, (screen_width-180, screen_height//2+20, 50, 17))
            armor_text = self.stat_font.render(f"Sword skill: {str(int(self.skills['sword']))}", True, white)
            self.window.blit(armor_text, (screen_width-180, screen_height//2+40, 50, 17))
            armor_text = self.stat_font.render(f"Spear skill: {str(int(self.skills['spear']))}", True, white)
            self.window.blit(armor_text, (screen_width-180, screen_height//2+60, 50, 17))         

    def keyboard(self, sprites):
        pressed = pygame.key.get_pressed()
        if self.attacking == False:
            if pressed[pygame.K_w] and not self.inventory_open:
                self.move("up", sprites)
            elif pressed[pygame.K_s] and not self.inventory_open:
                self.move("down", sprites)
            elif pressed[pygame.K_a] and not self.inventory_open:
                self.move("left", sprites)
            elif pressed[pygame.K_d] and not self.inventory_open:
                self.move("right", sprites)
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
        if (pressed[pygame.K_f] and self.selected["weapon"] != None and
            self.attacking == False and"go" not in self.move_status and self.energy > 1 and not self.inventory_open):
            for s in sprites:
                if s.obj_type == "npc":
                    if s.health > 0:
                        self.attack(self, s)
            self.energy -= self.selected["weapon"].cooldown_time*5
            self.attacking = True
            self.attack_time = time.time()

    def draw_inventory(self, sprites):
        def draw_item_ui(item, pos):
            if item.image == None and "Outfit" in str(item):# ???
                item.image = self.images_methods.pil_img_to_surface(self.images["walkcycle"][item.obj_type][item.anim][18])
                image = item.image
            else:
                image = item.image
            rect = image.get_rect()
            rect.center = pos.center
            self.window.blit(image, rect)
        def space_free():
            for s in sprites:
                if s.map.collidepoint(self.map.x-scale, self.map.y-scale):
                    return False
            return True
        # Storages or looting
        storage = None
        for s in sprites:
            if s.obj_type == "npc" and s.health <= 0 or s.obj_type == "storage":
                if self.map.top == s.map.bottom and self.map.left >= s.map.left-scale and self.map.right <= s.map.right+scale:
                    storage = s.inventory_map
                elif self.map.bottom == s.map.top and self.map.left >= s.map.left-scale and self.map.right <= s.map.right+scale:
                    storage = s.inventory_map
                elif self.map.left == s.map.right and self.map.top >= s.map.top-scale and self.map.bottom <= s.map.bottom+scale:
                    storage = s.inventory_map
                elif self.map.right == s.map.left and self.map.top >= s.map.top-scale and self.map.bottom <= s.map.bottom+scale:
                    storage = s.inventory_map          
        if storage != None:
            # Draw storage info
            storage_text = self.stat_font.render(f"Storage Items", True, white)
            self.window.blit(storage_text, (screen_width//5, 32, 50, 17))
            # Draw storage
            y_index, x_index, item_index = 1, 0, 0
            for i in storage:
                if item_index >= 5:
                    y_index += 1
                    item_index = 0
                    x_index = 0
                y = y_index*64
                x = x_index*64
                item_pos = pygame.Rect((screen_width//5)+x, y, 64, 64)
                pygame.draw.rect(self.window, brown, item_pos)
                pygame.draw.rect(self.window, grey, item_pos, 1)
                draw_item_ui(i, item_pos)
                x_index += 1
                item_index += 1
                # Append items to inventory
                if pygame.mouse.get_pressed()[0]:
                    time.sleep(0.1)
                    if item_pos.collidepoint(pygame.mouse.get_pos()):
                        self.inventory_map.append(i)
                        storage.remove(i)
        # Inventory
        y_index, x_index, item_index = 1, 0, 0
        for i in self.inventory_map:
            # Draw inventory info
            storage_text = self.stat_font.render(f"Player Items", True, white)
            self.window.blit(storage_text, (screen_width//2, 32, 50, 17))
            # Draw inventory
            if i not in [self.selected[k] for k in self.selected]:
                if item_index >= 5:
                    y_index += 1
                    item_index = 0
                    x_index = 0
                y = y_index*64
                x = x_index*64
                item_pos = pygame.Rect((screen_width//2)+x, y, 64, 64)
                pygame.draw.rect(self.window, brown, item_pos)
                pygame.draw.rect(self.window, grey, item_pos, 1)
                draw_item_ui(i, item_pos)
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
                                    self.count_armor()
                # Move items from inventory
                if pygame.mouse.get_pressed()[2]:
                    time.sleep(0.1)
                    if item_pos.collidepoint(pygame.mouse.get_pos()):
                        if storage != None:# Add item to the storage
                            self.inventory_map.remove(i)
                            storage.append(i)
                        else:
                            if space_free():# Remove item to map
                                i.map.x, i.map.y = self.map.x-scale, self.map.y-scale
                                self.inventory_map.remove(i)
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
                elif i.obj_type == "belt":
                    selected_pos = pygame.Rect(screen_width-64*2,64*3,64,64)
                elif i.obj_type == "legs":
                    selected_pos = pygame.Rect(screen_width-64,64*4,64,64)
                elif i.obj_type == "feet":
                    selected_pos = pygame.Rect(screen_width-64*2,64*4,64,64)
                pygame.draw.rect(self.window, brown, selected_pos)
                pygame.draw.rect(self.window, grey, selected_pos, 1)
                draw_item_ui(i, selected_pos)
                # Remove items from selected
                if pygame.mouse.get_pressed()[0]:
                    time.sleep(0.1)
                    if selected_pos.collidepoint(pygame.mouse.get_pos()):
                        for k in self.selected:
                            if i == self.selected[k]:
                                    self.selected[k] = None
                                    self.wear[k] = None
                                    self.count_armor()

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

    def draw_npc_stats(self, player):
        health_rect = pygame.Rect(0, 0, self.health_bar_width/5, scale/10)
        health_rect_i = pygame.Rect(0, 0, self.health/5, scale/10)
        health_rect.center = (self.map.centerx-player.camera_x, self.map.y-15-player.camera_y)
        health_rect_i.center = (self.map.centerx-player.camera_x, self.map.y-15-player.camera_y)
        pygame.draw.rect(self.window, red, health_rect, 1)
        pygame.draw.rect(self.window, red, health_rect_i)        

    def npc_movement_attack(self, player, sprites):# ???
        def calc_distance(player, npc=None, x=None, y=None):
            if npc != None:
                if npc.centerx < player.centerx:
                    x_distance = player.centerx - npc.centerx
                elif npc.centerx > player.centerx:
                    x_distance = npc.centerx - player.centerx
                else: x_distance = 0
                if npc.centery < player.centery:
                    y_distance = player.centery - npc.centery
                elif npc.centery > player.centery:
                    y_distance = npc.centery - player.centery
                else: y_distance = 0
                return x_distance, y_distance
            if x != None:
                if x < player.centerx:
                    x_distance = player.centerx - x
                elif x > player.centerx:
                    x_distance = x - player.centerx
                else: x_distance = 0
                return x_distance
            if y != None:
                if y < player.centery:
                    y_distance = player.centery - y
                elif y > player.centery:
                    y_distance = y - player.centery
                else: y_distance = 0
                return y_distance
        def calc_possible_moves(obj1, obj2_list) -> dict:
            moves = {"up":0, "down":0, "left":0, "right":0}
            obj1 = obj1.map
            for obj2 in obj2_list:#
                if obj1 != obj2:
                    obj2 = obj2.map
                    if obj1.top == obj2.bottom and obj1.left >= obj2.left-15 and obj1.right <= obj2.right+15:
                        if "up" in moves: moves.pop("up")
                    elif obj1.bottom == obj2.top and obj1.left >= obj2.left-15 and obj1.right <= obj2.right+15:
                        if "down" in moves: moves.pop("down")
                    if obj1.left == obj2.right and obj1.top >= obj2.top-15 and obj1.bottom <= obj2.bottom+15:
                        if "left" in moves: moves.pop("left")
                    elif obj1.right == obj2.left and obj1.top >= obj2.top-15 and obj1.bottom <= obj2.bottom+15:
                        if "right" in moves: moves.pop("right")
            if "up" in moves:
                moves["up"] = calc_distance(player=player.map, y=self.map.centery - self.speed)
            if "down" in moves:
                moves["down"] = calc_distance(player=player.map, y=self.map.centery + self.speed)
            if "left" in moves:
                moves["left"] = calc_distance(player=player.map, x=self.map.centerx - self.speed)
            if "right" in moves:
                moves["right"] = calc_distance(player=player.map, x=self.map.centerx + self.speed)
            return moves
        # NPCs move to player when player in distance
        if self.health > 0 and player.health > 0 and self.attacking == False:
            x_distance, y_distance = calc_distance(player=player.map, npc=self.map)
            if x_distance < 200 and y_distance < 200:
                # NPCs attack player
                if x_distance < 17 and y_distance < 19:
                    if "go" in self.move_status: self.move_status = self.move_status[:-3]
                    if self.selected["weapon"] != None and self.energy > 1:
                        self.attack(self, player)
                        self.energy -= self.selected["weapon"].cooldown_time*5
                        self.attacking = True
                        self.attack_time = time.time()
                else:
                    possible_moves = calc_possible_moves(self, sprites)#{'up': 57, 'down': 55, 'left': 79, 'right': 81}
                    if len(possible_moves) == 4 and self.movement == None:
                        if self.map.centerx > player.map.centerx and self.map.left != player.map.right:
                            self.move("left", sprites)
                        elif self.map.centerx < player.map.centerx and self.map.right != player.map.left:
                            self.move("right", sprites)
                        elif self.map.centery > player.map.centery and self.map.top != player.map.bottom:
                            self.move("up", sprites)
                        elif self.map.centery < player.map.centery and self.map.bottom != player.map.top:
                            self.move("down", sprites)
                    else:
                        if self.movement == None:
                            if "up" not in possible_moves or "down" not in possible_moves:
                                if "left" in possible_moves:
                                    if self.map.centery < player.map.centery:
                                        self.movement = {"left":35, "down":80}# If several obstacle ???
                                    elif self.map.centery > player.map.centery:
                                        self.movement = {"left":35, "up":80}
                                elif "right" in possible_moves:
                                    if self.map.centery < player.map.centery:
                                        self.movement = {"right":35, "down":80}
                                    elif self.map.centery > player.map.centery:
                                        self.movement = {"right":35, "up":80}
                            if "left" not in possible_moves or "right" not in possible_moves:
                                if "up" in possible_moves:
                                    self.movement = {"up":35}
                                elif "down" in possible_moves:
                                    self.movement = {"down":35}
                        else:
                            for i in self.movement:
                                if self.movement[i] >= 0:
                                    self.move(i, sprites)
                                    self.movement[i] -= self.speed
                                if self.movement[i] <= 0:
                                    if len(self.movement) == 1:
                                        self.movement = None
                                    elif len(self.movement) == 2:
                                        mv = list(self.movement.values())
                                        if mv[0] <= 0 and mv[1] <= 0:
                                            self.movement = None
                                else:
                                    break
            else:
                if "go" in self.move_status: self.move_status = self.move_status[:-3]