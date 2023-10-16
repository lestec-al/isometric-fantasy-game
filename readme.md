# Adventurer's Path game

The player survived the storm and found himself on a small island with hostile skeletons. Help him defeat evil and find treasures.

<img src="https://github.com/lestec-al/adventurer-s-path-game/raw/main/graphics/pic_game_1.png" width="375" height="225"/>  <img src="https://github.com/lestec-al/adventurer-s-path-game/raw/main/graphics/pic_game_4.png" width="375" height="225"/>
<img src="https://github.com/lestec-al/adventurer-s-path-game/raw/main/graphics/pic_game_5.png" width="375" height="225"/>  <img src="https://github.com/lestec-al/adventurer-s-path-game/raw/main/graphics/pic_game_6.png" width="375" height="225"/>

## Description

This is a demo project of an isometric fantasy game. One small level is ready. You can play alone or with friends over a local network.

Keyboard controls:
- wasd: move
- f: attack
- e: append item
- i: inventory / looting / trade
    - mouse left-click: equip / use item
    - mouse right-click: remove / sell item

Mechanics:
- player/NPC with animations, battle logic, skills (spear, sword), inventory, items, health, energy
- type items: weapons, clothes, potions, coins and chests for them
- NPC enemy move (with colisions, when player in some radius) and attack the player
- NPC trader sells/buys items for 100 coins per item
- interface, sounds, simple world map with NPCs
- online gameplay on local network, ~2-3 players


## Installation

- install Python (v3.10 or higher)
- install PyGame, Pillow, Tkinter
- download (and extract) or clone this repo
- launch via command line "python game.py" in the project folder


## The project used

- the map was created using the level editor "Tiled" - https://www.mapeditor.org
- character sprites - https://opengameart.org/content/character-animations-clothes-armor-weapons-skeleton-enemy-combat-dummy
- world map graphics - https://opengameart.org/content/2d-lost-garden-tileset-transition-to-jetrels-wood-tileset
- some items icons - http://dycha.net
- box icons - https://opengameart.org/content/jrpg-chests-16-32-64-and-128px-squared
- some sounds - https://darkworldaudio.itch.io/sound-effects-survival-i
- forest sound - https://opengameart.org/content/forest-ambience
- beach waves sound - https://opengameart.org/content/beach-ocean-waves