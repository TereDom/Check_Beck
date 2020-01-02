import pygame
import os
import random

inventory_sprites = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
size = width, height = 850, 500
screen = pygame.display.set_mode(size)
tile_width = tile_height = 50
CHEST_LOOT = ['potion', 'ammo', 'key']


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
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
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


class Chest(pygame.sprite.Sprite):
    def __init__(self, coords):
        super().__init__(all_sprites)
        self.image = load_image('close_chest.png')
        self.coords = coords
        self.loot_name = random.choice(CHEST_LOOT)
        self.rect = self.image.get_rect().move(tile_width * coords[0],
                                               tile_height * coords[1])
        if self.loot_name == 'key':
            self.loot_num = 1
            CHEST_LOOT.pop()
        elif self.loot_name == 'potion':
            self.loot_num = random.randint(1, 3)
        elif self.loot_name == 'ammo':
            self.loot_num = random.randint(15, 40)

    def open_chest(self):
        self.image = load_image('open_chest.png')


class FirstWeapon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_sprites)
        self.image = load_image('gun.png')
        self.rect = (680, 0)


class SecondWeapon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_sprites)
        self.image = load_image('knife.png')
        self.rect = (765, 0)


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


player_image = load_image('Player_down.png')
gamemap = GameMap(98, 98)
player, level_x, level_y, chests, gun, knife = generate_level(load_level('map.txt'))


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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e and player.map[int(player.y)][int(player.x)] == '!':
                chest = chests[(int(player.y), int(player.x))]
                chest.open_chest()
                player.inventory[chest.loot_name] = chest.loot_num
                del chest
            if event.key == pygame.K_w:
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
        if event.type == pygame.KEYUP:
            direction = None
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
    time += clock.tick()
    if move and time >= 150:
        player.update(direction)
        time = 0

    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)

    gamemap.render()
    all_sprites.draw(screen)
    screen.fill((0, 0, 0), pygame.Rect(650, 0, 850, 500))
    pygame.draw.rect(screen, (255, 255, 255), (660, 5, 180, 35), 1)
    pygame.draw.rect(screen, (255, 255, 255), (660, 65, 180, 65), 1)
    pygame.draw.rect(screen, (255, 255, 255), (680, 70, 55, 55), 1)
    pygame.draw.rect(screen, (255, 255, 255), (765, 70, 55, 55), 1)
    pygame.draw.rect(screen, (255, 255, 255), (660, 155, 55, 55), 1)
    pygame.draw.rect(screen, (255, 255, 255), (785, 155, 55, 55), 1)
    pygame.draw.rect(screen, (255, 255, 255), (660, 240, 55, 55), 1)
    pygame.draw.rect(screen, (255, 255, 255), (785, 240, 55, 55), 1)



 #   inventory_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
