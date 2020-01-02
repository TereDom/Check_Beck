import pygame
import os
import random

pygame.init()
inventory_sprites = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
size = width, height = 850, 500
screen = pygame.display.set_mode(size)
tile_width = tile_height = 50
CHEST_LOOT = ['potion', 'ammo', 'key']
LOOTS_WEIGHTS = [30, 30, 10]
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
    max_width = max(map(len, level_map))
    return level_map


def generate_level(level):
    new_player, x, y, chests = None, None, None, dict()
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '!':
                Tile("empty", x, y)
                chests[(y, x)] = Chest((x, y))
            elif level[y][x] == '@':
                Tile('empty', x, y)
    gun = FirstWeapon()
    knife = SecondWeapon()
    new_player = Player(3, 3, load_level('map.txt'))
    return new_player, x, y, chests, gun, knife


def upgrade_inventory():
    screen.fill((0, 0, 0), pygame.Rect(650, 0, 850, 500))
    pygame.draw.rect(screen, (255, 255, 255), (660, 5, 180, 35), 1)
    pygame.draw.rect(screen, (255, 255, 255), (660, 65, 180, 65), 1)

    pygame.draw.rect(screen, (255, 255, 255), (680, 70, 55, 55), 1)
    pygame.draw.rect(screen, (255, 255, 255), (765, 70, 55, 55), 1)
    pygame.draw.rect(screen, (255, 255, 255), (660, 155, 55, 55), 1)
    pygame.draw.rect(screen, (255, 255, 255), (785, 155, 55, 55), 1)
    pygame.draw.rect(screen, (255, 255, 255), (660, 240, 55, 55), 1)
    pygame.draw.rect(screen, (255, 255, 255), (785, 240, 55, 55), 1)
    pygame.draw.rect(screen, (255, 255, 255), (660, 310, 180, 180), 1)
    pygame.draw.rect(screen, pygame.color.Color('red'), (661, 6, HEALTH_BAR_SIZE / HP * player.hp, 33))
    inventory_sprites.draw(screen)


def set_direction_k(event, direction, move):
    if event.key == pygame.K_W:
        direction = 'up'
        move = True
    elif event.key == pygame.K_s:
        direction = 'down'
        move = True
    elif event.key == pygame.K_a:
        direction = 'left'
        move = True
    elif event.key == pygame.K_d:
        direction = 'right'
        move = True
    else:
        direction = None
        move = False
    if direction is None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            direction = "up"
            move = True
        elif keys[pygame.K_s]:
            direction = 'down'
            move = True
        elif keys[pygame.K_a]:
            direction = 'left'
            move = True
        elif keys[pygame.K_d]:
            direction = 'right'
            move = True
        else:
            direction = None
            move = False
    return direction, move


def set_direction_j(joistick, direction, move):
    axis0 = joistick.get_axis(0)
    axis1 = joistick.get_axis(1)
    axis0 = 0 if -0.1 <= axis0 <= 0.1 else axis0
    axis1 = 0 if -0.1 <= axis1 <= 0.1 else axis1

    if abs(axis0) > abs(axis1):
        if axis0 >= 0.1:
            direction = 'right'
            move = True
        elif axis0 <= -0.1:
            direction = 'left'
            move = True
    elif abs(axis0) < abs(axis1):
        if axis1 >= 0.1:
            direction = 'down'
            move = True
        elif axis1 <= -0.1:
            direction = 'up'
            move = True
    else:
        direction = None
        move = False
    return direction, move


def set_direction_j_hat(event, direction, move):
    if event.value == (0, 1):
        direction = 'up'
        move = True
    elif event.value == (0, -1):
        direction = 'down'
        move = True
    elif event.value == (1, 0):
        direction = 'right'
        move = True
    elif event.value == (-1, 0):
        direction = 'left'
        move = True
    elif event.value == (0, 0):
        direction = None
        move = False
    return direction, move


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        tile_images = {'wall': load_image('wall.png'), 'empty': load_image('floor.png')}
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = list(load_level('map.txt'))
        self.left = 0
        self.top = 0
        self.cell_size = 0

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self):
        pass


class Creatures:
    def __init__(self, hp, coords):
        self.hp = hp
        self.coords = coords


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, map):
        super().__init__(all_sprites)
        self.image = player_image
        self.inventory = dict()
        self.weapons = list()
        self.x, self.y = pos_x, pos_y
        self.image = load_image('Player_down.png')
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.map = map
        self.map = [list(i) for i in self.map]

    def update(self, direction):
        x = int(self.x)
        y = int(self.y)
        if (direction == 'up' and self.map[y + (1 if self.y % 1 != 0 else 0) - 1][x] != '#' and
                self.map[y + (1 if self.y % 1 != 0 else 0) - 1][x + (1 if self.x % 1 != 0 else 0)] != '#'):
            self.rect = self.rect.move(0, -25)
            self.y -= 0.5
            self.image = load_image('Player_Up.png')
        if (direction == 'down' and self.map[y + 1][x] != "#" and
                self.map[y + 1][x + (1 if self.x % 1 != 0 else 0)] != '#'):
            self.rect = self.rect.move(0, 25)
            self.y += 0.5
            self.image = load_image('Player_Down.png')
        if (direction == 'right' and self.map[y][x + 1] != '#' and
                self.map[y + (1 if self.y % 1 != 0 else 0)][x + 1] != '#'):
            self.rect = self.rect.move(25, 0)
            self.x += 0.5
            self.image = load_image('Player_right.png')
        if (direction == 'left' and self.map[y][x + (1 if self.x % 1 != 0 else 0) - 1] != '#' and
                self.map[y + (1 if self.y % 1 != 0 else 0)][x + (1 if self.x % 1 != 0 else 0) - 1] != '#'):
            self.rect = self.rect.move(-25, 0)
            self.x -= 0.5
            self.image = load_image('Player_left.png')


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


class Bat(Creatures):
    def __init__(self, hp, coords):
        super().__init__(hp, coords)
        self.__damage__ = None


class Dragon(Creatures):
    def __init__(self, hp, coords):
        super().__init__(hp, coords)
        self.__damage__ = None


class SkeletonBomber(Creatures):
    def __init__(self, hp, coords):
        super().__init__(hp, coords)
        self.__damage__ = None


class Frankenstein(Creatures):
    def __init__(self, hp, coords):
        super().__init__(hp, coords)
        self.__damage__ = None


class Potion(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_sprites)
        self.image = load_image('potion.png')
        self.rect = (785, 150)

    def update(self):
        pass


class Key(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_sprites)
        self.image = load_image('key.png')
        self.rect = (660, 240)

    def update(self):
        pass


class Ammo(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_sprites)
        self.image = load_image('ammo.png')
        self.rect = (660, 150)

    def update(self):
        pass


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
        if self.loot_name == "<class '__main__.Key'>":
            self.loot_num = 1
            CHEST_LOOT.pop()
            LOOTS_WEIGHTS.pop()
        elif self.loot_name == "<class '__main__.Potion'>":
            self.loot_num = random.randint(1, 3)
        elif self.loot_name == "<class '__main__.Ammo'>":
            self.loot_num = random.randint(5, 20)

    def open_chest(self):
        global chests_found
        pygame.mixer.music.load("data/ammo_picked.mp3") if self.loot_name == 'ammo' \
            else pygame.mixer.music.load("data/potion_picked.mp3")
        self.image = load_image('open_chest.png')
        pygame.mixer.music.play(1)
        chests_found += 1


class FirstWeapon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_sprites)
        self.image = load_image('gun.png')
        self.rect = (680, 70)


class SecondWeapon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_sprites)
        self.image = load_image('knife.png')
        self.rect = (765, 70)


class Potion(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_sprites)
        self.image = load_image('')
        self.rect = (x, y)

    def update(self):
        pass


class Key(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_sprites)
        self.image = load_image('')
        self.rect = (x, y)

    def update(self):
        pass
        pygame.mixer.music.play(1)
        chests_found += 1


class FirstWeapon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_sprites)
        self.image = load_image('gun.png')
        self.rect = (680, 70)


class SecondWeapon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_sprites)
        self.image = load_image('knife.png')
        self.rect = (765, 70)


player_image = load_image('Player_down.png')
gamemap = GameMap(98, 98)
player, level_x, level_y, chests, gun, knife = generate_level(load_level('map.txt'))

if pygame.joystick.get_count():
    stick = pygame.joystick.Joystick(0)
    stick.init()
if pygame.joystick.get_count():
    stick = pygame.joystick.Joystick(0)
    stick.init()
else:
    stick = None

clock = pygame.time.Clock()
time = 0
camera = Camera()
running = True
move = False
direction = None

while running:
    screen.fill(pygame.color.Color("black"))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.JOYHATMOTION:
            direction, move = set_direction_j_hat(event, direction, move)
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 7:
                running = False
            if event.button == 0 and player.map[int(player.y)][int(player.x)] == '!':
                chest = chests[(int(player.y), int(player.x))]
                chest.open_chest()
                player.inventory[chest.loot_name] = chest.loot_num
                player.map[int(player.y)][int(player.x)] = '?'
                del chests[(int(player.y), int(player.x))]
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 7:
                running = False
            if event.button == 0 and player.map[int(player.y)][int(player.x)] == '!':
                chest = chests[(int(player.y), int(player.x))]
                chest.open_chest()
                player.inventory[chest.loot_name] = chest.loot_num
                player.map[int(player.y)][int(player.x)] = '?'
                del chests[(int(player.y), int(player.x))]
        if event.type == pygame.KEYDOWN:
            if player.map[int(player.y)][int(player.x)] == '!' and event.key == pygame.K_e:
                chest = chests[(int(player.y), int(player.x))]
                chest.open_chest()
                if chest.loot_name in player.inventory.keys():
                    player.inventory[chest.loot_name] += chest.loot_num
                else:
                    player.inventory[chest.loot_name] = chest.loot_num
                player.map[int(player.y)][int(player.x)] = '?'
                del chest
            direction, move = set_direction_k(event, direction, move)
        if event.type == pygame.KEYUP:
            move = False
            direction = None

    if stick is not None and direction is None:
        direction, move = set_direction_j(stick, direction, move)

    time += clock.tick()
    if move and time >= 150:
        player.update(direction)
        time = 0

    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)

    gamemap.render()
    all_sprites.draw(screen)
    upgrade_inventory()
#   inventory_sprites.draw(screen)
    pygame.display.flip()

if stick is not None:
    stick.quit()
pygame.quit()
