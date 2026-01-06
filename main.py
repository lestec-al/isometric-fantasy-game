ON_ANDROID = False  # Change this to "True" before compilation on Android

import json
import os
import pygame
import random
import socket
import sys
import threading
import time
import string
from PIL import Image

if ON_ANDROID:
    import plyer
    # noinspection PyPackageRequirements
    import android  # type: ignore
    # noinspection PyPackageRequirements
    from android.storage import app_storage_path  # type: ignore

    MAIN_PATH = os.path.join(app_storage_path(), "app")
else:
    MAIN_PATH = ""

GRAPH_PATH = os.path.join(MAIN_PATH, "data", "graphics")
SOUND_PATH = os.path.join(MAIN_PATH, "data", "sounds")
OBJECTS_PATH = os.path.join(MAIN_PATH, "data", "game_objects.json")

SCALE = 3  # Must be the same in all players on the network
FPS = 60
THREADS_NUMBER = 1
ONLINE: socket.socket or None
MOBILE_MOVEMENT_ON = False
X_MOBILE, Y_MOBILE = None, None
IS_HOST: bool
PLAYER_ID: int
WIDTH: int
HEIGHT: int
TILE_SIZE: int
DAMAGES: list
HUMAN_PERSONS: list
NPC_PERSONS: list
ITEMS: list
SPRITES: list
TREETOPS: list
DEAD_NPC: list
WINDOW: pygame.Surface
FONT: pygame.font.Font
PLAYER: "Person"
SOUNDS: "Sounds"
IMAGES: "Images"
WORLD_MAP_RECT: pygame.Rect
GAME_OBJECTS: dict

BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
GREY = (102, 102, 102)
WHITE = (255, 255, 255)
BROWN = (222, 184, 135)


# MAIN ASSETS
class EditText:
    letters = [f"K_{i}" for i in list(string.ascii_lowercase)]
    specials = {"K_COMMA":",", "K_SEMICOLON":":", "K_PERIOD":".", "K_SLASH":"/"}
    digits = [f"K_{i}" for i in list(string.digits)]
    constants = vars(pygame.constants).items()
    selected_by_label = ""

    def __init__(
            self,
            text: str,
            label: str,
            size: int,
            color: tuple[int, int, int],
            # left, right, width
            pos: tuple[float, float, float],
            enabled = True
    ):
        self.text = text
        self.label = label
        self.color = color
        self.pos_x = int(pos[0])
        self.pos_y = int(pos[1])
        self.width = None if pos[2] == None else int(pos[2])
        self.font = pygame.font.Font("freesansbold.ttf", size)
        self.is_edit = False
        self.enabled = enabled

    def on_tick(self, events: list[pygame.event.Event]):
        if self.is_edit and self.enabled:
            self._check_typing(events)
        rect = self._draw()
        if self.enabled:
            self._check_if_pressed_set_is_edit(rect)

    def _check_if_pressed_set_is_edit(self, rect: pygame.Rect):
        if rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.is_edit = not self.is_edit
            if self.is_edit:
                EditText.selected_by_label = self.label
                pygame.key.start_text_input()
            time.sleep(0.3)

        if EditText.selected_by_label != self.label:
            self.is_edit = False

    def _check_typing(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if len(self.text) > 0:
                        self.text = self.text[0:-1]
                for name, value in self.constants:
                    if event.key == value:
                        if name in self.letters or name in self.digits:
                            self.text += name[2:]
                        if name in self.specials.keys():
                            self.text += self.specials[name]

    def _draw(self):
        # Label
        label_surface = self.font.render(self.label, True, GREY)
        label_rect = label_surface.get_rect()
        label_rect.x = self.pos_x + 10
        label_rect.y = self.pos_y + 10
        if self.width != None:
            label_rect.width = self.width
        WINDOW.blit(label_surface, label_rect)
        # Text
        text_surface = self.font.render(self.text, True, self.color)
        text_rect = text_surface.get_rect()
        text_rect.x = self.pos_x + 10
        text_rect.y = self.pos_y + 10 + label_rect.height
        WINDOW.blit(text_surface, text_rect)
        # Border
        if self.enabled:
            border_rect = label_rect.copy()
            border_rect.x = self.pos_x
            border_rect.y = self.pos_y
            label_width = label_rect.width if label_rect.width > text_rect.width else text_rect.width
            border_rect.width = label_width + 20
            border_rect.height = text_rect.height + label_rect.height + 20
            border_color = BROWN if self.is_edit else GREY
            pygame.draw.rect(WINDOW, border_color, border_rect, width=2, border_radius=10)
            return border_rect
        else:
            return None


class Text:
    """This module provide basic text on screen"""
    def __init__(
            self,
            pos: tuple[float, float, float, float],
            text: str,
            color: tuple[int, int, int],
            size: int,
            shadow = False,
            centered = True
    ):
        self.pos = pygame.Rect(pos)
        self.text = text
        self.color = color
        self.size = size
        self.shadow = shadow
        self.centered = centered

    def draw(self):
        if self.shadow:
            font_border = pygame.font.Font("freesansbold.ttf", self.size)
            surface = font_border.render(self.text, True, BLACK)
            if self.centered:
                rect = surface.get_rect()
                rect.center = self.pos.move(0, 4).center
                WINDOW.blit(surface, rect)
            else:
                rect = surface.get_rect()
                rect.centery = self.pos.move(0, 4).centery
                rect.x = self.pos.x
                WINDOW.blit(surface, rect)
        # Text itself
        font = pygame.font.Font("freesansbold.ttf", self.size)
        surface = font.render(self.text, True, self.color)
        if self.centered:
            rect = surface.get_rect()
            rect.center = self.pos.center
            WINDOW.blit(surface, rect)
        else:
            rect = surface.get_rect()
            rect.centery = self.pos.centery
            rect.x = self.pos.x
            WINDOW.blit(surface, rect)


class Button:
    """This module provide basic button functionality"""
    def __init__(
            self,
            pos: tuple[float, float, float, float],
            icon: pygame.Surface = None,
            is_border = False
    ):
        self.pos = pygame.Rect(pos)
        self.icon = icon
        self.is_border = is_border
        self.is_clicked = False

    def _draw(self):
        pygame.draw.rect(WINDOW, BROWN, self.pos, border_radius=100)
        if self.is_clicked:
            pygame.draw.rect(WINDOW, BLACK, self.pos, width=10, border_radius=100)
        if self.is_border:
            pygame.draw.rect(WINDOW, BLACK, self.pos, width=2, border_radius=100)
        if self.icon != None:
            rect = self.icon.get_rect()
            rect.center = self.pos.center
            WINDOW.blit(self.icon, rect)

    def draw_get_is_clicked(self) -> bool:
        self._draw()
        return self.pos.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]


class Sounds:
    """This module provide all sounds in the game"""
    def __init__(self):
        self.sound_status = {"nature": 0.0, "ocean": 0.0}
        self.all = []
        # Add all sounds
        for file in os.listdir(SOUND_PATH):
            self.all.append(pygame.mixer.Sound(os.path.join(SOUND_PATH, file)))

    def play_map_sounds(self):
        if self.sound_status["nature"] == 0.0:
            pygame.mixer.Sound.set_volume(self.all[7], 0.5)
            self.all[7].play()
            self.sound_status["nature"] = time.time()
        else:
            if time.time() - self.sound_status["nature"] >= self.all[7].get_length():
                self.sound_status["nature"] = 0.0
        if self.sound_status["ocean"] == 0.0:
            pygame.mixer.Sound.set_volume(self.all[6], 0.05)
            self.all[6].play()
            self.sound_status["ocean"] = time.time()
        else:
            if time.time() - self.sound_status["ocean"] >= self.all[6].get_length():
                self.sound_status["ocean"] = 0.0


class Images:
    """This module provide all images (sprites) in the game"""
    def __init__(self):
        self.trees = []
        self.player = {
            "bow": {"body": {}, "head": {}, "behind": {}, "belt": {}, "feet": {}, "hands": {},
                    "legs": {}, "torso": {}, "weapon": {}, "shield": {}},
            "hurt": {"body": {}, "head": {}, "behind": {}, "belt": {}, "feet": {}, "hands": {},
                     "legs": {}, "torso": {}, "weapon": {}, "shield": {}},
            "slash": {"body": {}, "head": {}, "behind": {}, "belt": {}, "feet": {}, "hands": {},
                      "legs": {}, "torso": {}, "weapon": {}, "shield": {}},
            "spellcast": {"body": {}, "head": {}, "behind": {}, "belt": {}, "feet": {}, "hands": {},
                          "legs": {}, "torso": {}, "weapon": {}, "shield": {}},
            "thrust": {"body": {}, "head": {}, "behind": {}, "belt": {}, "feet": {}, "hands": {},
                       "legs": {}, "torso": {}, "weapon": {}, "shield": {}},
            "walkcycle": {"body": {}, "head": {}, "behind": {}, "belt": {}, "feet": {}, "hands": {},
                          "legs": {}, "torso": {}, "weapon": {}, "shield": {}}}
        self.add_player_images()
        self.add_images(
            self.trees,
            os.path.join(GRAPH_PATH, "map", "wood_tileset.png"),
            32
        )

    def add_player_images(self):
        for folder in os.listdir(os.path.join(GRAPH_PATH, "player")):
            for img_big in os.listdir(os.path.join(GRAPH_PATH, "player", folder)):
                i = Image.open(os.path.join(GRAPH_PATH, "player", folder, img_big))
                width, height = i.width, i.height
                img_scale = 192 if img_big in "weapon_longsword.png|weapon_rapier.png|weapon_long_spear.png" else 64
                w, h = int(width / img_scale), int(height / img_scale)
                left, upper, right, lower = 0, 0, img_scale, img_scale
                r_i = 0
                for _ in range(h):
                    c_i = 0
                    for _ in range(w):
                        img = i.crop((left + c_i, upper + r_i, right + c_i, lower + r_i))
                        for k in self.player[folder]:
                            if k in img_big:
                                try:
                                    self.player[folder][k][img_big].append(img)
                                except KeyError:
                                    self.player[folder][k][img_big] = []
                                    self.player[folder][k][img_big].append(img)
                        c_i += img_scale
                    r_i += img_scale

    def add_images(self, result: list, path: str, graph_tileset_scale: int):
        i = Image.open(path)
        width, height = i.width, i.height
        w, h = int(width / graph_tileset_scale), int(height / graph_tileset_scale)
        left, upper, right, lower = 0, 0, graph_tileset_scale, graph_tileset_scale
        r_i = 0
        for _ in range(h):
            c_i = 0
            for _ in range(w):
                image = i.crop((left + c_i, upper + r_i, right + c_i, lower + r_i))
                img = self.pil_img_to_surface(image)
                result.append(img)
                c_i += graph_tileset_scale
            r_i += graph_tileset_scale

    def pil_img_to_surface(self, pil_img):
        image_orig = pygame.image.fromstring(pil_img.tobytes(), pil_img.size, pil_img.mode)
        return pygame.transform.scale(
            image_orig,
            (image_orig.get_width() * SCALE, image_orig.get_height() * SCALE)
        ).convert_alpha()

    def load32(self, image_path):
        """Resizing original image to (32px * scale)"""
        return pygame.transform.scale(
            pygame.image.load(os.path.join(GRAPH_PATH ,image_path)),
            (TILE_SIZE, TILE_SIZE)
        ).convert_alpha()

    def load_map(self, image_path):
        """Resizing original image to scale"""
        image_orig = pygame.image.load(os.path.join(GRAPH_PATH ,image_path))
        return pygame.transform.scale(
            image_orig,
            (image_orig.get_width() * SCALE, image_orig.get_height() * SCALE)
        ).convert()


# GAME OBJECTS
class Object:
    def __init__(self, obj_id, obj_map, obj_type):
        self.obj_id = obj_id
        self.obj_map = obj_map
        self.obj_type = obj_type
        self.image = None


class Box(Object):
    def __init__(self, obj_id, obj_map, obj_type, image, image_open):
        super().__init__(obj_id, obj_map, obj_type)
        self.image = image
        self.image_open = image_open
        self.inventory = []
        self.capacity = 30


class Item(Object):
    def __init__(self, obj_id, name, obj_type, image):
        super().__init__(obj_id, pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE), obj_type)
        self.name = name
        self.image = image


class Weapon(Item):
    def __init__(self, obj_id, name, obj_type, image, anim, damage, cooldown, radius):
        super().__init__(obj_id, name, obj_type, image)
        self.anim = anim
        self.damage = damage
        self.cooldown = cooldown
        self.radius = radius


class Outfit(Item):
    def __init__(self, obj_id, name, obj_type, image, anim, armor):
        super().__init__(obj_id, name, obj_type, image)
        self.anim = anim
        self.armor = armor


class Potion(Item):
    def __init__(self, obj_id, name, obj_type, image, for_adding):
        super().__init__(obj_id, name, obj_type, image)
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
    def __init__(self, obj_id, name, obj_type, image, amount):
        super().__init__(obj_id, name, obj_type, image)
        self.amount = amount


# PLAYERS, NPCs
class Person(Object):
    """
    Class for representing players and NPCs. Handles all sorts of things like stats, movement,
    attacks, inventory, etc.
    """
    def __init__(
            self,
            health,
            speed,
            body,
            sword_skill=1,
            spear_skill=1,
            hair=None,
            head=None,
            weapon=None,
            torso=None,
            hands=None,
            legs=None,
            belt=None,
            feet=None,
            behind=None,
            shield=None
    ):
        super().__init__(None, None, "npc-enemy")
        # Stats
        self.health = health
        self.health_bar_width = health
        self.speed = speed
        self.skills = {"sword": sword_skill, "spear": spear_skill}
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
        self.sound_status = {
            "attack": False,
            "under_attack": False,
            "drink_potion": False,
            "inventory_items": False,
            "box": False
        }
        self.sound_stage = 0
        # Map
        self.screen = None
        self.camera_x, self.camera_y = 0, 0
        # Movement, Animations
        self.move_status = "right"
        self.anim_stage = 0
        self.idle_stage = 0
        self.movement = None  # npc
        self.direction = "y"  # npc
        # Inventory
        self.inventory = []
        self.capacity = 20
        self.inventory_open = False
        self.box = None
        self.trader = None
        self.selected = {
            "head": head,
            "behind": behind,
            "belt": belt,
            "feet": feet,
            "hands": hands,
            "legs": legs,
            "torso": torso,
            "weapon": weapon,
            "shield": shield
        }
        self.wear = {
            "body": body,
            "head": hair,
            "behind": None,
            "belt": None,
            "feet": None,
            "hands": None,
            "legs": None,
            "torso": None,
            "weapon": None,
            "shield": None
        }
        self.hair = hair
        # Add selected items to inventory and to wearing (id -> item)
        for i1 in ITEMS:
            for s1 in self.selected:
                if self.selected[s1] != None and self.selected[s1] == i1.obj_id:
                    if i1 not in self.inventory:
                        self.inventory.append(i1)
                    self.selected[s1] = i1
                    self.wear[s1] = i1.anim
        self.count_armor()

    def count_armor(self):
        self.armor = 0
        for k in self.selected:
            if self.selected[k] != None and k != "weapon" and k != "behind":
                if k == "head":
                    # noinspection PyBroadException
                    try:
                        self.armor += self.selected[k].armor
                    except:
                        pass
                else:
                    self.armor += self.selected[k].armor

    def draw_person(self):
        def choose_animations(direction, anim_list):
            index = len(anim_list) // 4
            if direction == "u":
                ready_anim_list = anim_list[0:index]
            elif direction == "l":
                ready_anim_list = anim_list[index:index * 2]
            elif direction == "d":
                ready_anim_list = anim_list[index * 2:index * 3]
            elif direction == "r":
                ready_anim_list = anim_list[index * 3:]
            else:  # direction == "hurt":
                ready_anim_list = anim_list
            return ready_anim_list

        def draw(direction, anim):
            # Merge (body-clothes-belt-behind-shield) images into one + weapon separately
            image_body = choose_animations(
                direction,
                IMAGES.player[anim]["body"][self.wear["body"]]
            )[int(self.anim_stage)]
            if self.wear["belt"] != None:
                image_belt = choose_animations(
                    direction,
                    IMAGES.player[anim]["belt"][self.wear["belt"]]
                )[int(self.anim_stage)]
            else:
                image_belt = None
            if self.wear["behind"] != None:
                image_behind = choose_animations(
                    direction,
                    IMAGES.player[anim]["behind"][self.wear["behind"]]
                )[int(self.anim_stage)]
            else:
                image_behind = None
            if (self.wear["shield"] != None and anim == "slash" or self.wear[
                "shield"] != None and anim == "thrust" or
                    self.wear["shield"] != None and anim == "walkcycle"):
                image_shield = choose_animations(
                    direction,
                    IMAGES.player[anim]["shield"][self.wear["shield"]]
                )[int(self.anim_stage)]
            else:
                image_shield = None
            if anim == "slash" or anim == "thrust":
                image_weapon = choose_animations(
                    direction,
                    IMAGES.player[anim]["weapon"][self.wear["weapon"]]
                )[int(self.anim_stage)]
            else:
                image_weapon = None
            image = None
            for part in self.wear:
                if (
                        self.wear[part] != None and
                        part != "body" and
                        part != "belt" and
                        part != "weapon" and
                        part != "behind" and
                        part != "shield"
                ):
                    if image == None:
                        anim_list = choose_animations(
                            direction,
                            IMAGES.player[anim][part][self.wear[part]]
                        )
                        image = anim_list[int(self.anim_stage)]
                    else:
                        anim_list = choose_animations(
                            direction,
                            IMAGES.player[anim][part][self.wear[part]]
                        )
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
            self.screen.center = (
                self.obj_map.centerx - PLAYER.camera_x,
                self.obj_map.centery - 20 - PLAYER.camera_y
            )
            WINDOW.blit(img, self.screen)
            if image_weapon != None:
                img_weapon = IMAGES.pil_img_to_surface(image_weapon)
                screen_weapon = img_weapon.get_rect()
                screen_weapon.center = (
                    self.obj_map.centerx - PLAYER.camera_x,
                    self.obj_map.centery - 20 - PLAYER.camera_y
                )
                WINDOW.blit(img_weapon, screen_weapon)

        def animate(direction, anim):
            # Periodically play idle(spellcast) animation
            # noinspection PyBroadException
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
            # noinspection PyBroadException
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
            if self.move_status == "up":
                draw("u", "spellcast")
            elif self.move_status == "down":
                draw("d", "spellcast")
            elif self.move_status == "left":
                draw("l", "spellcast")
            elif self.move_status == "right":
                draw("r", "spellcast")
        elif self.attack_time != None and self.attack_anim_stop == False:
            if "sword" in self.wear["weapon"] or "rapier" in self.wear["weapon"]:
                if self.move_status == "up":
                    animate("u", "slash")
                elif self.move_status == "down":
                    animate("d", "slash")
                elif self.move_status == "left":
                    animate("l", "slash")
                elif self.move_status == "right":
                    animate("r", "slash")
            elif "staff" in self.wear["weapon"] or "spear" in self.wear["weapon"]:
                if self.move_status == "up":
                    animate("u", "thrust")
                elif self.move_status == "down":
                    animate("d", "thrust")
                elif self.move_status == "left":
                    animate("l", "thrust")
                elif self.move_status == "right":
                    animate("r", "thrust")
        else:
            if self.move_status == "up":
                animate("u", "walkcycle")
            elif self.move_status == "down":
                animate("d", "walkcycle")
            elif self.move_status == "left":
                animate("l", "walkcycle")
            elif self.move_status == "right":
                animate("r", "walkcycle")
            # Moving
            if self.move_status == "up-go":
                animate("u", "walkcycle")
            elif self.move_status == "down-go":
                animate("d", "walkcycle")
            elif self.move_status == "left-go":
                animate("l", "walkcycle")
            elif self.move_status == "right-go":
                animate("r", "walkcycle")

    def play_sounds(self):
        if self.under_attack_time != None and self.sound_status["under_attack"] == False:
            pygame.mixer.Sound.set_volume(SOUNDS.all[0], 0.4)
            pygame.mixer.Sound.set_volume(SOUNDS.all[4], 0.4)
            SOUNDS.all[0].play()
            SOUNDS.all[4].play()
            self.sound_status["under_attack"] = True
        elif (
                self.attack_time != None and
                self.attack_anim_stop == False and
                self.sound_status["attack"] == False
        ):
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
        if self.health_bar_width > self.health > 0:
            if "go" in self.move_status:
                self.health += 0.001
            else:
                self.health += 0.002
        if self.energy < self.energy_bar_width and self.health > 0:
            if "go" in self.move_status:
                self.energy += 0.01
            else:
                self.energy += 0.02
        # noinspection PyBroadException
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
        map_weapon = pygame.Rect(
            (self.obj_map.x, self.obj_map.y),
            (self.selected["weapon"].radius * SCALE, self.selected["weapon"].radius * SCALE)
        )
        map_weapon.center = self.obj_map.center
        if "up" in self.move_status:
            map_weapon.bottom = self.obj_map.top
        elif "down" in self.move_status:
            map_weapon.top = self.obj_map.bottom
        elif "left" in self.move_status:
            map_weapon.right = self.obj_map.left
        elif "right" in self.move_status:
            map_weapon.left = self.obj_map.right
        for o in HUMAN_PERSONS + NPC_PERSONS:
            o: Person
            if self != o:
                if (
                        o.obj_type == "player" or
                        o.obj_type == "online_player" or
                        "npc" in o.obj_type and
                        o.health > 0
                ):
                    if map_weapon.colliderect(o.obj_map):
                        skill = self.selected["weapon"].anim[7:-4]
                        if "spear" in skill or skill == "staff":
                            skill = "spear"
                        elif skill == "longsword" or skill == "rapier":
                            skill = "sword"
                        wd = self.selected["weapon"].damage
                        skill_d = (int(self.skills[skill]) / 10) * wd
                        min_damage = skill_d if skill_d < wd else wd
                        randomize_damage = random.randint(
                            int(min_damage), self.selected["weapon"].damage
                        )
                        damage = randomize_damage - o.armor if randomize_damage - o.armor > 0 else 0
                        o.health -= damage
                        o.under_attack_time = time.time()
                        self.skills[skill] += 0.01
                        if ONLINE != None:
                            DAMAGES.append((o.obj_id, damage, o.under_attack_time))

    def move(self, direction: str):
        if direction == "up":
            self.obj_map.centery -= (self.speed * SCALE)
            self.move_status = "up-go"
        elif direction == "down":
            self.obj_map.centery += (self.speed * SCALE)
            self.move_status = "down-go"
        elif direction == "left":
            self.obj_map.centerx -= (self.speed * SCALE)
            self.move_status = "left-go"
        elif direction == "right":
            self.obj_map.centerx += (self.speed * SCALE)
            self.move_status = "right-go"
        # Collisions
        for s in SPRITES:
            if self != s and self.obj_map.colliderect(s.obj_map):
                if "up" in self.move_status:
                    self.obj_map.top = s.obj_map.bottom
                elif "down" in self.move_status:
                    self.obj_map.bottom = s.obj_map.top
                elif "left" in self.move_status:
                    self.obj_map.left = s.obj_map.right
                elif "right" in self.move_status:
                    self.obj_map.right = s.obj_map.left

    # Methods only for Player
    def append_items_from_map(self):
        for i in ITEMS:
            if i.obj_map.x != 0 and i.obj_map != None:
                if i.obj_map.colliderect(self.obj_map):
                    if len(self.inventory) <= self.capacity and i not in self.inventory:
                        self.inventory.append(i)
                        i.obj_map.x, i.obj_map.y = 0, 0
                        self.sound_status["inventory_items"] = True

    def draw_player_stats(self):
        # Health, energy, cooldown indicator
        pygame.draw.rect(WINDOW, RED, (10, 10, self.health_bar_width, 17), 1)
        pygame.draw.rect(WINDOW, RED, (10, 10, self.health, 17))
        pygame.draw.rect(WINDOW, ORANGE, (10, 30, self.energy_bar_width, 17), 1)
        pygame.draw.rect(WINDOW, ORANGE, (10, 30, self.energy, 17))
        if self.attack_time != None:
            WINDOW.blit(FONT.render("!!!", True, WHITE), (10, 50, 20, 20))

    def keyboard_controls(self):
        pressed = pygame.key.get_pressed()
        if self.attack_time == None and self.under_attack_time == None:
            is_not_busy = self.is_not_busy()
            if pressed[pygame.K_w] and is_not_busy:
                self.move("up")
            elif pressed[pygame.K_s] and is_not_busy:
                self.move("down")
            elif pressed[pygame.K_a] and is_not_busy:
                self.move("left")
            elif pressed[pygame.K_d] and is_not_busy:
                self.move("right")
            else:
                if "go" in self.move_status:
                    self.move_status = self.move_status[:-3]
            if pressed[pygame.K_q]:
                if self.inventory_open == False:
                    self.inventory_open = True
                elif self.inventory_open == True:
                    self.inventory_open = False
                self.sound_status["box"] = True
                self.sound_status["inventory_items"] = True
                time.sleep(0.3)
            if pressed[pygame.K_r]:
                self.find_trader_box()
            if pressed[pygame.K_e]:
                self.append_items_from_map()
        if pressed[pygame.K_f]:
            self.try_to_attack()

    def is_not_busy(self) -> bool:
        return not self.inventory_open and self.trader == None and self.box == None

    def try_to_attack(self):
        if (
                self.selected["weapon"] != None and
                self.under_attack_time == None and
                self.attack_time == None and
                "go" not in self.move_status and
                not self.inventory_open and
                self.trader == None and
                self.box == None and
                self.energy >= self.selected["weapon"].cooldown * 5
        ):
            self.attack()
            self.energy -= self.selected["weapon"].cooldown * 5
            self.attack_time = time.time()

    def find_trader_box(self):
        # Try to find trader nearby
        if self.trader == None:
            radius = pygame.Rect((self.obj_map.x, self.obj_map.y), (75 * SCALE, 75 * SCALE))
            radius.center = self.obj_map.center
            for o in NPC_PERSONS:
                if "trader" in o.obj_type and o.health > 0:
                    if radius.colliderect(o.obj_map):
                        self.trader = o
        else:
            self.trader = None
        # Try to find box or dead NPC nearby
        if self.box == None:
            for s in SPRITES:
                # Not online_player
                if "npc" in s.obj_type and s.health <= 0 or s.obj_type == "box":
                    if (
                            self.obj_map.top == s.obj_map.bottom and
                            self.obj_map.left >= s.obj_map.left - TILE_SIZE and
                            self.obj_map.right <= s.obj_map.right + TILE_SIZE
                    ):
                        self.box = s
                    elif (
                            self.obj_map.bottom == s.obj_map.top and
                            self.obj_map.left >= s.obj_map.left - TILE_SIZE and
                            self.obj_map.right <= s.obj_map.right + TILE_SIZE
                    ):
                        self.box = s
                    elif (
                            self.obj_map.left == s.obj_map.right and
                            self.obj_map.top >= s.obj_map.top - TILE_SIZE and
                            self.obj_map.bottom <= s.obj_map.bottom + TILE_SIZE
                    ):
                        self.box = s
                    elif (
                            self.obj_map.right == s.obj_map.left and
                            self.obj_map.top >= s.obj_map.top - TILE_SIZE and
                            self.obj_map.bottom <= s.obj_map.bottom + TILE_SIZE
                    ):
                        self.box = s
        else:
            self.box = None
        #
        self.sound_status["box"] = True
        self.sound_status["inventory_items"] = True
        time.sleep(0.3)

    def get_stats(self):
        if self.selected["weapon"] != None:
            weapon_damage = self.selected["weapon"].damage
        else:
            weapon_damage = 0
        armor_stat = str(self.armor)[0:3] if len(str(self.armor)) > 3 else str(self.armor)
        sword_text = int(self.skills['sword'])
        spear_text = int(self.skills['spear'])
        return str(weapon_damage), armor_stat, str(sword_text), str(spear_text)

    def draw_inventory(self):
        text_w = WIDTH / 3
        selected_items = [self.selected[k] for k in self.selected]
        row_len, item_wh = get_half_screen_row_len()
        stats = self.get_stats()
        # Draw inventory, equipped, skills texts
        Text(
            pos=(0, 10, text_w, 20),
            text="INVENTORY",
            color=WHITE,
            size=20,
            shadow=True
        ).draw()
        Text(
            pos=(text_w, 10, text_w, 20),
            text=f"SKILLS (sword:{stats[2]}, spear:{stats[3]})",
            color=WHITE,
            size=20,
            shadow=True
        ).draw()
        Text(
            pos=(text_w * 2, 10, text_w, 20),
            text=f"EQUIPPED (DMG:{stats[0]}, ARM:{stats[1]})",
            color=WHITE,
            size=20,
            shadow=True
        ).draw()
        # Draw empty grid for equipped items
        y_index, x_index, item_index = 0, 0, 0
        for _ in range(9):
            if x_index >= 3:
                y_index += 1
                x_index = 0
            x = x_index * item_wh
            y = y_index * item_wh
            item_pos = pygame.Rect(WIDTH - item_wh - x - 10, y + 50, item_wh, item_wh)
            pygame.draw.rect(WINDOW, GREY, item_pos, 1)
            x_index += 1
        # Draw inventory
        y_index, x_index, item_index = 0, 0, 0
        for i in self.inventory:
            # Draw inventory item
            if i not in selected_items:
                # Check if the first row is already taken & set to second
                if item_index >= row_len:
                    y_index += 1
                    item_index = 0
                    x_index = 0
                y, x = y_index * item_wh, x_index * item_wh
                item_pos = pygame.Rect(x + 10, y + 50, item_wh, item_wh)
                # Draw item
                pygame.draw.rect(WINDOW, BROWN, item_pos)
                pygame.draw.rect(WINDOW, GREY, item_pos, 1)
                self.draw_item(i, item_pos)
                # Draw info about single item
                if "weapon" in i.obj_type:
                    t1 = str(i.damage)
                    t2 = str(i.cooldown)
                    text = f"{t1}, {t2}"
                elif "potion" in i.obj_type:
                    text = str(i.for_adding)
                elif "coins" in i.obj_type:
                    text = str(i.amount)
                else:
                    text = str(i.armor)
                WINDOW.blit(
                    FONT.render(f"{i.name}", True, WHITE),
                    pygame.Rect(x + 15, y + 55, item_wh, item_wh)
                )
                WINDOW.blit(
                    FONT.render(text, True, WHITE),
                    pygame.Rect(x + 15, y + 58 + FONT.get_height(), item_wh, item_wh)
                )
                # Use items
                if item_pos.collidepoint(pygame.mouse.get_pos()):
                    # Use items
                    if pygame.mouse.get_pressed()[0]:
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
                        time.sleep(0.3)
                    # Move items from player inventory
                    elif pygame.mouse.get_pressed()[2]:
                        self.sound_status["inventory_items"] = True
                        # Remove item to map
                        collide = False
                        for s in SPRITES:
                            if s.obj_map.collidepoint(
                                    self.obj_map.x - TILE_SIZE,
                                    self.obj_map.y - TILE_SIZE
                            ):
                                collide = True
                        if collide == False:
                            i.obj_map.x = self.obj_map.x - TILE_SIZE
                            i.obj_map.y = self.obj_map.y - TILE_SIZE
                            self.inventory.remove(i)
                        self.calc_coins(self.inventory)
                        time.sleep(0.3)
                x_index += 1
                item_index += 1
            # Draw selected item
            else:
                selected_pos = None
                # First row
                if i.obj_type == "weapon":
                    selected_pos = pygame.Rect(
                        WIDTH - item_wh - 10, 50, item_wh, item_wh
                    )
                elif i.obj_type == "shield":
                    selected_pos = pygame.Rect(
                        WIDTH - (item_wh * 2) - 10, 50, item_wh, item_wh
                    )
                elif i.obj_type == "behind":
                    selected_pos = pygame.Rect(
                        WIDTH - (item_wh * 3) - 10, 50, item_wh, item_wh
                    )
                # Second row
                elif i.obj_type == "hands":
                    selected_pos = pygame.Rect(
                        WIDTH - item_wh - 10, 50 + item_wh, item_wh, item_wh
                    )
                elif i.obj_type == "torso":
                    selected_pos = pygame.Rect(
                        WIDTH - (item_wh * 2) - 10, 50 + item_wh, item_wh, item_wh
                    )
                elif i.obj_type == "head":
                    selected_pos = pygame.Rect(
                        WIDTH - (item_wh * 3) - 10, 50 + item_wh, item_wh, item_wh
                    )
                # Third row
                elif i.obj_type == "feet":
                    selected_pos = pygame.Rect(
                        WIDTH - item_wh - 10, 50 + item_wh * 2, item_wh, item_wh
                    )
                elif i.obj_type == "legs":
                    selected_pos = pygame.Rect(
                        WIDTH - (item_wh * 2) - 10, 50 + item_wh * 2, item_wh, item_wh
                    )
                elif i.obj_type == "belt":
                    selected_pos = pygame.Rect(
                        WIDTH - (item_wh * 3) - 10, 50 + item_wh * 2, item_wh, item_wh
                    )
                if selected_pos != None:
                    pygame.draw.rect(WINDOW, BROWN, selected_pos)
                    pygame.draw.rect(WINDOW, GREY, selected_pos, 1)
                    self.draw_item(i, selected_pos)
                    if selected_pos.collidepoint(pygame.mouse.get_pos()):
                        # Move items from selected
                        if pygame.mouse.get_pressed()[0]:
                            self.sound_status["inventory_items"] = True
                            for k in self.selected:
                                if i == self.selected[k]:
                                    if k == "head" and self.hair != None:
                                        self.selected[k] = None
                                        self.wear[k] = self.hair
                                    else:
                                        self.selected[k] = None
                                        self.wear[k] = None
                                    self.count_armor()
                            time.sleep(0.3)

    def draw_sharing(self):
        row_len, item_wh = get_half_screen_row_len()
        # Draw box or dead NPC or Trader info
        text = ""
        if self.box != None:
            text = "NPC Items" if "npc" in self.box.obj_type else "Box Items"
        elif self.trader != None:
            text = "Trader Items"
        WINDOW.blit(
            FONT.render(text, True, WHITE), (WIDTH // 5, 20)
        )
        equipped_text = f"Inventory"
        WINDOW.blit(
            FONT.render(equipped_text, True, WHITE),(WIDTH - WIDTH // 3, 20)
        )
        # Draw box or dead NPC or Trader
        inventory = []
        if self.box != None:
            inventory = self.box.inventory
        elif self.trader != None:
            trader_selected = [self.trader.selected[k] for k in self.trader.selected]
            for i in self.trader.inventory:
                if i not in trader_selected:
                    inventory.append(i)
        y_index, x_index, item_index = 0, 0, 0
        for i in inventory:
            # Check if the first row is already taken & set to second
            if item_index >= row_len:
                y_index += 1
                item_index = 0
                x_index = 0
            y, x = y_index * item_wh, x_index * item_wh
            item_pos = pygame.Rect(x + 10, y + 50, item_wh, item_wh)
            pygame.draw.rect(WINDOW, BROWN, item_pos)
            pygame.draw.rect(WINDOW, GREY, item_pos, 1)
            self.draw_item(i, item_pos)
            # Draw info about single item
            if "weapon" in i.obj_type:
                t1 = str(i.damage)
                t2 = str(i.cooldown)
                text = f"{t1}, {t2}"
            elif "potion" in i.obj_type:
                text = str(i.for_adding)
            elif "coins" in i.obj_type:
                text = str(i.amount)
            else:
                text = str(i.armor)
            WINDOW.blit(FONT.render(f"{i.name}", True, WHITE),
                        pygame.Rect(x + 15, y + 55, item_wh, item_wh))
            WINDOW.blit(FONT.render(text, True, WHITE),
                        pygame.Rect(x + 15, y + 58 + FONT.get_height(), item_wh, item_wh))
            x_index += 1
            item_index += 1
            if item_pos.collidepoint(pygame.mouse.get_pos()):
                if pygame.mouse.get_pressed()[0]:
                    self.sound_status["inventory_items"] = True
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
                                    if ic.amount >= 100:  # Universal price ???
                                        self.inventory.append(i)
                                        self.trader.inventory.remove(i)
                                        ic.amount -= 100
                                        coins_found = False
                                        for ict in self.trader.inventory:
                                            if ict.obj_type == "coins":
                                                coins_found = True
                                                ict.amount += 100
                                        if coins_found == False:
                                            self.trader.inventory.append(
                                                Coins(
                                                    602,
                                                    "Coins",
                                                    "coins",
                                                    ic.image,
                                                    100
                                                )
                                            )
                        self.calc_coins(self.trader.inventory)
                    self.calc_coins(self.inventory)
                    time.sleep(0.3)
        #
        selected_items = [self.selected[k] for k in self.selected]
        # Draw player inventory
        y_index, x_index, item_index = 0, 0, 0
        for i in self.inventory:
            # Draw inventory item
            if i not in selected_items:
                # Check if the first row is already taken & set to second
                if x_index >= row_len:
                    y_index += 1
                    x_index = 0
                x = x_index * item_wh
                y = y_index * item_wh
                item_pos = pygame.Rect(WIDTH - item_wh - x - 10, y + 50, item_wh, item_wh)
                pygame.draw.rect(WINDOW, BROWN, item_pos)
                pygame.draw.rect(WINDOW, GREY, item_pos, 1)
                self.draw_item(i, item_pos)
                # Draw info about single item
                if "weapon" in i.obj_type:
                    t1 = str(i.damage)
                    t2 = str(i.cooldown)
                    text = f"{t1}, {t2}"
                elif "potion" in i.obj_type:
                    text = str(i.for_adding)
                elif "coins" in i.obj_type:
                    text = str(i.amount)
                else:
                    text = str(i.armor)
                WINDOW.blit(
                    FONT.render(f"{i.name}", True, WHITE),
                    pygame.Rect(WIDTH - item_wh - x - 5, y + 55, item_wh, item_wh)
                )
                WINDOW.blit(
                    FONT.render(text, True, WHITE),
                    pygame.Rect(
                        WIDTH - item_wh - x - 5, y + 58 + FONT.get_height(), item_wh, item_wh
                    )
                )
                # Use items
                if item_pos.collidepoint(pygame.mouse.get_pos()):
                    # Move items from player inventory
                    if pygame.mouse.get_pressed()[0]:
                        self.sound_status["inventory_items"] = True
                        if self.box != None:
                            # Add item to the box
                            if len(self.box.inventory) <= self.box.capacity and i not in self.box.inventory:
                                self.inventory.remove(i)
                                self.box.inventory.append(i)
                        elif self.trader != None:
                            # Sell item to trader ???
                            if len(self.trader.inventory) <= self.trader.capacity and i not in self.trader.inventory:
                                if i.obj_type != "coins":
                                    for ic in self.trader.inventory:
                                        if ic.obj_type == "coins":
                                            if ic.amount >= 100:  # Universal price ???
                                                self.inventory.remove(i)
                                                self.trader.inventory.append(i)
                                                ic.amount -= 100
                                                coins_found = False
                                                for ict in self.inventory:
                                                    if ict.obj_type == "coins":
                                                        coins_found = True
                                                        ict.amount += 100
                                                if coins_found == False:
                                                    self.inventory.append(
                                                        Coins(
                                                            602,
                                                            "Coins",
                                                            "coins",
                                                            ic.image,
                                                            100
                                                        )
                                                    )
                        self.calc_coins(self.inventory)
                        time.sleep(0.3)
                x_index += 1
                item_index += 1

    def calc_coins(self, inventory):
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

    def draw_item(self, item, pos):
        # If image doesn't exist, take from anim
        if item.image == None:
            if item.obj_type == "shield" or item.obj_type == "behind":
                img = IMAGES.pil_img_to_surface(
                    IMAGES.player["walkcycle"][item.obj_type][item.anim][10])
            else:
                img = IMAGES.pil_img_to_surface(
                    IMAGES.player["walkcycle"][item.obj_type][item.anim][18])
            if (
                    item.obj_type == "behind" or
                    item.obj_type == "hands" or
                    item.obj_type == "feet" or
                    item.obj_type == "legs" or
                    item.obj_type == "belt"
            ):
                h = img.get_height() // 2
                item.image = img.subsurface(pygame.Rect(0, h, img.get_width(), h))
            else:
                item.image = img
            image = item.image
        else:
            image = item.image
        rect = image.get_rect()
        rect.center = pos.center
        WINDOW.blit(image, rect)

    def camera(self):
        right_border = WORLD_MAP_RECT.width - WIDTH
        down_border = WORLD_MAP_RECT.height - HEIGHT
        if self.screen.x < WIDTH // 2:
            num1 = WIDTH // 2 - self.screen.x
            if self.camera_x - num1 < 0:
                self.camera_x = 0
            else:
                self.camera_x -= num1
        elif self.screen.x > WIDTH // 2:
            num1 = self.screen.x - WIDTH // 2
            if self.camera_x + num1 > right_border:
                self.camera_x = right_border
            else:
                self.camera_x += num1
        if self.screen.y < HEIGHT // 2:
            num1 = HEIGHT // 2 - self.screen.y
            if self.camera_y - num1 < 0:
                self.camera_y = 0
            else:
                self.camera_y -= num1
        elif self.screen.y > HEIGHT // 2:
            num1 = self.screen.y - HEIGHT // 2
            if self.camera_y + num1 > down_border:
                self.camera_y = down_border
            else:
                self.camera_y += num1

    # Methods only for NPCs
    def draw_npc_stats(self):
        health_rect = pygame.Rect(0, 0, self.health_bar_width * SCALE / 5, TILE_SIZE / 10)
        health_rect_i = pygame.Rect(0, 0, self.health * SCALE / 5, TILE_SIZE / 10)
        health_rect.center = (
            self.obj_map.centerx - PLAYER.camera_x,
            self.obj_map.y - 32 - PLAYER.camera_y
        )
        health_rect_i.center = (
            self.obj_map.centerx - PLAYER.camera_x, self.obj_map.y - 32 - PLAYER.camera_y)
        pygame.draw.rect(WINDOW, RED, health_rect, 1)
        pygame.draw.rect(WINDOW, RED, health_rect_i)

    def draw_npc_dialogs(self):
        if (
                self.health > 0 and
                PLAYER.health > 0 and
                self.attack_time == None and
                self.under_attack_time == None
        ):
            x_distance, y_distance, _ = self.calc_distance(
                person_map=PLAYER.obj_map,
                x=self.obj_map.centerx,
                y=self.obj_map.centery
            )
            if x_distance < 40 * SCALE and y_distance < 40 * SCALE:
                # Change move status on player direction when player in radius
                test = pygame.Rect((self.obj_map.x, self.obj_map.y), (40 * SCALE, 40 * SCALE))
                test.center = self.obj_map.center
                for status in ["up", "down", "left", "right"]:
                    if "up" in status:
                        test.bottom = self.obj_map.top
                    elif "down" in status:
                        test.top = self.obj_map.bottom
                    elif "left" in status:
                        test.right = self.obj_map.left
                    elif "right" in status:
                        test.left = self.obj_map.right
                    if test.colliderect(PLAYER.obj_map):
                        self.move_status = status
                # Draw dialogs
                rect_pos = (
                    self.obj_map.x - 30 - PLAYER.camera_x,
                    self.obj_map.y - 60 - PLAYER.camera_y
                )
                text = self.dialogs[0]
                pygame.draw.rect(WINDOW, GREY, (rect_pos, (50, 17)))
                WINDOW.blit(FONT.render(text, True, WHITE), (rect_pos, (50, 17)))

    def npc_move_attack(self):
        if self.health > 0 and self.attack_time == None and self.under_attack_time == None:
            # NPC seen radius
            seen_radius = pygame.Rect((0, 0), (300 * SCALE, 300 * SCALE))
            seen_radius.center = (self.obj_map.centerx, self.obj_map.centery)
            # Specify enemies for NPC and calculate distance to them
            distances = []
            for p in HUMAN_PERSONS:
                if p.health > 0:
                    if seen_radius.colliderect(p.obj_map):
                        x, y, d = self.calc_distance(
                            person_map=p.obj_map,
                            x=self.obj_map.centerx,
                            y=self.obj_map.centery
                        )
                        distances.append([p, x, y, d])

            # If players in NPC seen radius
            if len(distances) > 0:
                distances.sort(key=lambda s: s[3])
                player = distances[0][0]

                # When NPC close to the player
                if (distances[0][1] < self.selected["weapon"].radius * SCALE and distances[0][
                    2] < 10 * SCALE or
                        distances[0][2] < self.selected["weapon"].radius * SCALE and distances[0][
                            1] < 10 * SCALE):
                    # Stop anim
                    if "go" in self.move_status:
                        self.move_status = self.move_status[:-3]
                    # Turn to the player - testing all sides
                    test = pygame.Rect((self.obj_map.x, self.obj_map.y), (
                        self.selected["weapon"].radius, self.selected["weapon"].radius))
                    test.center = self.obj_map.center
                    for status in ["up", "down", "left", "right"]:
                        if "up" in status:
                            test.bottom = self.obj_map.top
                        elif "down" in status:
                            test.top = self.obj_map.bottom
                        elif "left" in status:
                            test.right = self.obj_map.left
                        elif "right" in status:
                            test.left = self.obj_map.right
                        if test.colliderect(player.obj_map):
                            self.move_status = status
                    # Attack player
                    if self.selected["weapon"] != None and self.energy >= self.selected[
                        "weapon"].cooldown * 5:
                        self.attack()
                        self.energy -= self.selected["weapon"].cooldown * 5
                        self.attack_time = time.time()

                # When the NPC is away from the player
                else:
                    # Calculate possible moves
                    possible_moves = {"up": 0, "down": 0, "left": 0, "right": 0}
                    o1 = self.obj_map

                    # Checking obstacles
                    for o2 in SPRITES:
                        if o1 != o2:
                            o2 = o2.obj_map
                            if (
                                    o1.top == o2.bottom and
                                    o1.left >= o2.left - 15 and
                                    o2.right + 15 >= o1.right >= o2.left and
                                    o1.left <= o2.right
                            ):
                                if "up" in possible_moves:
                                    possible_moves.pop("up")
                            if (
                                    o1.bottom == o2.top and
                                    o1.left >= o2.left - 15 and
                                    o2.right + 15 >= o1.right >= o2.left and
                                    o1.left <= o2.right
                            ):
                                if "down" in possible_moves:
                                    possible_moves.pop("down")
                            if (
                                    o1.left == o2.right and
                                    o1.top >= o2.top - 15 and
                                    o2.bottom + 15 >= o1.bottom >= o2.top and
                                    o1.top <= o2.bottom
                            ):
                                if "left" in possible_moves:
                                    possible_moves.pop("left")
                            if (
                                    o1.right == o2.left and
                                    o1.top >= o2.top - 15 and
                                    o2.bottom + 15 >= o1.bottom >= o2.top and
                                    o1.top <= o2.bottom
                            ):
                                if "right" in possible_moves:
                                    possible_moves.pop("right")
                    if "up" in possible_moves:
                        possible_moves["up"] = self.calc_distance(
                            person_map=player.obj_map,
                            y=self.obj_map.centery - (self.speed * SCALE)
                        )
                    if "down" in possible_moves:
                        possible_moves["down"] = self.calc_distance(
                            person_map=player.obj_map,
                            y=self.obj_map.centery + (self.speed * SCALE)
                        )
                    if "left" in possible_moves:
                        possible_moves["left"] = self.calc_distance(
                            person_map=player.obj_map,
                            x=self.obj_map.centerx - (self.speed * SCALE)
                        )
                    if "right" in possible_moves:
                        possible_moves["right"] = self.calc_distance(
                            person_map=player.obj_map,
                            x=self.obj_map.centerx + (self.speed * SCALE)
                        )

                    # Moving
                    if self.movement == None:
                        if (
                                "up" not in possible_moves and
                                self.obj_map.centery > player.obj_map.centery or
                                "down" not in possible_moves and
                                self.obj_map.centery < player.obj_map.centery
                        ):
                            if "left" in possible_moves:
                                self.movement = {"left": 40}
                                self.direction = "y"
                            elif "right" in possible_moves:
                                self.movement = {"right": 40}
                                self.direction = "y"
                        if (
                                "left" not in possible_moves and
                                self.obj_map.centerx > player.obj_map.centerx or
                                "right" not in possible_moves and
                                self.obj_map.centerx < player.obj_map.centerx
                        ):
                            if "up" in possible_moves:
                                self.movement = {"up": 40}
                                self.direction = "x"
                            elif "down" in possible_moves:
                                self.movement = {"down": 40}
                                self.direction = "x"
                        else:
                            if "x" in self.direction:
                                if self.obj_map.centerx > player.obj_map.centerx:
                                    self.move("left")
                                elif self.obj_map.centerx < player.obj_map.centerx:
                                    self.move("right")
                                elif self.obj_map.centery > player.obj_map.centery:
                                    self.move("up")
                                elif self.obj_map.centery < player.obj_map.centery:
                                    self.move("down")
                            elif "y" in self.direction:
                                if self.obj_map.centery > player.obj_map.centery:
                                    self.move("up")
                                elif self.obj_map.centery < player.obj_map.centery:
                                    self.move("down")
                                elif self.obj_map.centerx > player.obj_map.centerx:
                                    self.move("left")
                                elif self.obj_map.centerx < player.obj_map.centerx:
                                    self.move("right")

                    elif self.movement != None:
                        self.movement: dict[str, int]
                        for i in self.movement:
                            if i in possible_moves:
                                if self.movement[i] >= 0:
                                    self.move(i)
                                    self.movement[i] -= (self.speed * SCALE)
                                if self.movement[i] <= 0:
                                    self.movement = None
                                else:
                                    break
                            else:
                                self.movement = None

            # If the NPC did not see the players -> stop
            else:
                if "go" in self.move_status:
                    self.move_status = self.move_status[:-3]

    def calc_distance(self, person_map: pygame.Rect, x: int = None, y: int = None):
        """Calculate distance from Person.obj_map to 'x' and|or 'y'"""
        x_distance = 0
        y_distance = 0
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
            eu_distance = ((x - person_map.centerx) ** 2 + (y - person_map.centery) ** 2) ** 0.5
            return x_distance, y_distance, eu_distance
        elif x != None:
            return x_distance
        elif y != None:
            return y_distance


# ONLINE GAMEPLAY
class OnlineUpdateThread(threading.Thread):
    """This module provides communication between the player (host) and the players (clients)"""
    def __init__(self):
        super().__init__()
        self.stop_flag = threading.Event()
        self.last_data = []

    def run(self):
        global IS_HOST
        conn = None
        if IS_HOST == True:
            # noinspection PyBroadException
            try:
                conn, address = ONLINE.accept()
            except:
                pass

        while not self.stop_flag.is_set():
            time.sleep(0.01)
            if IS_HOST:
                self.receive_update_data(conn)
                self.send_data(conn, IS_HOST)
            elif not IS_HOST:
                self.send_data(ONLINE, IS_HOST)
                self.receive_update_data(ONLINE)

        if not IS_HOST:
            IS_HOST = True

    def stop(self):
        self.stop_flag.set()
        # After thread is stopped - delete persons associated with that thread
        persons = HUMAN_PERSONS + NPC_PERSONS
        for d in self.last_data:
            for s in persons:
                if s.obj_id == d["obj_id"] and d["obj_id"] != PLAYER.obj_id:
                    SPRITES.remove(s)
                    HUMAN_PERSONS.remove(s)

    def send_data(self, source: socket.socket, is_host: bool):
        sending_data = [{"damages": DAMAGES}]
        for s in HUMAN_PERSONS + NPC_PERSONS:
            if s.obj_type != "npc-trader":
                if (
                        (is_host == True and "player" in s.obj_type) or
                        (is_host == False and s.obj_id == PLAYER.obj_id)
                ):
                    sending_data.append({
                        "obj_id": s.obj_id,
                        "obj_type": s.obj_type,
                        "health": s.health,
                        "attack_stop": s.attack_stop,
                        "attack_anim_stop": s.attack_anim_stop,
                        "attack_time": s.attack_time if s.attack_time != None else "None",
                        "under_attack_time": s.under_attack_time if s.under_attack_time != None else "None",
                        "map_x": s.obj_map.x,
                        "map_y": s.obj_map.y,
                        "move_status": s.move_status,
                        "wear": s.wear,
                        "armor": s.armor
                    })
        data_to_send = json.dumps(sending_data)
        try:
            source.sendall(bytes(data_to_send, encoding="utf-8"))
        except Exception as e:
            print(f"Send Data Error: {e}")
        DAMAGES.clear()

    def receive_update_data(self, source):
        def update_person_info(person: Person, url_person: dict):
            person.move_status = url_person["move_status"]
            person.health = url_person["health"]
            person.attack_stop = url_person["attack_stop"]
            person.attack_anim_stop = url_person["attack_anim_stop"]
            person.wear = url_person["wear"]
            person.armor = url_person["armor"]
            # noinspection PyBroadException
            try:
                person.attack_time = float(url_person["attack_time"])
            except:
                person.attack_time = None
            # noinspection PyBroadException
            try:
                person.under_attack_time = float(url_person["under_attack_time"])
            except:
                person.under_attack_time = None

        try:
            received_data = json.loads(source.recv(10000).decode("utf-8"))
            persons = HUMAN_PERSONS + NPC_PERSONS
            #
            first_obj = received_data[0]
            for i in first_obj["damages"]:
                for s in persons:
                    # (person.obj_id, damage, under_attack_time)
                    if s.obj_id == i[0]:
                        s.health -= i[1]
                        s.under_attack_time = i[2]
            #
            self.last_data = received_data[1:]
            for d in self.last_data:
                # Check if person already exist
                found = False
                for s in persons:
                    if s.obj_id == d["obj_id"]:
                        found = True
                        if d["obj_id"] != PLAYER.obj_id:
                            # Update person
                            s.obj_map.x = d["map_x"]
                            s.obj_map.y = d["map_y"]
                            update_person_info(s, d)
                # If person not found, create new
                if found == False:
                    new = create_person(d["obj_type"])
                    new.obj_type = "online_player" if d["obj_type"] == "player" else d["obj_type"]
                    new.obj_id = d["obj_id"]
                    new.obj_map = pygame.Rect(d["map_x"], d["map_y"], TILE_SIZE / 2, TILE_SIZE / 2)
                    update_person_info(new, d)
        except Exception as e:
            print(f"Receive Data Error: {e}")
            self.stop()


# UTILS FUNCTIONS
def create_unique_id(objs_list: list, start_id=1):
    new_id = start_id
    test = False
    while test == False:
        test = True
        for i in objs_list:
            if new_id == i.obj_id:
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
        c_item = Weapon(
            new_id, item.name, item.obj_type, item.image, item.anim, item.damage,
            item.cooldown, item.radius
        )
    elif item.obj_type in [
        "head", "weapon", "torso", "hands", "legs", "belt", "feet", "behind", "shield"
    ]:
        c_item = Outfit(new_id, item.name, item.obj_type, None, item.anim, item.armor)
    elif "potion" in item.obj_type:
        c_item = Potion(new_id, item.name, item.obj_type, item.image, item.for_adding)
    else:  # if "coins" in item.obj_type:
        c_item = Coins(new_id, item.name, item.obj_type, item.image, item.amount)
    ITEMS.append(c_item)
    return new_id, c_item


def create_person(person_type: str) -> Person:
    i = GAME_OBJECTS["persons"][person_type]
    # Create person items copy (assign new id)
    for key in i:
        if key not in ["health", "speed", "sword_skill", "spear_skill"]:
            for p_item in persons_boxes_items():
                if key == "inventory":
                    for index, inventory_item_id in enumerate(i["inventory"]):
                        if inventory_item_id == p_item.obj_id:
                            i["inventory"][index], _ = create_item_copy(p_item)
                elif type(i[key]) == int and i[key] == p_item.obj_id:
                    i[key], _ = create_item_copy(p_item)
    # Create person
    person = Person(i["health"], i["speed"], i["body"], i["sword_skill"], i["spear_skill"],
                    i["hair"], i["head"], i["weapon"], i["torso"], i["hands"], i["legs"], i["belt"],
                    i["feet"], i["behind"], i["shield"])
    # Add items to inventory
    for item in ITEMS:
        if item.obj_id in i["inventory"]:
            if item.obj_type == "coins":
                # Randomize new persons amount of coins
                item.amount = random.randint(100, item.amount if item.amount > 100 else 1000)
            person.inventory.append(item)
    #
    if "player" in person_type:
        person.obj_type = "player"
        person.obj_id = PLAYER_ID
        HUMAN_PERSONS.append(person)
    else:
        person.obj_id = create_unique_id(HUMAN_PERSONS + NPC_PERSONS, 100)
        NPC_PERSONS.append(person)
        if "trader" in person_type:
            person.obj_type = "npc-trader"
            person.dialogs = i["dialogs"]
    SPRITES.append(person)
    return person


def init_world_objects():
    global ITEMS, SPRITES, TREETOPS, PLAYER

    # Create items
    for i in GAME_OBJECTS["items"]:
        if "weapon" in i["obj_type"]:
            item = Weapon(
                i["id"], i["name"], i["obj_type"], IMAGES.load32(i["image"]), i["anim"],
                i["damage"], i["cooldown"], i["radius"]
            )
        elif "potion" in i["obj_type"]:
            item = Potion(
                i["id"], i["name"], i["obj_type"], IMAGES.load32(i["image"]), i["for_adding"]
            )
        elif "coins" in i["obj_type"]:
            item = Coins(
                i["id"], i["name"], i["obj_type"], IMAGES.load32(i["image"]), i["amount"]
            )
        else:
            item = Outfit(
                i["id"], i["name"], i["obj_type"], None, i["anim"], i["armor"]
            )
        ITEMS.append(item)

    # Create boxes
    created_boxes = []
    for i in GAME_OBJECTS["boxes"]:
        # Create box items copy
        for p_item in persons_boxes_items():
            for index, inventory_item in enumerate(i["inventory"]):
                if inventory_item == p_item.obj_id:
                    i["inventory"][index], _ = create_item_copy(p_item)
        # Create box
        box = Box(i["id"], None, i["obj_type"], IMAGES.load32(i["image"]),
                  IMAGES.load32(i["image_open"]))
        for item in ITEMS:
            if item.obj_id in i["inventory"]:
                if item.obj_type == "coins":
                    # Randomize coins amount
                    item.amount = random.randint(10, item.amount if item.amount > 100 else 1000)
                box.inventory.append(item)
        created_boxes.append(box)

    # Create world (map + objects + persons)
    for file_path in [
        os.path.join(GRAPH_PATH, "map", "world_map_borders.csv"),
        os.path.join(GRAPH_PATH, "map", "world_map_trees.csv"),
        os.path.join(GRAPH_PATH, "map", "world_map_obj.csv")
    ]:
        with open(file_path) as file:
            for y_index, row in enumerate(file):
                row = eval(row)
                y = y_index * TILE_SIZE
                for x_index, i in enumerate(row):
                    x = x_index * TILE_SIZE
                    if "world_map_borders" in file.name:
                        if i == 0:
                            w = Object(
                                obj_id=0,
                                obj_map=pygame.Rect(x, y, TILE_SIZE, TILE_SIZE),
                                obj_type="border"
                            )
                            SPRITES.append(w)
                    elif "world_map_trees" in file.name:
                        if i != -1:
                            if i in [202, 203, 250, 251, 253, 254]:
                                t = Object(
                                    obj_id=i,
                                    obj_map=pygame.Rect(x, y, TILE_SIZE, TILE_SIZE - 10),
                                    obj_type="tree"
                                )
                                t.image = IMAGES.trees[i]
                                SPRITES.append(t)
                            else:
                                t = Object(
                                    obj_id=i,
                                    obj_map=pygame.Rect(x, y, TILE_SIZE, TILE_SIZE),
                                    obj_type="tree_up"
                                )
                                t.image = IMAGES.trees[i]
                                TREETOPS.append(t)
                    elif "world_map_obj" in file.name:
                        if i == 1:
                            PLAYER = create_person("player")
                            PLAYER.obj_map = pygame.Rect(x, y, TILE_SIZE / 2, TILE_SIZE / 2)
                        elif i == 2:
                            ri = random.randint(0, len(ITEMS) - 1)
                            item = ITEMS[ri]
                            if item in persons_boxes_items():
                                _, c_item = create_item_copy(item)
                                c_item.obj_map.x, c_item.obj_map.y = x, y
                            else:
                                item.obj_map.x, item.obj_map.y = x, y
                        elif i == 3:
                            enemy = create_person("enemy")
                            enemy.obj_map = pygame.Rect(x, y, TILE_SIZE / 2, TILE_SIZE / 2)
                        elif i == 4:
                            for s in created_boxes:
                                if s.obj_map == None:
                                    s.obj_map = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                                    s.obj_map.inflate_ip(0, -10)
                                    SPRITES.append(s)
                        elif i == 5:
                            trader = create_person("trader")
                            trader.obj_map = pygame.Rect(x, y, TILE_SIZE / 2, TILE_SIZE / 2)
                            trader.capacity = 30


def get_half_screen_row_len() -> tuple[int, int]:
    scaled = 42 * SCALE
    item_wh = scaled if scaled >= 110 else 110
    if 1 <= SCALE < 4:
        row_len = 5
    elif SCALE == 4:
        row_len = 4
    else:
        row_len = 1
    return row_len, item_wh


def close_gameplay(threads: list[OnlineUpdateThread]):
    def shutdown():
        time.sleep(1)
        # noinspection PyBroadException
        try:
            ONLINE.shutdown(socket.SHUT_RDWR)
        except:
            pass
        ONLINE.close()

    if ONLINE != None:
        for t in threads:
            t.stop()
        threading.Thread(target=shutdown).start()


def get_is_back_clicked(e: pygame.event.Event):
    return e.type == pygame.QUIT or (
            e.type == pygame.KEYDOWN and (e.key == pygame.K_ESCAPE or e.key == pygame.K_AC_BACK)
    )


def run_game():
    global WIDTH, HEIGHT, TILE_SIZE, SCALE, MOBILE_MOVEMENT_ON, X_MOBILE, Y_MOBILE
    global ONLINE, IS_HOST, PLAYER_ID, THREADS_NUMBER, DAMAGES
    global WINDOW, FONT, SOUNDS, IMAGES, WORLD_MAP_RECT
    global HUMAN_PERSONS, NPC_PERSONS, ITEMS, SPRITES, TREETOPS, DEAD_NPC, GAME_OBJECTS

    # Height and width one tile on map multiplied by scale
    TILE_SIZE = 32 * SCALE
    # NPC damages that sent to other online players
    DAMAGES = []

    with open(OBJECTS_PATH, 'r') as file:
        data: dict = json.load(file)
    GAME_OBJECTS = data

    # Load assets for map, objects
    HUMAN_PERSONS, NPC_PERSONS, ITEMS, SPRITES, TREETOPS, DEAD_NPC = [], [], [], [], [], []
    SOUNDS, IMAGES = Sounds(), Images()
    FONT = pygame.font.Font("freesansbold.ttf", 15)
    world_map_img = IMAGES.load_map(os.path.join("map", "world_map.png"))
    WORLD_MAP_RECT = world_map_img.get_rect()

    move_img = IMAGES.load32("move.png")
    sword_img = IMAGES.load32("sword.png")
    item_img = IMAGES.load32("item.png")
    trade_img = IMAGES.load32("trade.png")
    grab_img = IMAGES.load32("grab.png")

    init_world_objects()

    # On host - create threads for other players. On client - only one thread
    threads = []
    if ONLINE != None:
        for _ in range(THREADS_NUMBER):
            t = OnlineUpdateThread()
            t.start()
            threads.append(t)

    # Controls on mobile by accelerometer
    if ON_ANDROID:
        try:
            plyer.accelerometer.enable()
        except Exception as e:
            print(f"Accelerometer not available {e}")

    # Buttons creation
    _, item_wh = get_half_screen_row_len()
    move_button = Button(
        (10, HEIGHT - item_wh - 10, item_wh, item_wh),
        move_img
    )
    attack_button = Button(
        (WIDTH - item_wh - 10, HEIGHT - item_wh - 10, item_wh, item_wh),
        sword_img
    )
    grab_button = Button(
        (WIDTH - (item_wh * 2) - 10 - 3, HEIGHT - item_wh - 10, item_wh, item_wh),
        grab_img
    )
    loot_trade_button = Button(
        (WIDTH - (item_wh * 3) - 10 - 6, HEIGHT - item_wh - 10, item_wh, item_wh),
        trade_img
    )
    inventory_button = Button(
        (WIDTH - (item_wh * 4) - 10 - 9, HEIGHT - item_wh - 10, item_wh, item_wh),
        item_img
    )

    # GAMEPLAY LOOP
    clock = pygame.time.Clock()
    game_loop = True
    while game_loop:
        for event in pygame.event.get():
            if get_is_back_clicked(event):
                close_gameplay(threads)
                game_loop = False

        # Draw map
        SOUNDS.play_map_sounds()
        WINDOW.blit(world_map_img, (0 - PLAYER.camera_x, 0 - PLAYER.camera_y))

        # Draw objects
        for d in DEAD_NPC:
            d: Person
            d.draw_person()
        for i in ITEMS:
            if i not in PLAYER.inventory and i.obj_map.x != 0:
                if i.image == None:
                    WINDOW.blit(
                        item_img,
                        (i.obj_map.x - PLAYER.camera_x, i.obj_map.y - PLAYER.camera_y)
                    )
                else:
                    WINDOW.blit(
                        i.image,
                        (i.obj_map.x - PLAYER.camera_x, i.obj_map.y - PLAYER.camera_y)
                    )
        for s in sorted(SPRITES, key=lambda s1: s1.obj_map.centery):
            if (
                    s not in DEAD_NPC and
                    (s.obj_type == "online_player" or "npc" in s.obj_type) and
                    s.health <= 0
            ):
                DEAD_NPC.append(s)
            elif (
                    s.obj_type == "player" or
                    s.obj_type == "online_player" or
                    "npc" in s.obj_type and
                    s.health > 0
            ):
                s: Person
                s.draw_person()
                s.play_sounds()
            elif s.obj_type == "tree":
                s: Object
                WINDOW.blit(
                    s.image,
                    (s.obj_map.x - PLAYER.camera_x, s.obj_map.y - 5 - PLAYER.camera_y)
                )
            elif s.obj_type == "box":
                s: Box
                box_image = s.image_open if PLAYER.box == s else s.image
                WINDOW.blit(
                    box_image,
                    (s.obj_map.x - PLAYER.camera_x, s.obj_map.y - 5 - PLAYER.camera_y)
                )
        for t in TREETOPS:
            WINDOW.blit(
                t.image,
                (t.obj_map.x - PLAYER.camera_x, t.obj_map.y - 5 - PLAYER.camera_y)
            )

        # NPCs
        for s in NPC_PERSONS:
            s: Person
            if s.health > 0:
                s.stats_restoration()
                s.draw_npc_stats()
                if "enemy" in s.obj_type:
                    if IS_HOST == True:
                        s.npc_move_attack()
                elif "trader" in s.obj_type:
                    s.draw_npc_dialogs()
                    if s.under_attack_time != None:
                        s.obj_type = "npc-enemy"

        # Player
        if PLAYER.health > 0:
            PLAYER.keyboard_controls()
            if PLAYER.inventory_open:
                PLAYER.draw_inventory()
            if PLAYER.box != None or PLAYER.trader != None:
                PLAYER.draw_sharing()
            PLAYER.draw_player_stats()
            PLAYER.stats_restoration()
            PLAYER.camera()
        else:
            PLAYER.inventory_open = False
            if ONLINE == None:
                close_gameplay(threads)
                game_loop = False

        if ON_ANDROID:
            # Button for enabling moving by accelerometer
            x_g, y_g, z_g = plyer.accelerometer.acceleration
            if move_button.draw_get_is_clicked():
                if MOBILE_MOVEMENT_ON == False:
                    MOBILE_MOVEMENT_ON = True
                    move_button.is_clicked = True
                    # noinspection PyBroadException
                    try:
                        X_MOBILE = x_g
                        Y_MOBILE = y_g
                    except Exception as _:
                        pass
                elif MOBILE_MOVEMENT_ON == True:
                    MOBILE_MOVEMENT_ON = False
                    move_button.is_clicked = False
                time.sleep(0.3)

            # Controls by accelerometer
            if (
                    MOBILE_MOVEMENT_ON and
                    PLAYER.attack_time == None and
                    PLAYER.under_attack_time == None
            ):
                is_not_busy = PLAYER.is_not_busy()
                # noinspection PyBroadException
                try:
                    if y_g > Y_MOBILE + 1 and is_not_busy:
                        PLAYER.move("right")  # "down"
                    elif y_g < Y_MOBILE - 1 and is_not_busy:
                        PLAYER.move("left")  # "up"
                    elif x_g > X_MOBILE + 1 and is_not_busy:
                        PLAYER.move("down")  # "left"
                    elif x_g < X_MOBILE - 1 and is_not_busy:
                        PLAYER.move("up")  # "right"
                except Exception as _:
                    pass

            # Onscreen buttons for controls
            if attack_button.draw_get_is_clicked():
                PLAYER.try_to_attack()

            if grab_button.draw_get_is_clicked():
                PLAYER.append_items_from_map()

            if loot_trade_button.draw_get_is_clicked():
                PLAYER.find_trader_box()
                if PLAYER.box != None or PLAYER.trader != None:
                    loot_trade_button.is_clicked = True
                else:
                    loot_trade_button.is_clicked = False

            if inventory_button.draw_get_is_clicked():
                if PLAYER.inventory_open == False:
                    PLAYER.inventory_open = True
                    inventory_button.is_clicked = True
                elif PLAYER.inventory_open == True:
                    PLAYER.inventory_open = False
                    inventory_button.is_clicked = False
                PLAYER.sound_status["box"] = True
                PLAYER.sound_status["inventory_items"] = True
                time.sleep(0.3)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


def get_local_ip():
    """
    Attempts to find the non-loopback local IP address by connecting to an
    external IP address.
    """
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    except socket.error:
        local_ip = socket.gethostbyname(socket.gethostname())
    finally:
        if s:
            s.close()
    return local_ip


def run_main_menu():
    global WIDTH, HEIGHT, TILE_SIZE, SCALE, MOBILE_MOVEMENT_ON, X_MOBILE, Y_MOBILE
    global ONLINE, IS_HOST, PLAYER_ID, THREADS_NUMBER, DAMAGES
    global WINDOW, FONT, SOUNDS, IMAGES, WORLD_MAP_RECT
    global HUMAN_PERSONS, NPC_PERSONS, ITEMS, SPRITES, TREETOPS, DEAD_NPC, GAME_OBJECTS

    # Online related vars
    local_url = get_local_ip()
    host = local_url
    PLAYER_ID = 1  # Must be unique among other players on the network
    players = 1
    url = local_url
    port = 5241

    pygame.init()
    info = pygame.display.Info()
    WIDTH = 1600 if ON_ANDROID else info.current_w
    HEIGHT = 800 if ON_ANDROID else info.current_h
    pygame.display.set_icon(pygame.image.load(os.path.join(GRAPH_PATH, "icon.png")))
    pygame.display.set_caption("Adventurer's Path")
    WINDOW = pygame.display.set_mode(
        (WIDTH, HEIGHT),
        pygame.SCALED | pygame.FULLSCREEN,
        vsync=1
    )

    back_img = pygame.transform.scale(
        surface=pygame.image.load(os.path.join(GRAPH_PATH, "menu_background.png")),
        size=(WIDTH, HEIGHT)
    )

    w = WIDTH / 3
    h = HEIGHT / 7
    h07 = h / 1.5
    padding = h / 4
    left = WIDTH - w - padding
    settings_rect = (
        padding,
        (HEIGHT / 2) - padding,
        (padding * 2) + w,
        HEIGHT / 2
    )

    title = Text((left, 0, w, h),"Adventurer's Path", WHITE, 50, True)

    def setup_button(text: str, bottom_offset: float):
        font = pygame.font.Font("freesansbold.ttf", 25)
        return Button(
            (left, HEIGHT - h - bottom_offset, w, h),
            font.render(text, True, BLACK),
            True
        )

    start_single_button = setup_button("Start Single-Player Game", h * 3 + padding * 4)
    create_online_button = setup_button("Create New Online Game", h * 2 + padding * 3)
    connect_button = setup_button("Connect To Online Game", h + padding * 2)
    exit_button = setup_button("Exit", padding)

    def get_pos(y_offset: float):
        return padding + 20, (HEIGHT / 2) - padding + 20 + y_offset, w

    host_not_edit = EditText(
        f"{host}", "Address for players to connect to you",
        25, BLACK, get_pos(0), False
    )
    players_edit = EditText(
        f"{players}", "Players that will be connected to you",
        25, BLACK, get_pos(h07)
    )
    player_id_edit = EditText(
        f"{PLAYER_ID}", "Your ID (must be unique among players)",
        25, BLACK, get_pos(h07 * 2)
    )
    url_edit = EditText(
        f"{url}", "Address to connect",
        25, BLACK, get_pos(h07 * 3)
    )

    # Menu loop
    clock = pygame.time.Clock()
    err_msg = ""
    game_mode = ""
    while True:
        if game_mode != "":
            if game_mode == "exit":
                break
            else:
                # Check if data is OK before break loop
                try:
                    players = int(players_edit.text)
                    PLAYER_ID = int(player_id_edit.text)
                    url = url_edit.text
                    IS_HOST = True
                    THREADS_NUMBER = 1
                    ONLINE = None
                    if game_mode == "create":
                        ONLINE = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        ONLINE.bind((host, port))
                        ONLINE.listen(players)
                        THREADS_NUMBER = players
                    elif game_mode == "connect":
                        ONLINE = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        ONLINE.connect((url, port))
                        IS_HOST = False
                    break
                except Exception as e:
                    game_mode = ""
                    err_msg = f"Settings error: {e}"
                    print(err_msg)

        WINDOW.blit(back_img, (0, 0, WIDTH, HEIGHT))
        pygame.draw.rect(WINDOW, WHITE, settings_rect, border_radius=10)
        pygame.draw.rect(WINDOW, BLACK, settings_rect, width=1, border_radius=10)

        if err_msg != "":
            Text((padding, 0, w, h),err_msg, RED, 30, True, False).draw()

        title.draw()

        events = pygame.event.get()

        host_not_edit.on_tick(events)
        players_edit.on_tick(events)
        player_id_edit.on_tick(events)
        url_edit.on_tick(events)

        for event in events:
            if get_is_back_clicked(event):
                game_mode = "exit"
                time.sleep(0.3)
        if start_single_button.draw_get_is_clicked():
            game_mode = "offline"
            time.sleep(0.3)
        if create_online_button.draw_get_is_clicked():
            game_mode = "create"
            time.sleep(0.3)
        if connect_button.draw_get_is_clicked():
            game_mode = "connect"
            time.sleep(0.3)
        if exit_button.draw_get_is_clicked():
            game_mode = "exit"
            time.sleep(0.3)

        pygame.display.flip()
        clock.tick(FPS)

    if game_mode == "exit":
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    while True:
        run_main_menu()
        run_game()