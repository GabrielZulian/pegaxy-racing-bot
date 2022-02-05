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


def show(rectangles, img=None):
    """ Show an popup with rectangles showing the rectangles[(x, y, w, h),...]
        over img or a printSreen if no img provided. Useful for debugging"""

    if img is None:
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            img = np.array(sct.grab(monitor))

    for (x, y, w, h) in rectangles[0]:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255, 255), 2)

    # cv2.rectangle(img, (result[0], result[1]), (result[0] + result[2], result[1] + result[3]), (255,50,255), 2)
    cv2.imshow('img', img)
    cv2.waitKey(0)


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

    horses = """
     _                     _                     _          
    |_) _   _   _.        |_)  _.  _ o ._   _   |_)  _ _|_  
    |  (/_ (_| (_| >< \/  | \ (_| (_ | | | (_|  |_) (_) |_  
            _|        /                     _|           

                /\                       /\                         
                \ \                     / /
              __/_/,,;;;`;       ;';;;,,\_\__        
           ,~(  )  , )~~\|       |/~~( ,  (  )~;
           ' / / --`--,             .--'-- \ \ `
            /  \    | '             ` |    /  \      
    """

    print(horses)
    print('Starting pegaxy racing bot...')
    print('Press CTRL + C to stop bot')
    print('\n')

    print('Acessing racing menu...')
    do_click(images['racing_menu'])

    print('Picking the pegaxy...')
    do_click(images['pick_a_pega'])
    time.sleep(2)

    while True:

        while True:
            print('Pressing start...')
            do_click(images['start'])

            if (do_click(images['empty_energy'], 0.7)):
                print('Pegaxy without energy, waiting 1 hour...')
                time.sleep(configs['wait_for_energy_recharge'])
                print('Refreshing page...')
                pyautogui.hotkey('ctrl', 'f5')
                time.sleep(5)
                break
            else:
                break

        while True:
            print('Waiting metamask sign...')
            do_click(images['sign'], 30)

            if (do_click(images['find_another'])):
                print('Fail to start race, searching for another...')
            else:
                print('Starting race...')
                break

        time.sleep(30)
        do_click(images['next_match'], 60)
        print('Next race...')

        time.sleep(3)


if __name__ == '__main__':

    main()
