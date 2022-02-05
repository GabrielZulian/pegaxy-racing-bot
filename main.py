from random import random
from cv2 import cv2
from os import listdir
import numpy as np
import mss
import pyautogui
import time
import sys
import yaml

# load values from config.yaml
stream = open("configs.yaml", 'r')
configs = yaml.safe_load(stream)

th_values = configs['threshold']


def move_cursor(x, y, t):
    pyautogui.moveTo(x, y, t, pyautogui.easeInOutQuad)


def load_screenshots(dir_path='./screenshots/'):

    file_names = listdir(dir_path)
    targets = {}
    for file in file_names:
        path = 'screenshots/' + file
        targets[file.removesuffix('.png')] = cv2.imread(path)

    return targets


def already_race_menu():
    matches = locate_coordinates(images['racing_menu_on'])
    return len(matches[0]) > 0


def do_click(img, timeout=3, threshold=th_values['default']):

    start = time.time()
    has_timed_out = False
    while(not has_timed_out):
        matches = locate_coordinates(img, threshold)

        if(len(matches[0]) == 0):
            has_timed_out = time.time()-start > timeout
            continue

        x, y, w, h = matches[0][0]
        pos_x = x + w / 2
        pos_y = y + h / 2
        move_cursor(pos_x, pos_y, 1)
        pyautogui.click()
        return True

    return False


def locate_coordinates(img, threshold=th_values['default']):
    print = print_screen()
    result = cv2.matchTemplate(print, img, cv2.TM_CCOEFF_NORMED)
    w = img.shape[1]
    h = img.shape[0]

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles


def print_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))

        # Grab the data
        return sct_img[:, :, :3]


def main():

    global images
    images = load_screenshots()

    print('Iniciando bot')

    do_click(images['racing_menu'])

    do_click(images['pick_a_pega'])

    while True:
        do_click(images['start'])

        if (do_click['empty_energy']):
            print('Pegaxy sem energia, aguardando 1 hora...')

        print('Aguardando wallet...')
        do_click(images['sign'], 30)

        if (do_click(images['find_another'])):
            print('Falha ao iniciar corrida, procurar outra...')

        print('Próxima corrida...')
        do_click(images['next_match'], 120)

        time.sleep(3)

    # do_click(images['sign'])


if __name__ == '__main__':

    main()
