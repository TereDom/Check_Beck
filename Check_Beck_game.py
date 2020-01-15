import pygame
import os
import random
import sys


pygame.init()

bullet_group = pygame.sprite.Group()
creatures_group = pygame.sprite.Group()
weapons_group = pygame.sprite.Group()
chest_group = pygame.sprite.Group()
inventory_sprites = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
dark_zones = dict()
dark_group = pygame.sprite.Group()
monsters_group = pygame.sprite.Group()

LIST_OF_MONSTERS = ['Bat', 'Dragon', 'SkeletonBomber', 'Frankenstein']

size = width, height = 850, 500
tile_width = tile_height = 50
HEALTH_BAR_SIZE = 178
chests_found = 0
HP = 50

screen = pygame.display.set_mode(size)
amount_sprites = 47996


def show_progress(setMax, setVal):
    # Всего процентов
    precent_max = setMax
    # Текущее количество процентов
    precent_cur = int(setVal / setMax * 100)
    # Это 100% прогресс бара
    length_pb = 60
    # Вычислить текущее значение прогресса
    length_cur = int(length_pb / 100 * precent_cur)
    # Выводим прогресс бар
    sys.stderr.write(
        '\rLoading: [' + '#' * length_cur + '.' * (length_pb - length_cur) + '] ' + str(precent_cur) + '%')

    # screen.fill(pygame.color.Color('black'))
    # width_pb = 500
    # height_pb = 50
    # pygame.draw.rect(screen, pygame.color.Color('white'), ((width - width_pb) // 2, (height - height_pb) // 2,
    #                                                        width_pb, height_pb), 2)
    # pygame.draw.rect(screen, pygame.color.Color("white"), ((width - width_pb) // 2, (height - height_pb) // 2,
    #                                                        int(width_pb / 100 * precent_cur), height_pb), 0)
    # pygame.display.flip()


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

    load_val = 0

    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '!':
                Tile("empty", x, y)
                chests[(y, x)] = Chest((x, y))
                monsters[(x - 1, y - 1)] = random_monster('Bat',
                                                          (x - 1, y - 1), (x, y))
            elif level[y][x] == '@':
                Tile('empty', x, y)
                player_coords = x, y

            elif level[y][x] == '*':
                Tile('door', x, y)
            load_val += 1
            show_progress(amount_sprites, load_val)

    # p_x, p_y = player_coords
    # p_x, p_y = p_x * 2, p_y * 2
    # for y in range(len(level) * 2):
    #    for x in range(len(level[0]) * 2):
    #        if (x, y) not in [(p_x, p_y - 1), (p_x, p_y - 2), (p_x, p_y + 2), (p_x, p_y + 3),
    #                          (p_x + 1, p_y - 1), (p_x + 1, p_y - 2), (p_x + 1, p_y + 2), (p_x + 1, p_y + 3),
    #                          (p_x - 2, p_y), (p_x - 1, p_y), (p_x + 2, p_y), (p_x + 3, p_y),
    #                          (p_x - 2, p_y + 1), (p_x - 1, p_y + 1), (p_x + 2, p_y + 1), (p_x + 3, p_y + 1),
    #                          (p_x - 1, p_y - 1), (p_x - 1, p_y + 2), (p_x + 2, p_y - 1), (p_x + 2, p_y + 2),
    #                          (p_x, p_y), (p_x + 1, p_y), (p_x, p_y + 1), (p_x + 1, p_y + 1)]:
    #            dark_zones[(x, y)] = Tile('dark', x, y)
    #            load_val += 1
    #            show_progress(amount_sprites, load_val)

    gun = FirstWeapon()
    knife = SecondWeapon()
    new_player = Player(*player_coords)

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
        self.minimap_coords = self.x + ((self.width - 194) // 2), height * 0.6

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
        size_of_map = 194
        pygame.draw.rect(screen, (255, 255, 255), (self.x + ((self.width - int(self.width * 0.88)) // 2),
                                                   height * 0.13, int(self.width * 0.88), height * 0.13), 1)

        pygame.draw.rect(screen, (255, 255, 255) if player.active_weapon == 2 else (225, 204, 79),
                         (self.x + ((self.width - int(self.width * 0.88)) // 2) +
                          (int(self.width * 0.88) - size_of_slots * 2) // 4 - 1, height * 0.14 - 1,
                          size_of_slots + 2, size_of_slots + 2), 1)

        pygame.draw.rect(screen, (255, 255, 255) if player.active_weapon == 1 else (225, 204, 79),
                         (self.x + ((self.width - int(self.width * 0.88)) // 2) +
                          int(self.width * 0.88) - (int(self.width * 0.88) - size_of_slots * 2) // 4
                          - size_of_slots - 1, height * 0.14 - 1, size_of_slots + 2, size_of_slots + 2), 1)

        pygame.draw.rect(screen, (255, 255, 255), (self.x + ((self.width - int(self.width * 0.88)) // 2) - 1,
                                                   height * 0.31 - 1, size_of_slots + 2, size_of_slots + 2), 1)

        pygame.draw.rect(screen, (255, 255, 255), (self.x + ((self.width - int(self.width * 0.88)) // 2)
                                                   + int(self.width * 0.88) - size_of_slots - 1, height * 0.31 - 1,
                                                   size_of_slots + 2, size_of_slots + 2), 1)

        pygame.draw.rect(screen, (255, 255, 255), (self.x + ((self.width - int(self.width * 0.88)) // 2),
                                                   height * 0.48, size_of_slots, size_of_slots), 1)

        pygame.draw.rect(screen, (255, 255, 255), (self.x + ((self.width - int(self.width * 0.88)) // 2)
                                                   + int(self.width * 0.88) - size_of_slots,
                                                   height * 0.48, size_of_slots, size_of_slots), 1)

        pygame.draw.rect(screen, (255, 255, 255), (self.x + ((self.width - size_of_map) // 2),
                                                   height * 0.6, size_of_map, size_of_map), 1)

    def get_minimap_coords(self):
        return self.minimap_coords

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
        tile_images = {'wall': load_image('wall.png'), 'dark': load_image('dark.png'),
                       'empty': load_image('floor.png'), 'door': load_image('door.png')}
        super().__init__((all_sprites, tiles_group) if tile_type != 'dark' else dark_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move((tile_width if tile_type != 'dark' else tile_width / 2) * pos_x,
                                               (tile_height if tile_type != 'dark' else tile_height / 2) * pos_y)


class GameMap:
    def __init__(self, width, height, map):
        self.width = width
        self.height = height
        self.board = list(load_level('map.txt'))
        self.left = 0
        self.top = 0
        self.cell_size = 0
        self.map = [list(i) for i in map]

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self):
        pass


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, creatures_group)
        self.image = player_image
        self.active_weapon = 1
        self.inventory = {'Ammo': 15, 'Potion': 0, 'Key': 0}
        self.x, self.y = pos_x, pos_y
        self.image = load_image('Player_down.png')
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.hp = HP
        self.direction = 'down'
        self.coords = (self.x, self.y)

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
        x, y = self.x * 2, self.y * 2
        for i in [(x, y - 1), (x, y - 2), (x, y + 2), (x, y + 3),
                  (x + 1, y - 1), (x + 1, y - 2), (x + 1, y + 2), (x + 1, y + 3),
                  (x - 2, y), (x - 1, y), (x + 2, y), (x + 3, y),
                  (x - 2, y + 1), (x - 1, y + 1), (x + 2, y + 1), (x + 3, y + 1),
                  (x - 1, y - 1), (x - 1, y + 2), (x + 2, y - 1), (x + 2, y + 2),
                  (x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]:
            if i in dark_zones.keys():
                dark_zones[i].kill()
                del dark_zones[i]

        minimap.update_player_coords(int(self.x), int(self.y))
        minimap.draw()

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

    def hit(self):
        if self.active_weapon == 1:
            if player.inventory['Ammo']:
                pygame.mixer.music.load("data/shot.mp3")
                pygame.mixer.music.play(1)
                player.inventory['Ammo'] -= 1
                bul = Bullet(player)
            elif not player.inventory['Ammo']:
                pygame.mixer.music.load("data/noAmmo_shot.mp3")
                pygame.mixer.music.play(1)
        elif self.active_weapon == 2:
            pygame.mixer.music.load("data/hit.mp3")
            pygame.mixer.music.play(1)

    def heal(self):
        if player.inventory['Potion'] and self.hp < HP:
            pygame.mixer.music.load('data/heal.mp3')
            pygame.mixer.music.play(1)
            player.hp = HP if self.hp + 10 > HP else self.hp + 10
            player.inventory['Potion'] -= 1


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
        super().__init__(all_sprites, monsters_group, creatures_group)
        self.image = load_image('bat_down.png')
        self.CHEST_COORDS = chest_coords
        self.DAMAGE = 5
        self.hp = 20
        self.coords = coords
        self.x, self.y = self.coords
        self.rect = self.image.get_rect().move(tile_width * coords[0], tile_height * coords[1])
        self.direction = ('down', 0, 1)
        self.rage = (False, 'None')
        self.i = 0
        self.way = [self.CHEST_COORDS]

    def update(self, direction):
        if not self.rage[0]:
            self.move()
            self.i += 1
            if self.i == 4:
                self.direction = self.change_direction(self.direction)
                self.i = 0
            if self.hp < 20:
                self.rage = (True, 'hit')
            elif gamemap.map[self.CHEST_COORDS[1]][self.CHEST_COORDS[0]] == '?':
                self.rage = (True, 'open_chest')
        if self.rage[0]:
            if self.way:
                if self.way[-1] != (player.x, player.y):
                    if len(self.way) >= 2 and self.way[-2] == (player.x, player.y):
                        del self.way[-1]
                        del self.way[-1]
                    else:
                        self.way.append((player.x, player.y))

                self.direction = self.change_direction(self.direction)
                if self.coords != self.way[0]:
                    self.move()
                else:
                    del self.way[0]
            else:
                self.way.append((player.x, player.y))

    def change_direction(self, old_dir):
        possible_dir = [('down', 0, 1), ('right', 1, 0), ('up', 0, -1), ('left', -1, 0)]
        if not self.rage[0]:
            new_dir = possible_dir.index(old_dir) + 1
            new_dir = possible_dir[new_dir if new_dir != len(possible_dir) else 0]
            return new_dir
        elif self.rage[0]:
            y_changed = self.way[0][1] - self.y
            x_changed = self.way[0][0] - self.x
            if y_changed != 0:
                if y_changed > 0:
                    return possible_dir[0]
                elif y_changed < 0:
                    return possible_dir[2]
            elif x_changed != 0:
                if x_changed > 0:
                    return possible_dir[1]
                elif x_changed < 0:
                    return possible_dir[3]

    def move(self):
        del monsters[self.coords]
        self.rect = self.rect.move(self.direction[1] * 25, self.direction[2] * 25)
        self.x += self.direction[1] * 0.5
        self.y += self.direction[2] * 0.5
        self.coords = self.x, self.y
        self.image = load_image('bat_' + self.direction[0] + '.png')
        monsters[self.coords] = self

    def damage(self, type):
        if type == 'bullet':
            self.hp -= 5
        elif type == 'knife':
            self.hp -= 10
        if self.hp <= 0:
            del monsters[self.coords]
            self.kill()
        pygame.mixer.music.load('data/damage.mp3')
        pygame.mixer.music.play(1)


class Dragon(pygame.sprite.Sprite):
    def __init__(self, coords, chest_coords):
        super().__init__(all_sprites, monsters_group, creatures_group)
        self.image = load_image('dragon_down.png')
        self.CHEST_COORDS = chest_coords
        self.DAMAGE = 10
        self.hp = 40
        self.coords = coords
        self.x, self.y = coords
        self.x, self.y = self.coords
        self.rect = self.image.get_rect().move(tile_width * coords[0], tile_height * coords[1])
        self.direction = ('down', 0, 1)
        self.rage = (False, 'None')
        self.i = 0
        self.way = [self.CHEST_COORDS]

    def update(self, direction):
        if not self.rage[0]:
            self.move()
            self.i += 1
            if self.i == 4:
                self.direction = self.change_direction(self.direction)
                self.i = 0
            if self.hp < 40:
                self.rage = (True, 'hit')
            elif gamemap.map[self.CHEST_COORDS[1]][self.CHEST_COORDS[0]] == '?':
                self.rage = (True, 'open_chest')
        if self.rage[0]:
            if self.way:
                if self.way[-1] != (player.x, player.y):
                    self.way.append((player.x, player.y))
                self.direction = self.change_direction(self.direction)
                if self.coords != self.way[0]:
                    self.move()
                else:
                    del self.way[0]
            else:
                self.way.append((player.x, player.y))

    def change_direction(self, old_dir):
        possible_dir = [('down', 0, 1), ('right', 1, 0), ('up', 0, -1), ('left', -1, 0)]
        if not self.rage[0]:
            new_dir = possible_dir.index(old_dir) + 1
            new_dir = possible_dir[new_dir if new_dir != len(possible_dir) else 0]
            return new_dir
        elif self.rage[0]:
            y_changed = self.way[0][1] - self.y
            x_changed = self.way[0][0] - self.x
            if y_changed != 0:
                if y_changed > 0:
                    return possible_dir[0]
                elif y_changed < 0:
                    return possible_dir[2]
            elif x_changed != 0:
                if x_changed > 0:
                    return possible_dir[1]
                elif x_changed < 0:
                    return possible_dir[3]

    def move(self):
        del monsters[self.coords]
        self.rect = self.rect.move(self.direction[1] * 25, self.direction[2] * 25)
        self.x += self.direction[1] * 0.5
        self.y += self.direction[2] * 0.5
        self.coords = self.x, self.y
        self.image = load_image('dragon_' + self.direction[0] + '.png')
        monsters[self.coords] = self

    def damage(self, type):
        if type == 'bullet':
            self.hp -= 5
        elif type == 'knife':
            self.hp -= 10
        if self.hp <= 0:
            del monsters[self.coords]
            self.kill()
        pygame.mixer.music.load('data/damage.mp3')
        pygame.mixer.music.play(1)


class SkeletonBomber(pygame.sprite.Sprite):
    def __init__(self, coords, chest_coords):
        super().__init__(all_sprites, monsters_group, creatures_group)
        self.image = load_image('skeleton_down.png')
        self.CHEST_COORDS = chest_coords
        self.DAMAGE = 25
        self.hp = 10
        self.coords = coords
        self.x, self.y = self.coords
        self.rect = self.image.get_rect().move(tile_width * coords[0], tile_height * coords[1])
        self.direction = ('down', 0, 1)
        self.rage = (False, 'None')
        self.i = 0
        self.way = [self.CHEST_COORDS]

    def update(self, direction):
        if not self.rage[0]:
            self.move()
            self.i += 1
            if self.i == 2:
                self.direction = self.change_direction(self.direction)
                self.i = 0
            if self.hp < 10:
                self.rage = (True, 'hit')
            elif gamemap.map[self.CHEST_COORDS[1]][self.CHEST_COORDS[0]] == '?':
                self.rage = (True, 'open_chest')
        if self.rage[0]:
            if self.way:
                if self.way[-1] != (player.x, player.y):
                    self.way.append((int(player.x), int(player.y)))
                self.direction = self.change_direction(self.direction)
                if self.coords != self.way[0]:
                    self.move()
                else:
                    del self.way[0]
            else:
                self.way.append((int(player.x), int(player.y)))

    def change_direction(self, old_dir):
        possible_dir = [('down', 0, 1), ('right', 1, 0), ('up', 0, -1), ('left', -1, 0)]
        if not self.rage[0]:
            new_dir = possible_dir.index(old_dir) + 1
            new_dir = possible_dir[new_dir if new_dir != len(possible_dir) else 0]
            return new_dir
        elif self.rage[0]:
            y_changed = self.way[0][1] - self.y
            x_changed = self.way[0][0] - self.x
            if y_changed != 0:
                if y_changed > 0:
                    return possible_dir[0]
                elif y_changed < 0:
                    return possible_dir[2]
            elif x_changed != 0:
                if x_changed > 0:
                    return possible_dir[1]
                elif x_changed < 0:
                    return possible_dir[3]

    def move(self):
        del monsters[self.coords]
        self.rect = self.rect.move(self.direction[1] * 50, self.direction[2] * 50)
        self.x += self.direction[1]
        self.y += self.direction[2]
        self.coords = self.x, self.y
        self.image = load_image('skeleton_' + self.direction[0] + '.png')
        monsters[self.coords] = self

    def damage(self, type):
        if type == 'bullet':
            self.hp -= 5
        elif type == 'knife':
            self.hp -= 10
        if self.hp <= 0:
            del monsters[self.coords]
            self.kill()
        pygame.mixer.music.load('data/damage.mp3')
        pygame.mixer.music.play(1)


class Frankenstein(pygame.sprite.Sprite):
    def __init__(self, coords, chest_coords):
        super().__init__(all_sprites, monsters_group, creatures_group)
        self.image = load_image('frankenstein_down.png')
        self.CHEST_COORDS = chest_coords
        self.hp = 75
        self.DAMAGE = 15
        self.coords = coords
        self.x, self.y = self.coords
        self.rect = self.image.get_rect().move(tile_width * coords[0], tile_height * coords[1])
        self.direction = ('down', 0, 1)
        self.rage = (False, 'None')
        self.i = 0
        self.way = [self.CHEST_COORDS]

    def update(self, direction):
        if not self.rage[0]:
            self.move()
            self.i += 1
            if self.i == 4:
                self.direction = self.change_direction(self.direction)
                self.i = 0
            if self.hp < 75:
                self.rage = (True, 'hit')
            elif gamemap.map[self.CHEST_COORDS[1]][self.CHEST_COORDS[0]] == '?':
                self.rage = (True, 'open_chest')
        if self.rage[1] == 'hit':
            if self.way:
                if self.way[-1] != (player.x, player.y):
                    self.way.append((player.x, player.y))
                self.direction = self.change_direction(self.direction)
                if self.coords != self.way[0]:
                    self.move()
                else:
                    del self.way[0]
            else:
                self.way.append((player.x, player.y))

    def change_direction(self, old_dir):
        possible_dir = [('down', 0, 1), ('right', 1, 0), ('up', 0, -1), ('left', -1, 0)]
        if not self.rage[0]:
            new_dir = possible_dir.index(old_dir) + 1
            new_dir = possible_dir[new_dir if new_dir != len(possible_dir) else 0]
            return new_dir
        elif self.rage[0]:
            y_changed = self.way[0][1] - self.y
            x_changed = self.way[0][0] - self.x
            if y_changed != 0:
                if y_changed > 0:
                    return possible_dir[0]
                elif y_changed < 0:
                    return possible_dir[2]
            elif x_changed != 0:
                if x_changed > 0:
                    return possible_dir[1]
                elif x_changed < 0:
                    return possible_dir[3]

    def move(self):
        del monsters[self.coords]
        self.rect = self.rect.move(self.direction[1] * 25, self.direction[2] * 25)
        self.x += self.direction[1] * 0.5
        self.y += self.direction[2] * 0.5
        self.coords = self.x, self.y
        self.image = load_image('frankenstein_' + self.direction[0] + '.png')
        monsters[self.coords] = self

    def damage(self, type):
        if type == 'bullet':
            self.hp -= 5
        elif type == 'knife':
            self.hp -= 10
        if self.hp <= 0:
            del monsters[self.coords]
            self.kill()
        pygame.mixer.music.load('data/damage.mp3')
        pygame.mixer.music.play(1)


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


class Bullet(pygame.sprite.Sprite):
    def __init__(self, master):
        super().__init__(bullet_group, all_sprites)
        self.image = load_image('Bullet.png')
        self.direction = master.direction
        self.coords = master.x, master.y
        self.x, self.y = self.coords
        self.rect = master.rect
        self.dir = {'down': [0, 1], 'right': [1, 0], 'up': [0, -1], 'left': [-1, 0]}

    def update(self):
        x = int(self.x)
        y = int(self.y)

        if (self.direction == 'up' and gamemap.map[y + (1 if self.y % 1 != 0 else 0) - 1][x] != '#' and
                gamemap.map[y + (1 if self.y % 1 != 0 else 0) - 1][x + (1 if self.x % 1 != 0 else 0)] != '#'):
            self.rect = self.rect.move(0, -25)
            self.y -= 0.5
            self.coords = (x, y)
        elif (self.direction == 'down' and gamemap.map[y + 1][x] != "#" and
              gamemap.map[y + 1][x + (1 if self.x % 1 != 0 else 0)] != '#'):
            self.rect = self.rect.move(0, 25)
            self.y += 0.5
            self.coords = (x, y)
        elif (self.direction == 'right' and gamemap.map[y][x + 1] != '#' and
              gamemap.map[y + (1 if self.y % 1 != 0 else 0)][x + 1] != '#'):
            self.rect = self.rect.move(25, 0)
            self.x += 0.5
            self.coords = (x, y)
        elif (self.direction == 'left' and gamemap.map[y][x + (1 if self.x % 1 != 0 else 0) - 1] != '#' and
              gamemap.map[y + (1 if self.y % 1 != 0 else 0)][x + (1 if self.x % 1 != 0 else 0) - 1] != '#'):
            self.rect = self.rect.move(-25, 0)
            self.x -= 0.5
            self.coords = (x, y)
        else:
            self.kill()
        lst = list(monsters.values())
        for monster in lst:
            if not (not (self.coords == monster.coords) and not (
                    (self.coords[0], self.coords[1] - 0.5) == monster.coords) and not (
                    (self.coords[0], self.coords[1] + 0.5) == monster.coords) and not (
                    (self.coords[0] + 0.5, self.coords[1]) == monster.coords) and not (
                    (self.coords[0] - 0.5, self.coords[1]) == monster.coords)):
                monster.damage('bullet')
                self.kill()



class MiniMap:
    def __init__(self, w, h, coords, cell_size, player_coords):
        self.map = [[None for _ in range(w)] for _ in range(h)]
        self.x, self.y = coords
        self.cell_size = cell_size
        self.p_x, self.p_y = player_coords
        self.map[97][95] = 0

    def open_cell(self, x, y):
        self.map[y][x] = 1

    def update_player_coords(self, x, y):
        self.map[self.p_y][self.p_x] = 1
        self.map[y][x] = -1
        self.p_x, self.p_y = x, y

    def draw(self):
        for y in range(len(self.map)):
            for x in range(len(self.map[0])):
                if self.map[y][x] == -1:
                    pygame.draw.rect(
                        screen, pygame.color.Color('yellow'), (self.x + x * self.cell_size,
                                                               self.y + y * self.cell_size,
                                                               self.cell_size, self.cell_size), 0)
                elif self.map[y][x] == 0:
                    pygame.draw.rect(
                        screen, pygame.color.Color('blue'), (self.x + x * self.cell_size,
                                                             self.y + y * self.cell_size,
                                                             self.cell_size, self.cell_size), 0)
                elif self.map[y][x] is not None:
                    pygame.draw.rect(
                        screen, pygame.color.Color('red'), (self.x + x * self.cell_size,
                                                            self.y + y * self.cell_size,
                                                            self.cell_size, self.cell_size), 0)
                else:
                    pygame.draw.rect(
                        screen, pygame.color.Color('black'), (self.x + x * self.cell_size,
                                                            self.y + y * self.cell_size,
                                                            self.cell_size, self.cell_size), 0)



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
        if self.loot_name == 'Ammo':
            pygame.mixer.music.load("data/ammo_picked.mp3")
        elif self.loot_name == "Key":
            pygame.mixer.music.load('data/key_picked.mp3')
        else:
            pygame.mixer.music.load("data/potion_picked.mp3")
        self.image = load_image('open_chest.png')
        pygame.mixer.music.play(1)
        chests_found += 1


player_image = load_image('Player_down.png')
gamemap, player, level_x, level_y, chests, gun, knife, monsters = generate_level(load_level('map.txt'))

minimap = MiniMap(len(gamemap.map), len(gamemap.map[0]), inventory.get_minimap_coords(), 2, (player.x, player.y))

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
bul_clock = pygame.time.Clock()
bul_timer = 0
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
        if event.type == pygame.JOYAXISMOTION:
            set_direction_rs(player, stick)
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button in [7, 6]:
                running = False
            if event.button == 0 and gamemap.map[int(player.y)][int(player.x)] == '!':
                chest = chests[(int(player.y), int(player.x))]
                chest.open_chest()
                player.inventory[chest.loot_name.type] += chest.loot_num
                gamemap.map[int(player.y)][int(player.x)] = '?'
                del chests[(int(player.y), int(player.x))]
            if event.button == 2:
                player.hit()
            if event.button == 1:
                player.heal()
        if event.type == pygame.KEYDOWN:
            if gamemap.map[int(player.y)][int(player.x)] == '!' and event.key == pygame.K_e:
                chest = chests[(int(player.y), int(player.x))]
                chest.open_chest()
                player.inventory[chest.loot_name.type] += chest.loot_num
                gamemap.map[int(player.y)][int(player.x)] = '?'
                del chest
            if event.key == pygame.K_2:
                player.active_weapon = 2
            if event.key == pygame.K_1:
                player.active_weapon = 1
            if event.key == pygame.K_3:
                player.heal()
            if event.key == pygame.K_SPACE:
                player.hit()
            if event.key == pygame.K_ESCAPE:
                running = False

        if (event.type == pygame.KEYUP or event.type == pygame.KEYDOWN) and \
                event.key in [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]:
            direction, move = set_direction_wasd(event)

    if stick is not None and flag:
        direction, move = set_direction_ls(stick)

    player_timer += player_clock.tick()
    monster_timer += monster_clock.tick()
    bul_timer += bul_clock.tick()

    if monster_timer >= 150:
        for monster in monsters_group:
            monster.update(monster.direction)
        monster_timer = 0

    if move and player_timer >= 150:
        if player.direction != direction:
            player.update_direction(direction)
        else:
            player.update(direction)
        player_timer = 0

    if bul_timer >= 30:
        for sprite in bullet_group:
            sprite.update()
        bul_timer = 0

    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    for sprite in dark_group:
        camera.apply(sprite)

    gamemap.render()
    all_sprites.draw(screen)
    monsters_group.draw(screen)
    dark_group.draw(screen)

    inventory.upgrade()
    minimap.draw()
    pygame.display.flip()

if stick is not None:
    stick.quit()
pygame.quit()
