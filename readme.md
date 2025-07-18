# Adventurer's Path (PC & Android)
*A short isometric game project with combat, loot, and local co-op!*

The player survived the storm and found himself on a small island with hostile skeletons. Help him defeat evil and find treasures.

<img src="https://github.com/lestec-al/isometric-fantasy-game/raw/main/pic_game_7.jpg" width="375" height="225" alt="Android"/>  <img src="https://github.com/lestec-al/isometric-fantasy-game/raw/main/pic_game_8.jpg" width="375" height="225" alt="Android"/>
<img src="https://github.com/lestec-al/isometric-fantasy-game/raw/main/pic_game_1.png" width="375" height="225" alt="Windows"/>  <img src="https://github.com/lestec-al/isometric-fantasy-game/raw/main/pic_game_4.png" width="375" height="225" alt="Windows"/>
<img src="https://github.com/lestec-al/isometric-fantasy-game/raw/main/pic_game_5.png" width="375" height="225" alt="Windows"/>  <img src="https://github.com/lestec-al/isometric-fantasy-game/raw/main/pic_game_6.png" width="375" height="225" alt="Windows"/>

## Mechanics
- Player/NPCs with animations, battle logic, skills (spear, sword), inventory, items, health, energy.
- Items types: weapons, clothes, potions, coins (and chests for them).
- NPC enemy move (with collisions, when player in some radius) and attack the player.
- NPC trader sells/buys items for 100 coins per item.
- Interface, sounds, small world map with NPCs.
- Online gameplay on local network, ~2-3 players (for now only on PC).
- Game is works on PC & Android (APK build with [python-for-android](https://github.com/kivy/python-for-android)).

## Controls
#### PC
| Key  | Action        |  
|------|---------------|  
| WASD | Move          |  
| F    | Attack        |  
| E    | Append item   |  
| R    | Looting/Trade |  
| Q    | Inventory     |
| ESC  | Exit          |
#### Android
- Touch buttons.
- Accelerometer (click on left/bottom button -> rotate your device to move).

## Installation & running
See releases and pick from them. Or for direct running the code:
- install Python (v3.10 or higher).
- install frameworks from "requirements.txt" (it is advised to create virtual environment and install there).
- download (and extract) or clone this repo.
- launch via command line "python menu.py" in the project folder.

## The project used
- the map was created using the level editor "Tiled" - https://www.mapeditor.org
- character sprites - https://opengameart.org/content/character-animations-clothes-armor-weapons-skeleton-enemy-combat-dummy
- world map graphics - https://opengameart.org/content/2d-lost-garden-tileset-transition-to-jetrels-wood-tileset
- some items icons - http://dycha.net
- box icons - https://opengameart.org/content/jrpg-chests-16-32-64-and-128px-squared
- some sounds - https://darkworldaudio.itch.io/sound-effects-survival-i
- forest sound - https://opengameart.org/content/forest-ambience
- beach waves sound - https://opengameart.org/content/beach-ocean-waves