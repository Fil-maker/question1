import os
import sys

import pygame
import requests

# Инициализируем pygame
pygame.init()
WIDTH, HEIGHT = 600, 450
screen = pygame.display.set_mode((WIDTH, HEIGHT))
running = True

coor_1, coor_2 = 65.582118, 57.18029
delta = 0.001220703125
type_val = {'Х': 'map', 'П': 'sat', 'И': 'sat,skl'}
current_type = 'Х'
place_marker = ''
show_post = False
full_address, post = '', ''
map_generated = False

button_sprites = pygame.sprite.Group()
inputbox_sprites = pygame.sprite.Group()
text_sprites = pygame.sprite.Group()

font = pygame.font.Font(None, 45)
font1 = pygame.font.Font(None, 32)
font2 = pygame.font.Font(None, 14)
color = pygame.color.Color(140, 140, 140)


class Button(pygame.sprite.Sprite):
    def __init__(self, group, x, y, width, height):
        super().__init__(group)
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.bgcolor = pygame.Color(64, 64, 64)
        self.bgimage = None
        self.hovered = False
        self.clicked = False
        self.rect = pygame.rect.Rect(x, y, width, height)
        self.text = ''
        self.font = pygame.font.FontType(None, -1)
        self.textcolor = (0, 0, 0, 0)

    def on_click(self, event):
        if self.x < event.pos[0] < self.x + self.width \
                and self.y < event.pos[1] < self.y + self.height:
            self.clicked = True

    def on_hover(self, event):  # По наведении курсора на кнопку
        self.hovered = False
        if self.x < event.pos[0] < self.x + self.width \
                and self.y < event.pos[1] < self.y + self.height:
            self.hovered = True

    def set_background_color(self, color: pygame.Color):
        self.bgcolor = color

    def set_text(self, text, font: pygame.font.Font, color: pygame.color.Color):
        self.text = text
        self.font = font
        self.textcolor = color

    def update(self, *args):
        self.clicked = False
        for arg in args:
            if arg.type == pygame.MOUSEBUTTONDOWN:
                self.on_click(arg)
            elif arg.type == pygame.MOUSEMOTION:
                self.on_hover(arg)
        self.render()

    def render(self):
        self.image = pygame.Surface([self.width, self.height], flags=pygame.SRCALPHA)
        if self.bgimage is not None:
            self.image.blit(self.bgimage, (0, 0))
        else:
            self.image.fill(self.bgcolor)
        if self.hovered:
            black = pygame.Surface((self.width, self.height), flags=pygame.SRCALPHA)
            black.fill(pygame.Color(*((16 + 16 * self.clicked,) * 3)))
            self.image.blit(black, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
        try:
            rendered = self.font.render(self.text, True, self.textcolor)
            w, h = rendered.get_size()
            self.image.blit(rendered, ((self.width - w) // 2, (self.height - h) // 2))
        except AttributeError:
            print('text not found')


class InputBox(pygame.sprite.Sprite):
    symbols = 'abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя1234567890_ ,.'

    def __init__(self, group, x, y, width, height, placeholder='',
                 font=pygame.font.Font(None, 14)):
        super().__init__(group)
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.placeholder = placeholder
        self.font = font
        self.bgcolor = pygame.color.Color(105, 105, 105)
        self.bgimage = None
        self.active = False
        self.enabled = True
        self.text = ''
        self.rect = pygame.rect.Rect(x, y, width, height)
        self.incorrect = False
        self.max_length = None

    def on_click(self, event):
        self.active = False
        if self.enabled and self.x < event.pos[0] < self.x + self.width \
                and self.y < event.pos[1] < self.y + self.height:
            self.active = True

    def set_placeholder_text(self, placeholder):
        self.placeholder = placeholder

    def set_enabled(self, enabled):
        self.enabled = enabled
        if not enabled:
            self.text = ''

    def set_incorrect(self, incorrect):
        self.incorrect = incorrect

    def set_max_length(self, length):
        self.max_length = length

    def set_background_color(self, color: pygame.Color):
        self.bgcolor = color

    def on_keydown(self, event):
        if event.key == pygame.K_RETURN:
            self.active = False
        elif event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.unicode.lower() in InputBox.symbols:
            if self.max_length is None or len(self.text) < self.max_length:
                self.text += event.unicode
                self.incorrect = False

    def update(self, *args):
        for arg in args:
            if arg.type == pygame.MOUSEBUTTONDOWN:
                self.on_click(arg)
            elif self.active and arg.type == pygame.KEYDOWN:
                self.on_keydown(arg)
        self.render()

    def render(self):
        self.image = pygame.Surface([self.width, self.height], flags=pygame.SRCALPHA)
        if self.bgimage is not None:
            self.image.blit(self.bgimage, (0, 0))
        else:
            self.image.fill(self.bgcolor)
            if not self.incorrect:
                pygame.draw.rect(self.image, pygame.color.Color(0xe7, 0xda, 0xae, 255),
                                 (0, 0, self.image.get_width(),
                                  self.image.get_height()), 1)
        if self.incorrect:
            pygame.draw.rect(self.image, pygame.color.Color(255, 0, 0, 255),
                             (0, 0, self.image.get_width(),
                              self.image.get_height()), 1)

        rendered = self.font.render(self.text if self.text else self.placeholder, True,
                                    pygame.color.Color(0xe7, 0xda, 0xae) if self.text
                                    else pygame.color.Color(128, 128, 128))
        w, h = rendered.get_size()
        self.image.blit(rendered, ((self.width - w) // 2, (self.height - h) // 2))

        if not self.enabled:
            black = pygame.Surface((self.width, self.height))
            black.fill(pygame.Color(0, 0, 0))
            black.set_alpha(150)
            self.image.blit(black, (0, 0))
        if self.active:
            pygame.draw.rect(self.image, pygame.color.Color(0xe7, 0xda, 0xae, 255),
                             (0, 0, self.image.get_width() - 1, self.image.get_height() - 1), 2)
        # self.surface.blit(self.image, (self.x, self.y))


class TextBox(pygame.sprite.Sprite):
    symbols = 'abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя1234567890_ ,.'

    def __init__(self, group, x, y, width, height, placeholder='',
                 font=pygame.font.Font(None, 14)):
        super().__init__(group)
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.placeholder = placeholder
        self.font = font
        self.bgcolor = pygame.color.Color(105, 105, 105)
        self.bgimage = None
        self.active = False
        self.enabled = True
        self.text = ''
        self.rect = pygame.rect.Rect(x, y, width, height)
        self.incorrect = False
        self.max_length = None

    def set_placeholder_text(self, placeholder):
        self.placeholder = placeholder

    def set_enabled(self, enabled):
        self.enabled = enabled
        if not enabled:
            self.text = ''

    def set_incorrect(self, incorrect):
        self.incorrect = incorrect

    def set_background_color(self, color: pygame.Color):
        self.bgcolor = color

    def update(self, *args):
        self.render()

    def render(self):
        self.image = pygame.Surface([self.width, self.height], flags=pygame.SRCALPHA)
        if self.bgimage is not None:
            self.image.blit(self.bgimage, (0, 0))
        else:
            self.image.fill(self.bgcolor)
            if not self.incorrect:
                pygame.draw.rect(self.image, pygame.color.Color(0xe7, 0xda, 0xae, 255),
                                 (0, 0, self.image.get_width(),
                                  self.image.get_height()), 1)
        if self.incorrect:
            pygame.draw.rect(self.image, pygame.color.Color(255, 0, 0, 255),
                             (0, 0, self.image.get_width(),
                              self.image.get_height()), 1)

        rendered = self.font.render(self.text if self.text else self.placeholder, True,
                                    pygame.color.Color(0xe7, 0xda, 0xae) if self.text
                                    else pygame.color.Color(128, 128, 128))
        w, h = rendered.get_size()
        self.image.blit(rendered, ((self.width - w) // 2, (self.height - h) // 2))

        if not self.enabled:
            black = pygame.Surface((self.width, self.height))
            black.fill(pygame.Color(0, 0, 0))
            black.set_alpha(150)
            self.image.blit(black, (0, 0))
        if self.active:
            pygame.draw.rect(self.image, pygame.color.Color(0xe7, 0xda, 0xae, 255),
                             (0, 0, self.image.get_width() - 1, self.image.get_height() - 1), 2)
        # self.surface.blit(self.image, (self.x, self.y))


swap_index = Button(button_sprites, WIDTH // 20, HEIGHT // 10 * 8.25, 3 * WIDTH // 20 + WIDTH // 40, HEIGHT // 20)
swap_index.set_text('НЕ показывает почту', font2, color)
swap_index.render()

address = TextBox(text_sprites, 4 * WIDTH // 20 + WIDTH // 20, HEIGHT // 10 * 8.25, 14 * WIDTH // 20, HEIGHT // 20,
                  'Полный адрес')
address.set_background_color(pygame.color.Color(27, 18, 12, 200))
address.render()

cancel = Button(button_sprites, WIDTH // 20, HEIGHT // 10 * 9, 3 * WIDTH // 20 + WIDTH // 40, HEIGHT // 20)
cancel.set_text('Сброс результата', font2, color)
cancel.render()

g_input = InputBox(inputbox_sprites, 4 * WIDTH // 20 + WIDTH // 20, HEIGHT // 10 * 9, 11 * WIDTH // 20, HEIGHT // 20,
                   'Адрес')
g_input.set_background_color(pygame.color.Color(27, 18, 12, 200))
g_input.set_max_length(40)
g_input.render()

confirm = Button(button_sprites, 16 * WIDTH // 20 + WIDTH // 40, HEIGHT // 10 * 9, WIDTH // 18, HEIGHT // 20)
confirm.set_text('O=', font1, color)
confirm.render()

change_view = Button(button_sprites, WIDTH // 10 * 9, HEIGHT // 10 * 9, WIDTH // 20, HEIGHT // 20)
change_view.set_text(current_type, font, color)
change_view.render()


def get_toponym_of_place(place):
    api_key = '40d1649f-0493-4b70-98ba-98533de7710b'
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey={api_key}&geocode={place}&format=json&kind=house"

    response = requests.get(geocoder_request)

    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        return toponym
    return False


def get_place_of_coordinates(c1, c2):
    api_key = '40d1649f-0493-4b70-98ba-98533de7710b'
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey={api_key}&geocode={c1},{c2}&lang=ru_RU&spn={delta},{delta}&format=json"

    response = requests.get(geocoder_request)

    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        return toponym
    return False


def load_image():
    map_request = f'''http://static-maps.yandex.ru/1.x/?bbox={coor_1 - delta},{coor_2 - delta}~{coor_1 + delta},{coor_2 + delta}&l={
    type_val[current_type]}{place_marker}'''
    response = requests.get(map_request)
    if not response:
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        raise Exception
    with open("map.png", "wb") as file:
        file.write(response.content)


def get_organization_of_text(text, add):
    api_key = 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3'
    geocoder_request = f"https://search-maps.yandex.ru/v1/?apikey={api_key}&text={add}&lang=ru_RU&ll={text}&spn={0.0075},{0.0075}&rspn=1&type=biz"
    print(geocoder_request)
    response = requests.get(geocoder_request)
    if response:
        return response.json()
    return False


while running:
    map_generated = False
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_LEFT:
                try:
                    coor_1 -= delta
                    load_image()
                    map_generated = True
                except Exception as e:
                    coor_1 += delta
            elif event.key == pygame.K_RIGHT:
                try:
                    coor_1 += delta
                    load_image()
                    map_generated = True
                except Exception as e:
                    coor_1 -= delta
            elif event.key == pygame.K_DOWN:
                try:
                    coor_2 -= delta
                    load_image()
                    map_generated = True
                except Exception as e:
                    coor_2 += delta
            elif event.key == pygame.K_UP:
                try:
                    coor_2 += delta
                    load_image()
                    map_generated = True
                except Exception as e:
                    coor_2 -= delta

            if event.key == pygame.K_PAGEUP:
                if coor_2 + delta * 2 < 80 and abs(coor_1 + delta * 2) < 180:
                    delta *= 2
                print(delta)

            elif event.key == pygame.K_PAGEDOWN:
                if delta / 2 >= 0.0003:
                    delta /= 2
                print(delta)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and event.pos[1] < HEIGHT // 10 * 8.25:
                x, y = event.pos
                y = HEIGHT - y
                width_per, height_per = x / WIDTH, y / HEIGHT
                coor_1, coor_2 = (coor_1 + delta - (coor_1 - delta)) * width_per + coor_1 - delta, (
                        coor_2 + delta - (coor_2 - delta)) * height_per + coor_2 - delta
                toponym = get_place_of_coordinates(coor_1, coor_2)
                place_marker = f'&pt={coor_1},{coor_2}'
                try:
                    full_address = toponym['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
                    post = toponym['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
                except Exception as e:
                    print(e)

            if event.button == 3:
                x, y = event.pos
                y = HEIGHT - y
                width_per, height_per = x / WIDTH, y / HEIGHT
                coor_1_x, coor_2_x = (coor_1 + delta - (coor_1 - delta)) * width_per + coor_1 - delta, (
                        coor_2 + delta - (coor_2 - delta)) * height_per + coor_2 - delta

                toponym = get_place_of_coordinates(coor_1_x, coor_2_x)
                orgs = get_organization_of_text(f'{coor_1_x},{coor_2_x}',
                                                toponym['metaDataProperty']['GeocoderMetaData']['Address']['formatted'])
                if orgs['features'][0]['properties']['name']:
                    place_marker = f"&pt={str(orgs['features'][0]['geometry']['coordinates'][0])},{str(orgs['features'][0]['geometry']['coordinates'][1])}"
                    full_address, post = orgs['features'][0]['properties']['name'], ''
                    address.text = ''

        if change_view.clicked:
            if current_type == 'Х':
                current_type = 'П'
                change_view.set_text(current_type, font, color)
            elif current_type == 'П':
                current_type = 'И'
                change_view.set_text(current_type, font, color)
            elif current_type == 'И':
                current_type = 'Х'
                change_view.set_text(current_type, font, color)

        if confirm.clicked:
            toponym = get_toponym_of_place(g_input.text)
            if toponym:
                coor_1, coor_2 = map(lambda x: float(x), toponym['Point']['pos'].split())
                coor_1_2, coor_2_2 = map(lambda x: float(x),
                                         toponym['boundedBy']['Envelope']['lowerCorner'].split())
                delta = min(coor_1 - coor_1_2, coor_2 - coor_2_2)
                place_marker = f'&pt={coor_1},{coor_2}'
                try:
                    full_address = toponym['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
                    post = toponym['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
                except Exception as e:
                    print(e)

        if cancel.clicked:
            place_marker = ''
            full_address, post = '', ''
            address.text = ''

        if swap_index.clicked:
            if show_post:
                show_post = False
                swap_index.text = 'НЕ показывает почту'
            else:
                show_post = True
                swap_index.text = 'Показывает почту'

        if show_post:
            if full_address:
                address.text = f'{full_address}, {post}'
        else:
            #
            address.text = full_address

        button_sprites.update(event)
        inputbox_sprites.update(event)
        text_sprites.update(event)
    try:
        load_image()
        screen.blit(pygame.image.load("map.png"), (0, 0))
    except Exception as e:
        print(e)

    button_sprites.draw(screen)
    inputbox_sprites.draw(screen)
    text_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
os.remove("map.png")
sys.exit(0)
