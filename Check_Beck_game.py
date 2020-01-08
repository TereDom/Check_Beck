import pygame
import os
import random

pygame.init()
weapons_group = pygame.sprite.Group()
chest_group = pygame.sprite.Group()
inventory_sprites = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
monsters_group = pygame.sprite.Group()
LIST_OF_MONSTERS = ['Bat', 'Dragon', 'SkeletonBomber', 'Frankenstein']
size = width, height = 850, 500
screen = pygame.display.set_mode(size)
tile_width = tile_height = 50
HP = 50
HEALTH_BAR_SIZE = 178
chests_found = 0


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    return level_map


def generate_level(level):
    new_player, x, y, chests, monsters = None, None, None, dict(), dict()
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '!':
                Tile("empty", x, y)
                chests[(y, x)] = Chest((x, y))
                monsters[(y - 1, x - 1)] = random_monster(random.choices(LIST_OF_MONSTERS)[0],
                                                          [x - 1, y - 1], (x, y))
            elif level[y][x] == '@':
                Tile('empty', x, y)
            elif level[y][x] == '*':
                Tile('door', x, y)
    gun = FirstWeapon()
    knife = SecondWeapon()
    new_player = Player(3, 3)
    gamemap = GameMap(98, 98, load_level('map.txt'))
    return gamemap, new_player, x, y, chests, gun, knife, monsters


def random_monster(name, coords, chest_coords):
    if name == 'Bat':
        return Bat(coords, chest_coords)
    elif name == 'Dragon':
        return Dragon(coords, chest_coords)
    elif name == 'SkeletonBomber':
        return SkeletonBomber(coords, chest_coords)
    elif name == 'Frankenstein':
        return Frankenstein(coords, chest_coords)


class Inventory:
    def __init__(self, width, height):
        self.x = width * 0.76
        self.width = width - self.x

    def draw_health_bar(self):
        screen.fill((51, 20, 20), pygame.Rect(self.x, 0, width, height))
        pygame.draw.rect(screen, (255, 255, 255), (self.x + ((self.width - int(self.width * 0.88)) // 2), 5,
                                                   (int(self.width * 0.88)), height * 0.07), 1)

        pygame.draw.rect(screen, pygame.color.Color('red'), (self.x + (self.width - int(self.width * 0.88)) // 2 + 1,
                                                             height * 0.012,
                                                             (int(self.width * 0.88) - 2) / HP * player.hp,
                                                             height * 0.07 - 2))

    def draw_slots(self):
        size_of_slots = 55
        size_of_map = 180
        pygame.draw.rect(screen, (255, 255, 255), (self.x + ((self.width - int(self.width * 0.88)) // 2),
                                                   height * 0.13, int(self.width * 0.88), height * 0.13), 1)

        pygame.draw.rect(screen, (255, 255, 255), (self.x + ((self.width - int(self.width * 0.88)) // 2)
                                                   + (int(self.width * 0.88) - size_of_slots * 2) // 4,
                                                   height * 0.14, size_of_slots, size_of_slots), 1)

        pygame.draw.rect(screen, (255, 255, 255), (self.x + ((self.width - int(self.width * 0.88)) // 2)
                                                   + int(self.width * 0.88) - (int(self.width * 0.88)
                                                                               - size_of_slots * 2) // 4
                                                   - size_of_slots,
                                                   height * 0.14, size_of_slots, size_of_slots), 1)

        pygame.draw.rect(screen, (255, 255, 255), (self.x + ((self.width - int(self.width * 0.88)) // 2), height * 0.31,
                                                   size_of_slots, size_of_slots), 1)

        pygame.draw.rect(screen, (255, 255, 255), (self.x + ((self.width - int(self.width * 0.88)) // 2)
                                                   + int(self.width * 0.88) - size_of_slots, height * 0.31,
                                                   size_of_slots, size_of_slots), 1)

        pygame.draw.rect(screen, (255, 255, 255), (self.x + ((self.width - int(self.width * 0.88)) // 2),
                                                   height * 0.48, size_of_slots, size_of_slots), 1)

        pygame.draw.rect(screen, (255, 255, 255), (self.x + ((self.width - int(self.width * 0.88)) // 2)
                                                   + int(self.width * 0.88) - size_of_slots,
                                                   height * 0.48, size_of_slots, size_of_slots), 1)

        pygame.draw.rect(screen, (255, 255, 255), (self.x + ((self.width - size_of_map) // 2),
                                                   height * 0.62, size_of_map, size_of_map), 1)

    def draw_numbers(self):
        shift_for_once = 45
        shift_for_twice = 38
        shift_for_thrice = 31
        shifts = [shift_for_once, shift_for_twice, shift_for_thrice]
        vertical_shift = 46
        for sprite in chest_group:
            if player.inventory[sprite.type] != 0:
                font = pygame.font.Font(None, 20)
                text = font.render((str(player.inventory[sprite.type])), 1, (100, 255, 100))
                text_x = sprite.rect[0] + shifts[len(str(player.inventory[sprite.type])) - 1]
                text_y = sprite.rect[1] + vertical_shift
                screen.blit(text, (text_x, text_y))

    def upgrade(self):
        self.draw_health_bar()
        self.draw_slots()
        self.draw_numbers()
        weapons_group.draw(screen)
        draw_sprites = pygame.sprite.Group()
        for sprite in chest_group:
            if player.inventory[sprite.type] != 0:
                draw_sprites.add(sprite)
        draw_sprites.draw(screen)


def set_direction_wasd(event):
    move = True
    direction = None
    if event.key == pygame.K_w:
        direction = 'up'
    elif event.key == pygame.K_s:
        direction = 'down'
    elif event.key == pygame.K_a:
        direction = 'left'
    elif event.key == pygame.K_d:
        direction = 'right'
    else:
        move = False
    if event.type == pygame.KEYUP and event.key in (pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d):
        keys = pygame.key.get_pressed()
        move = True
        if keys[pygame.K_w]:
            direction = "up"
        elif keys[pygame.K_s]:
            direction = 'down'
        elif keys[pygame.K_a]:
            direction = 'left'
        elif keys[pygame.K_d]:
            direction = 'right'
        else:
            move = False
    return direction, move


def set_direction_uldr(player, event):
    direction = player.direction
    if event.key == pygame.K_UP:
        direction = 'up'
    if event.key == pygame.K_DOWN:
        direction = 'down'
    if event.key == pygame.K_LEFT:
        direction = 'left'
    if event.key == pygame.K_RIGHT:
        direction = 'right'
    player.update_direction(direction)


def set_direction_ls(joistick):
    axis0 = joistick.get_axis(0)
    axis1 = joistick.get_axis(1)
    axis0 = 0 if -0.1 <= axis0 <= 0.1 else axis0
    axis1 = 0 if -0.1 <= axis1 <= 0.1 else axis1

    move = True
    direction = None
    if abs(axis0) > abs(axis1):
        if axis0 >= 0.1:
            direction = 'right'
        elif axis0 <= -0.1:
            direction = 'left'
    elif abs(axis0) < abs(axis1):
        if axis1 >= 0.1:
            direction = 'down'
        elif axis1 <= -0.1:
            direction = 'up'
    else:
        move = False
    return direction, move


def set_direction_rs(player, joistick):
    axis4 = joistick.get_axis(4)
    axis3 = joistick.get_axis(3)
    axis4 = 0 if -0.1 <= axis4 <= 0.1 else axis4
    axis3 = 0 if -0.1 <= axis3 <= 0.1 else axis3

    direction = player.direction
    if abs(axis4) > abs(axis3):
        if axis4 >= 0.1:
            direction = 'right'
        elif axis4 <= -0.1:
            direction = 'left'
    elif abs(axis4) < abs(axis3):
        if axis3 >= 0.1:
            direction = 'down'
        elif axis3 <= -0.1:
            direction = 'up'

    player.update_direction(direction)


def set_direction_hat(event):
    flag = False
    move = True
    direction = None
    if event.value == (0, 1):
        direction = 'up'
    elif event.value == (0, -1):
        direction = 'down'
    elif event.value == (1, 0):
        direction = 'right'
    elif event.value == (-1, 0):
        direction = 'left'
    elif event.value == (0, 0):
        move = False
        flag = True
    return direction, move, flag


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        tile_images = {'wall': load_image('wall.png'),
                       'empty': load_image('floor.png'), 'door': load_image('door.png')}
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class GameMap:
    def __init__(self, width, height, map):
        self.width = width
        self.height = height
        self.board = list(load_level('map.txt'))
        self.left = 0
        self.top = 0
        self.cell_size = 0
        self.map = map
        self.map = [list(i) for i in self.map]

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self):
        pass


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites)
        self.image = player_image
        self.inventory = {'Ammo': 0, 'Potion': 0, 'Key': 0}
        self.weapons = []
        self.x, self.y = pos_x, pos_y
        self.image = load_image('Player_down.png')
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.hp = HP
        self.direction = 'down'

    def update(self, direction):
        x = int(self.x)
        y = int(self.y)
        if (direction == 'up' and gamemap.map[y + (1 if self.y % 1 != 0 else 0) - 1][x] != '#' and
                gamemap.map[y + (1 if self.y % 1 != 0 else 0) - 1][x + (1 if self.x % 1 != 0 else 0)] != '#'):
            self.rect = self.rect.move(0, -25)
            self.y -= 0.5
            self.image = load_image('Player_up.png')
            self.direction = 'up'
        elif (direction == 'down' and gamemap.map[y + 1][x] != "#" and
              gamemap.map[y + 1][x + (1 if self.x % 1 != 0 else 0)] != '#'):
            self.rect = self.rect.move(0, 25)
            self.y += 0.5
            self.image = load_image('Player_down.png')
            self.direction = 'down'
        elif (direction == 'right' and gamemap.map[y][x + 1] != '#' and
              gamemap.map[y + (1 if self.y % 1 != 0 else 0)][x + 1] != '#'):
            self.rect = self.rect.move(25, 0)
            self.x += 0.5
            self.image = load_image('Player_right.png')
            self.direction = 'right'
        elif (direction == 'left' and gamemap.map[y][x + (1 if self.x % 1 != 0 else 0) - 1] != '#' and
              gamemap.map[y + (1 if self.y % 1 != 0 else 0)][x + (1 if self.x % 1 != 0 else 0) - 1] != '#'):
            self.rect = self.rect.move(-25, 0)
            self.x -= 0.5
            self.image = load_image('Player_left.png')
            self.direction = 'left'

    def update_direction(self, direction):
        self.direction = direction
        if direction == 'up':
            self.image = load_image("Player_up.png")
        elif direction == 'down':
            self.image = load_image("Player_down.png")
        elif direction == 'left':
            self.image = load_image('Player_left.png')
        elif direction == 'right':
            self.image = load_image('Player_right.png')


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2 + 100)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


class Bat(pygame.sprite.Sprite):
    def __init__(self, coords, chest_coords):
        super().__init__(all_sprites, monsters_group)
        self.image = load_image('bat_down.png')
        self.CHEST_COORDS = chest_coords
        self.HP = 50
        self.DAMAGE = None
        self.coords = coords
        self.rect = self.image.get_rect().move(tile_width * coords[0], tile_height * coords[1])
        self.direction = ('down', 0, 1)
        self.rage = False
        self.i = 0

    def update(self, direction):
        if not self.rage:
            self.rect = self.rect.move(self.direction[1] * 25, self.direction[2] * 25)
            self.coords[0] += self.direction[1] * 0.5
            self.coords[1] += self.direction[2] * 0.5
            self.i += 1
            if self.i == 4:
                self.direction = self.change_direction(self.direction)
                self.i = 0

    def change_direction(self, old_dir):
        possible_dir = [('down', 0, 1), ('right', 1, 0), ('up', 0, -1), ('left', -1, 0)]
        new_dir = possible_dir.index(old_dir) + 1
        new_dir = possible_dir[new_dir if new_dir != len(possible_dir) else 0]
        self.image = load_image('bat_' + new_dir[0] + '.png')
        return new_dir


class Dragon(pygame.sprite.Sprite):
    def __init__(self, coords, chest_coords):
        super().__init__(all_sprites, monsters_group)
        self.image = load_image('dragon_down.png')
        self.CHEST_COORDS = chest_coords
        self.HP = 50
        self.DAMAGE = None
        self.coords = coords
        self.rect = self.image.get_rect().move(tile_width * coords[0], tile_height * coords[1])
        self.direction = ('down', 0, 1)
        self.rage = False
        self.i = 0

    def update(self, direction):
        if not self.rage:
            self.rect = self.rect.move(self.direction[1] * 25, self.direction[2] * 25)
            self.coords[0] += self.direction[1] * 0.5
            self.coords[1] += self.direction[2] * 0.5
            self.i += 1
            if self.i == 4:
                self.direction = self.change_direction(self.direction)
                self.i = 0

    def change_direction(self, old_dir):
        possible_dir = [('down', 0, 1), ('right', 1, 0), ('up', 0, -1), ('left', -1, 0)]
        new_dir = possible_dir.index(old_dir) + 1
        new_dir = possible_dir[new_dir if new_dir != len(possible_dir) else 0]
        self.image = load_image('dragon_' + new_dir[0] + '.png')
        return new_dir


class SkeletonBomber(pygame.sprite.Sprite):
    def __init__(self, coords, chest_coords):
        super().__init__(all_sprites, monsters_group)
        self.image = load_image('skeleton_down.png')
        self.CHEST_COORDS = chest_coords
        self.HP = 50
        self.DAMAGE = None
        self.coords = coords
        self.rect = self.image.get_rect().move(tile_width * coords[0], tile_height * coords[1])
        self.direction = ('down', 0, 1)
        self.rage = False
        self.i = 0

    def update(self, direction):
        if not self.rage:
            self.rect = self.rect.move(self.direction[1] * 25, self.direction[2] * 25)
            self.coords[0] += self.direction[1] * 0.5
            self.coords[1] += self.direction[2] * 0.5
            self.i += 1
            if self.i == 4:
                self.direction = self.change_direction(self.direction)
                self.i = 0

    def change_direction(self, old_dir):
        possible_dir = [('down', 0, 1), ('right', 1, 0), ('up', 0, -1), ('left', -1, 0)]
        new_dir = possible_dir.index(old_dir) + 1
        new_dir = possible_dir[new_dir if new_dir != len(possible_dir) else 0]
        self.image = load_image('skeleton_' + new_dir[0] + '.png')
        return new_dir


class Frankenstein(pygame.sprite.Sprite):
    def __init__(self, coords, chest_coords):
        super().__init__(all_sprites, monsters_group)
        self.image = load_image('frankenstein_down.png')
        self.CHEST_COORDS = chest_coords
        self.HP = 50
        self.DAMAGE = None
        self.coords = coords
        self.rect = self.image.get_rect().move(tile_width * coords[0], tile_height * coords[1])
        self.direction = ('down', 0, 1)
        self.rage = False
        self.i = 0

    def update(self, direction):
        if not self.rage:
            self.rect = self.rect.move(self.direction[1] * 25, self.direction[2] * 25)
            self.coords[0] += self.direction[1] * 0.5
            self.coords[1] += self.direction[2] * 0.5
            self.i += 1
            if self.i == 4:
                self.direction = self.change_direction(self.direction)
                self.i = 0

    def change_direction(self, old_dir):
        possible_dir = [('down', 0, 1), ('right', 1, 0), ('up', 0, -1), ('left', -1, 0)]
        new_dir = possible_dir.index(old_dir) + 1
        new_dir = possible_dir[new_dir if new_dir != len(possible_dir) else 0]
        self.image = load_image('frankenstein_' + new_dir[0] + '.png')
        return new_dir


class Potion(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_sprites, chest_group)
        self.type = 'Potion'
        self.image = load_image('potion.png')
        self.rect = (inventory.x + ((inventory.width - int(inventory.width * 0.88)) // 2), height * 0.30)

    def update(self):
        pass


class Key(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_sprites, chest_group)
        self.type = 'Key'
        self.image = load_image('key.png')
        self.rect = (inventory.x + ((inventory.width - int(inventory.width * 0.88)) // 2)
                                                   + int(inventory.width * 0.88) - 55, height * 0.30)

    def update(self):
        pass


class Ammo(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_sprites, chest_group)
        self.type = 'Ammo'
        self.image = load_image('ammo.png')
        self.rect = (inventory.x + ((inventory.width - int(inventory.width * 0.88)) // 2), height * 0.47)

    def update(self):
        pass


class FirstWeapon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_sprites, weapons_group)
        self.image = load_image('gun.png')
        self.rect = (inventory.x + ((inventory.width - int(inventory.width * 0.88)) // 2)
                                                   + (int(inventory.width * 0.88) - 55 * 2) // 4, height * 0.14)


class SecondWeapon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_sprites, weapons_group)
        self.image = load_image('knife.png')
        self.rect = (inventory.x + ((inventory.width - int(inventory.width * 0.88)) // 2)
                                                   + int(inventory.width * 0.88) - (int(inventory.width * 0.88)
                                                                               - 55 * 2) // 4 - 55, height * 0.14)

inventory = Inventory(width, height)
CHEST_LOOT = [Potion(), Ammo(), Key()]
LOOTS_WEIGHTS = [30, 30, 10]


class Chest(pygame.sprite.Sprite):
    def __init__(self, coords):
        super().__init__(all_sprites)
        self.image = load_image('close_chest.png')
        self.coords = coords
        self.loot_name = random.choices(CHEST_LOOT, weights=LOOTS_WEIGHTS)[0]
        self.rect = self.image.get_rect().move(tile_width * coords[0],
                                               tile_height * coords[1])
        if self.loot_name.type == 'Key':
            self.loot_num = 1
            CHEST_LOOT.pop()
            LOOTS_WEIGHTS.pop()
        elif self.loot_name.type == 'Potion':
            self.loot_num = random.randint(1, 3)
        elif self.loot_name.type == 'Ammo':
            self.loot_num = random.randint(5, 20)

    def open_chest(self):
        global chests_found
        pygame.mixer.music.load("data/ammo_picked.mp3") if self.loot_name.type == 'Ammo' \
            else pygame.mixer.music.load("data/potion_picked.mp3")
        self.image = load_image('open_chest.png')
        pygame.mixer.music.play(1)
        chests_found += 1


player_image = load_image('Player_down.png')
gamemap, player, level_x, level_y, chests, gun, knife, monsters = generate_level(load_level('map.txt'))

if pygame.joystick.get_count():
    stick = pygame.joystick.Joystick(0)
    stick.init()
if pygame.joystick.get_count():
    stick = pygame.joystick.Joystick(0)
    stick.init()
else:
    stick = None

player_clock = pygame.time.Clock()
monster_clock = pygame.time.Clock()

player_timer = 0
monster_timer = 0

camera = Camera()
running = True
move = False
direction = None
flag = True

while running:
    screen.fill(pygame.color.Color("black"))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.JOYHATMOTION:
            direction, move, flag = set_direction_hat(event)
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 7:
                running = False
            if event.button == 0 and gamemap.map[int(player.y)][int(player.x)] == '!':
                chest = chests[(int(player.y), int(player.x))]
                chest.open_chest()
                player.inventory[chest.loot_name.type] += chest.loot_num
                gamemap.map[int(player.y)][int(player.x)] = '?'
                del chests[(int(player.y), int(player.x))]
        if event.type == pygame.KEYDOWN:
            if gamemap.map[int(player.y)][int(player.x)] == '!' and event.key == pygame.K_e:
                chest = chests[(int(player.y), int(player.x))]
                chest.open_chest()
                player.inventory[chest.loot_name.type] += chest.loot_num
                gamemap.map[int(player.y)][int(player.x)] = '?'
                del chest
            set_direction_uldr(player, event)
        if event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:
            direction, move = set_direction_wasd(event)

    if stick is not None and flag:
        direction, move = set_direction_ls(stick)

    player_timer += player_clock.tick()
    monster_timer += monster_clock.tick()

    if monster_timer >= 150:
        for monster in monsters_group:
            monster.update(monster.direction)
        monster_timer = 0

    if move and player_timer >= 150:
        player.update(direction)
        player_timer = 0

    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)

    gamemap.render()
    all_sprites.draw(screen)

    monsters_group.draw(screen)
    inventory.upgrade()
    pygame.display.flip()

if stick is not None:
    stick.quit()
pygame.quit()
