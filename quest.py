import os
import sys

import pygame
import requests

# Инициализируем pygame
pygame.init()
screen = pygame.display.set_mode((600, 450))
running = True
coor_1, coor_2 = 37.5308, 55.7031
spn_1, spn_2 = 0.2, 0.2
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                spn_1, spn_2 = spn_1 + 0.01, spn_2 + 0.01
            if event.button == 5:
                spn_1, spn_2 = spn_1 - 0.01, spn_2 - 0.01
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                coor_1 -= 0.01
            if event.key == pygame.K_RIGHT:
                coor_1 += 0.01
            if event.key == pygame.K_DOWN:
                coor_2 -= 0.01
            if event.key == pygame.K_UP:
                coor_2 += 0.01

    response = None
    try:
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={coor_1},{coor_2}&spn={spn_1},{spn_2}&l=map"
        response = requests.get(map_request)
    except:
        pass

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")

    # Запишем полученное изображение в файл.
    map_file = "map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)

    # Рисуем картинку, загружаемую из только что созданного файла.
    screen.blit(pygame.image.load(map_file), (0, 0))
    # Переключаем экран и ждем закрытия окна.
    pygame.display.flip()

    # coor_1, coor_2 = coor_1 + 0.01, coor_2 - 0.01
pygame.quit()

# Удаляем за собой файл с изображением.
os.remove(map_file)
