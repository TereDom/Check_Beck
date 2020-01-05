import pygame
import os
import random

pygame.init()
inventory_sprites = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
monsters_group = pygame.sprite.Group()
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
    max_width = max(map(len, level_map))
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
                monsters[(y - 1, x - 1)] = random.choices(LIST_OF_MONSTERS)[0]((y - 1, x - 1))
            elif level[y][x] == '@':
                Tile('empty', x, y)
            elif level[y][x] == '*':
                Tile('door', x, y)
    gun = FirstWeapon()
    knife = SecondWeapon()
    new_player = Player(3, 3, load_level('map.txt'))
    return new_player, x, y, chests, gun, knife, monsters


def upgrade_inventory():
    screen.fill((51, 20, 20), pygame.Rect(650, 0, 850, 500))
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
    print(direction)

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
        self.hp = HP
        self.direction = 'down'

    def update(self, direction):
        x = int(self.x)
        y = int(self.y)
        if (direction == 'up' and self.map[y + (1 if self.y % 1 != 0 else 0) - 1][x] != '#' and
                self.map[y + (1 if self.y % 1 != 0 else 0) - 1][x + (1 if self.x % 1 != 0 else 0)] != '#'):
            self.rect = self.rect.move(0, -25)
            self.y -= 0.5
            self.image = load_image('Player_up.png')
            self.direction = 'up'
        if (direction == 'down' and self.map[y + 1][x] != "#" and
                self.map[y + 1][x + (1 if self.x % 1 != 0 else 0)] != '#'):
            self.rect = self.rect.move(0, 25)
            self.y += 0.5
            self.image = load_image('Player_down.png')
            self.direction = 'down'
        if (direction == 'right' and self.map[y][x + 1] != '#' and
                self.map[y + (1 if self.y % 1 != 0 else 0)][x + 1] != '#'):
            self.rect = self.rect.move(25, 0)
            self.x += 0.5
            self.image = load_image('Player_right.png')
            self.direction = 'right'
        if (direction == 'left' and self.map[y][x + (1 if self.x % 1 != 0 else 0) - 1] != '#' and
                self.map[y + (1 if self.y % 1 != 0 else 0)][x + (1 if self.x % 1 != 0 else 0) - 1] != '#'):
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
    def __init__(self, coords):
        super().__init__(monsters_group)
        self.image = load_image('bat_down.png')
        self.HP = 50
        self.DAMAGE = None
        self.coords = coords
        self.rect = self.coords


class Dragon(pygame.sprite.Sprite):
    def __init__(self, coords):
        super().__init__(monsters_group)
        self.image = load_image('dragon_down.png')
        self.HP = 50
        self.DAMAGE = None
        self.coords = coords
        self.rect = self.coords


class SkeletonBomber(pygame.sprite.Sprite):
    def __init__(self, coords):
        super().__init__(monsters_group)
        self.image = load_image('SkeletonBomber_down.png')
        self.HP = 50
        self.DAMAGE = None
        self.coords = coords
        self.rect = self.coords


class Frankenstein(pygame.sprite.Sprite):
    def __init__(self, coords):
        super().__init__(monsters_group)
        self.image = load_image('frankenstein_down.png')
        self.HP = 50
        self.DAMAGE = None
        self.coords = coords
        self.rect = self.coords


LIST_OF_MONSTERS = [Bat((None, None)), Dragon((None, None)),
                    SkeletonBomber((None, None)), Frankenstein((None, None))]


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
        if str(self.loot_name.__class__) == "<class '__main__.Key'>":
            self.loot_num = 1
            CHEST_LOOT.pop()
            LOOTS_WEIGHTS.pop()
        elif str(self.loot_name.__class__) == "<class '__main__.Potion'>":
            self.loot_num = random.randint(1, 3)
        elif str(self.loot_name.__class__) == "<class '__main__.Ammo'>":
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


player_image = load_image('Player_down.png')
gamemap = GameMap(98, 98)
player, level_x, level_y, chests, gun, knife, monsters = generate_level(load_level('map.txt'))

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
flag = True

while running:
    screen.fill(pygame.color.Color("black"))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.JOYHATMOTION:
            direction, move, flag = set_direction_hat(event)
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 7 or event.button == 6:
                running = False
            if event.button == 0 and player.map[int(player.y)][int(player.x)] == '!':
                chest = chests[(int(player.y), int(player.x))]
                chest.open_chest()
                if chest.loot_name in player.inventory.keys():
                    player.inventory[chest.loot_name] += chest.loot_num
                else:
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
            set_direction_uldr(player, event)
        if event.type == pygame.JOYAXISMOTION and event.axis in (2, 3):
            print('ok')
            set_direction_rs(player, stick)

        if event.type in (pygame.KEYUP, pygame.KEYDOWN):
            direction, move = set_direction_wasd(event)

    if stick is not None and flag:
        direction, move = set_direction_ls(stick)

    time += clock.tick()
    if move and time >= 150:
        player.update(direction)
        time = 0

    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)

    gamemap.render()
    all_sprites.draw(screen)
    monsters_group.draw(screen)
    upgrade_inventory()
    inventory_sprites.draw(screen)
    pygame.display.flip()

if stick is not None:
    stick.quit()
pygame.quit()
