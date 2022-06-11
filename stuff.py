import pygame
from pygame.locals import *
from settings import *

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
        self.map = pygame.Rect(0, 0, scale, scale)

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

    def drink_potion(self, player):
        if "health" in self.name.lower():
            if player.health + self.for_adding > player.health_bar_width:
                player.health = player.health_bar_width
            else:
                player.health += self.for_adding
        elif "energy" in self.name.lower():
            if player.energy + self.for_adding > player.energy_bar_width:
                player.energy = player.energy_bar_width
            else:
                player.energy += self.for_adding

class Coins(Item):
    def __init__(self, id, name, obj_type, image, amount):
        super().__init__(id, name, obj_type, image)
        self.amount = amount