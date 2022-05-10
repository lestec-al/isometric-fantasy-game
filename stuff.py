import pygame, os, sys, time
from pygame.locals import *
from settings import *

class Object():
    def __init__(self, id, map, obj_type):
        self.id = id
        self.map = map
        self.obj_type = obj_type

class Item():
    def __init__(self, id, obj_type, image):
        self.id = id
        self.obj_type = obj_type
        self.image = image
        self.map = pygame.Rect(0, 0, scale/2, scale/2)

class Weapon(Item):
    def __init__(self, id, obj_type, image, anim, damage, cooldown_time):
        Item.__init__(self, id, obj_type, image)
        self.anim = anim
        self.damage = damage
        self.cooldown_time = cooldown_time

class Outfit(Item):
    def __init__(self, id, obj_type, image, anim, armor):
        Item.__init__(self, id, obj_type, image)
        self.anim = anim
        self.armor = armor

class Potion(Item):
    def __init__(self, id, obj_type, image, health_for_adding):
        Item.__init__(self, id, obj_type, image)
        self.health_for_adding = health_for_adding

    def drink_potion(self, player):
        if player.health + self.health_for_adding > player.health_bar_width:
            player.health = player.health_bar_width
        else:
            player.health += self.health_for_adding