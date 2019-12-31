import pygame
import os


all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
size = width, height = 500, 400
screen = pygame.display.set_mode(size)
tile_width = tile_height = 50


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


BOARD = list(map(lambda row: list(row), load_level('map.txt')))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '!':
                Tile("chest", x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    return new_player, x, y


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        tile_images = {'wall': load_image('wall.png'), 'empty': load_image('floor.png'),
                       'chest': load_image('close_chest.png')}
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
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
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.inventory = dict()
        self.weapons = list()
        self.x = pos_x
        self.y = pos_y
        self.image = load_image('Player.png')
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

    def update(self, event):
        if event.key == pygame.K_w:
            self.rect = self.rect.move(0, -25)
        if event.key == pygame.K_s:
            self.rect = self.rect.move(0, 25)
        if event.key == pygame.K_d:
            self.rect = self.rect.move(25, 0)
        if event.key == pygame.K_a:
            self.rect = self.rect.move(-25, 0)



class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
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


class Chest:
    def __init__(self, coords, loot_name, loot_num=1):
        self.coords = coords
        self.loot_name = loot_name
        self.loot_num = loot_num


player_image = load_image('Player.png')
GameMap = GameMap(5, 7)
player, level_x, level_y = generate_level(load_level('map.txt'))


camera = Camera()
running = True
while running:
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            player.update(event)

    GameMap.render()
    all_sprites.draw(screen)
    player_group.draw(screen)

    pygame.display.flip()
