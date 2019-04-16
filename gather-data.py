import pyautogui
import numpy as np
from PIL import Image
from time import sleep
from glob import glob
import cv2
import uuid
import os

def find_origin_coordinates():
    im = pyautogui.screenshot()
    im2 = Image.open('anchors/endless.png')
    result = cv2.matchTemplate(np.array(im2), np.array(im), cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val < 0.999:
        raise Exception('no endless found')
    return max_loc

def click(x, y):
    global offset
    pyautogui.moveTo(offset[0]+x, offset[1]+y)
    pyautogui.click()

def start_game():
    click(625, 600)
    sleep(2)
    click(343, 201)
    click(543, 461)
    click(637, 631)
    sleep(9)

def look_for_wanted_criminals():
    im = pyautogui.screenshot(region=(offset[0]+670, offset[1]+276, 120, 60))
    im2 = Image.open('anchors/bulletin.png')
    if not (np.array(im) == np.array(im2)).all():
        raise Exception()
    pyautogui.move(1,1)
    pyautogui.press('right')
    wanted_criminals = pyautogui.screenshot(region=(offset[0]+64, offset[1]+50, 1140, 640))
    pyautogui.press('left')
    return wanted_criminals

def call_next():
    click(415, 200)
    sleep(7)

def received_docs():
    return pyautogui.screenshot(region=(offset[0]+67, offset[1]+479, 417-67, 599-479))

def moveTo(x, y):
    global offset
    pyautogui.moveTo(offset[0]+x, offset[1]+y)

def dragTo(x, y, button='left', duration=0.4):
    global offset
    pyautogui.dragTo(offset[0]+x, offset[1]+y, button=button, duration=duration)

def open_doc(counter):
    moveTo(243 + ((-1) ** (counter % 2)) * (counter // 2) * 20, 547)
    dragTo(815, 468)

def screenshot(x1, y1, x2, y2):
    global offset
    return pyautogui.screenshot(region=(offset[0]+x1, offset[1]+y1, x2 - x1, y2 - y1))

def receive_all_documents():
    im = received_docs()
    im2 = Image.open('anchors/nodocs.png')
    counter = 0
    total = 0
    documents_screenshots = []
    while not (np.array(im) == np.array(im2)).all():
        if total == 12:
            raise Exception('Cannot receive all documents')
        open_doc(counter)
        documents_screenshots.append(screenshot(430, 265, 1204, 682))
        new_im = received_docs()
        if (np.array(im) == np.array(new_im)).all():
            counter += 1
            total += 1
        else:
            counter = 0
            im = new_im
    return documents_screenshots

def put_document_away():
    moveTo(815, 468)
    dragTo(198, 547) # needs to overshoot because it is dropped early

def find_entry_visa():
    im = pyautogui.screenshot()
    im2 = Image.open('anchors/entry_visa.png')
    result = cv2.matchTemplate(np.array(im2), np.array(im), cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val > 0.999:
        return max_loc[0] - offset[0], max_loc[1] - offset[1]
    return None

def return_documents():
    counter = 0
    im = screenshot(815, 468, 855, 508)
    im2 = Image.open('anchors/nodoc_right.png')
    while not (np.array(im) == np.array(im2)).all():
        if counter > 10:
            raise Exception()
        counter += 1
        moveTo(815, 468)
        dragTo(221, 391)
        im = screenshot(815, 468, 855, 508)

    im = received_docs()
    im2 = Image.open('anchors/nodocs.png')
    counter = 1
    while not (np.array(im) == np.array(im2)).all():
        if counter > 10:
            raise Exception()
        moveTo(243 + ((-1) ** (counter % 2)) * (counter // 2) * 20, 547)
        dragTo(221, 391)
        new_im = received_docs()
        if (np.array(im) == np.array(new_im)).all():
            counter += 1
        else:
            counter = 0
            im = new_im

def accept():
    counter = 0
    im2 = Image.open('anchors/nodoc_right.png')
    while True:
        counter += 1
        if counter == 10:
            raise Exception('failed to find entry visa')
        im = screenshot(815, 468, 855, 508)
        if (np.array(im) == np.array(im2)).all():
            return False

        entry_visa = find_entry_visa()
        if entry_visa is None:
            put_document_away()
            continue
        moveTo(*entry_visa)
        dragTo(1038, 395)
        pyautogui.press('tab')
        sleep(0.5)
        click(1038, 395)
        moveTo(1038, 455)
        pyautogui.press('tab')
        moveTo(1038, 475)
        dragTo(221, 391)
        return_documents()
        return True

def get_person_face():
    return screenshot(823-757, 280-16, 413, 683)

def back_to_main_menu():
    pyautogui.press('esc')
    click(634, 564)
    sleep(2)
    click(637, 517)
    click(141, 629)

def get_transcript():
    moveTo(248, 622)
    dragTo(795, 475)
    im = screenshot(430, 265, 1204, 682)
    dragTo(248, 622)
    return im

def ask_for_passport():
    moveTo(313, 636)
    dragTo(800, 477)
    click(800, 477)
    pyautogui.move(1,1)
    pyautogui.press('right')
    pyautogui.press('space')
    sleep(0.5)
    click(611, 392)
    click(144, 544)
    sleep(2)
    click(239, 628)
    sleep(5)
    moveTo(800, 477)
    pyautogui.press('left')
    dragTo(313, 636)

def put_citation_away():
    moveTo(640, 639)
    dragTo(1197, 268)

def has_finished():
    im = screenshot(586, 492, 675, 533)
    im2 = Image.open('anchors/okay.png')
    return (np.array(im) == np.array(im2)).all()

while True:
    try:
        max_loc = find_origin_coordinates()
        offset = max_loc[0] - 600, max_loc[1] - 580
        start_game()
        wanted_criminals = look_for_wanted_criminals()
        while not has_finished():
            call_next()
            sleep(2)
            docs = receive_all_documents()
            face = get_person_face()
            transcript = get_transcript()
            if not accept():
                ask_for_passport()
                docs.extend(receive_all_documents())
                accept()
            sleep(8)
            if has_finished():
                break
            result = screenshot(627, 494, 994, 646)
            if not os.path.exists('data'): os.mkdir('data')
            images = [face, wanted_criminals, transcript] + docs
            id = str(uuid.uuid4())
            os.mkdir('data/{}'.format(id))
            for i, im in enumerate(images):
                im.save('data/{}/{}.png'.format(id, i))
            result.save('data/{}/result.png'.format(id))
            put_citation_away()
    except Exception as e:
        print(e)
        if 'no endless found' in str(e):
            sleep(600)
            if not has_finished():
                raise
    click(632, 500)
    click(140, 627)
    sleep(2)