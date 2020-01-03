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
    inventory = Inventory(width, height)
    new_player = Player(3, 3, load_level('map.txt'))
    return new_player, x, y, chests, gun, knife, inventory


class Inventory:
    def __init__(self, width, height):
        self.x = width * 0.76
        self.width = width - self.x

    def draw_health_bar(self):
        pygame.draw.rect(screen, (255, 255, 255), (int(self.x + self.width * 0.059), height // 100,
                                                   int(width - self.width * 0.059 * 2 - self.x) + 1, height * 0.07), 1)
        pygame.draw.rect(screen, pygame.color.Color('red'), (int(self.x + self.width * 0.059) + 1,
                                                             height * 0.012,
                                                             int(width - self.width * 0.059 * 2 - self.x)
                                                             / HP * player.hp - 1,
                                                             height * 0.066))

    def draw_slots(self):
        width_of_slots = 55
        pygame.draw.rect(screen, (255, 255, 255), (int(self.x + self.width * 0.059), height * 0.13, self.width * 0.882,
                                                   height * 0.13), 1)

        pygame.draw.rect(screen, (255, 255, 255), (int(self.x + self.width * 0.157), height * 0.14, width_of_slots,
                                                   width_of_slots), 1)

        pygame.draw.rect(screen, (255, 255, 255), (int(self.x + self.width * 0.57), height * 0.14, width_of_slots,
                                                   width_of_slots), 1)

        pygame.draw.rect(screen, (255, 255, 255), (int(self.x + self.width * 0.059), height * 0.31, width_of_slots,
                                                   width_of_slots), 1)

        pygame.draw.rect(screen, (255, 255, 255), (int(self.x + self.width * 0.67), height * 0.31, width_of_slots,
                                                   width_of_slots), 1)

        pygame.draw.rect(screen, (255, 255, 255), (int(self.x + self.width * 0.059), height * 0.48, width_of_slots,
                                                   width_of_slots), 1)
        pygame.draw.rect(screen, (255, 255, 255), (int(self.x + self.width * 0.67), height * 0.48,  width_of_slots,
                                                   width_of_slots), 1)
        pygame.draw.rect(screen, (255, 255, 255), (int(self.x + self.width * 0.059), height * 0.62, self.width * 0.88,
                                                   self.width * 0.88), 1)

    def upgrade(self):
        screen.fill((51, 20, 20), pygame.Rect(646, 0, 850, 500))
        self.draw_health_bar()
        self.draw_slots()
        inventory_sprites.draw(screen)




def set_direction_wasd(event):
    direction = None
    move = True
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


def set_direction_j_ls(joistick):
    axis0 = joistick.get_axis(0)
    axis1 = joistick.get_axis(1)
    axis0 = 0 if -0.1 <= axis0 <= 0.1 else axis0
    axis1 = 0 if -0.1 <= axis1 <= 0.1 else axis1

    direction = None
    move = True
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


def set_direction_j_hat(event):
    direction = None
    move = True
    flag = False
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
        self.hp = HP

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
        self.rect = (783, 150)

    def update(self):
        pass


class Key(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_sprites)
        self.image = load_image('key.png')
        self.rect = (658, 240)

    def update(self):
        pass


class Ammo(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_sprites)
        self.image = load_image('ammo.png')
        self.rect = (658, 150)

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
        self.rect = (678, 70)


class SecondWeapon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_sprites)
        self.image = load_image('knife.png')
        self.rect = (763, 70)


player_image = load_image('Player_down.png')
gamemap = GameMap(98, 98)
player, level_x, level_y, chests, gun, knife, inventory = generate_level(load_level('map.txt'))

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
            direction, move, flag = set_direction_j_hat(event)
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 7:
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
        if event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:
            direction, move = set_direction_wasd(event)
    if stick is not None and flag:
        direction, move = set_direction_j_ls(stick)

    time += clock.tick()
    if move and time >= 150:
        player.update(direction)
        time = 0

    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)

    gamemap.render()
    all_sprites.draw(screen)
    inventory.upgrade()
    pygame.display.flip()

if stick is not None:
    stick.quit()
pygame.quit()
