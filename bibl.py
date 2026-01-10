import cv2
import numpy as np
import pyautogui
import time
from datetime import datetime, timedelta
import pyautogui
import easyocr
import os

from bd import (
    is_blacklisted,
    add_found_item,
    add_item_change,
    add_unique_item
)

region_loc = (1650, 0, 270, 185)  # регион свойства локации (окно справа сверху)
region_pers = (0, 0, 290, 175)  # регион свойства персонажа (окно слева сверху)
coord_loc = (613, 509, 304, 231)  # регион описания локации (для определения в какой локации находится персонаж)
region_predmet = (845, 445, 227, 187)  # регион окна найденного предмета
window_notepad = (570, 280, 770, 480)  # регион окна поиска (всего блокнота)
region_modern = (965, 300, 345, 455)  # регион окна модернизации (апгрейдов)
region_aps = (780, 404, 370, 200)  # регион окна выбора апгрейдов

def find_button(
    path: str,
    conf: float = 0.8,
    time_limit: float = 3.0,
    pause: float = 0.2,
    region: tuple | None = None
):
    """
    Ищет кнопку на экране и возвращает координаты центра.
    :return: (x, y) если найдено, иначе None
    """

    print(f"[FIND] Загружаем шаблон: {path}")

    template = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        raise ValueError(f"[ERROR] Не удалось загрузить изображение: {path}")

    h, w = template.shape
    finish_time = datetime.now() + timedelta(seconds=time_limit)

    while datetime.now() < finish_time:
        print("[FIND] Делаем скриншот")

        screenshot = pyautogui.screenshot(region=region)
        screen = cv2.cvtColor(
            np.array(screenshot),
            cv2.COLOR_RGB2GRAY
        )

        print("[FIND] Сравниваем изображение")
        result = cv2.matchTemplate(
            screen,
            template,
            cv2.TM_CCOEFF_NORMED
        )

        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        print(f"[FIND] Уверенность совпадения: {max_val:.3f}")

        if max_val >= conf:
            x = max_loc[0] + w // 2
            y = max_loc[1] + h // 2

            if region:
                x += region[0]
                y += region[1]

            print(f"[FIND] Кнопка найдена: ({x}, {y})")
            return x, y

        print("[FIND] Не найдено, ждём...")
        time.sleep(pause)

    print("[FIND] Таймаут, кнопка не найдена")
    return None

def click_button(
    path: str,
    conf: float = 0.8,
    time_limit: float = 5.0,
    pause: float = 0.2,
    region: tuple | None = None
):
    """
    Ищет кнопку и кликает по ней.

    :return: True если клик выполнен, иначе False
    """

    print(f"[CLICK] Пытаемся нажать кнопку: {path}")

    coords = find_button(
        path=path,
        conf=conf,
        time_limit=time_limit,
        pause=pause,
        region=region
    )

    if coords is None:
        print("[CLICK] Кнопка не найдена, клик невозможен")
        return False

    x, y = coords
    print(f"[CLICK] Кликаем по координатам: ({x}, {y})")
    pyautogui.click(x, y)
    return True


def compare_with_folder(image, folder: str, conf: float = 0.8):
    """
    image — numpy.ndarray (grayscale!)
    """

    print("[COMPARE] Сравнение изображения с папкой")

    if image is None:
        print("[COMPARE] Ошибка: изображение пустое")
        return False, None, None

    for filename in os.listdir(folder):
        ref_path = os.path.join(folder, filename)

        ref = cv2.imread(ref_path, cv2.IMREAD_GRAYSCALE)
        if ref is None:
            continue

        # Приводим размеры
        if image.shape != ref.shape:
            ref = cv2.resize(ref, (image.shape[1], image.shape[0]))

        result = cv2.matchTemplate(
            image,
            ref,
            cv2.TM_CCOEFF_NORMED
        )

        _, max_val, _, _ = cv2.minMaxLoc(result)
        print(f"[COMPARE] {filename}: confidence={max_val:.3f}")

        if max_val >= conf:
            print(f"[COMPARE] Совпадение найдено: {filename}")
            return filename

    print("[COMPARE] Совпадений нет")
    return None

def eating():
    while(True):
        eda = find_button("capture/eda_full.png",conf=0.98, region=region_pers)
        if eda is None:
            print("Персонаж голоден")
            click_button("capture/notepad.png", region=region_pers)
            click_button("capture/popcorn.png", region=window_notepad)
            click_button("capture/isp.png", region=window_notepad)
            pyautogui.moveTo(1, 2)
            time.sleep(3)
        else:
            print("Персонаж сыт")
            break
def poisk():
    print("Начало поиска")
    scanner = easyocr.Reader(["ru"], gpu=True)
    print("EasyOCR включился")
    #  функция проверки сытости и её восполнения
    # eating()
    #  функция открытия окна локации
    win = find_button("capture/home.png")
    if win is None:
        click_button("capture/location.png")
        click_button("capture/home.png")
    else:
        click_button("capture/home.png")
    # ------------------------------
    # функция проверки локации
    screenshot = pyautogui.screenshot(region=window_notepad)
    image = cv2.cvtColor(
        np.array(screenshot),
        cv2.COLOR_RGB2GRAY
    )
    loc = compare_with_folder(image, "capture/loc")



    while True:
        print("Начало цикла")

        # --- Переход в окно поиска ---
        button = find_button("capture/poisk.png")
        if button is None:
            click_button("capture/home.png")
        click_button("capture/poisk.png")

        end = find_button("capture/no_energy.png")
        if end:
            print("Недостаточно энергии")
            return 'END'

        ok = find_button("capture/ok.png", time_limit=5)
        print("Кнопка ОК найдена")

        if not ok:
            continue


        timenow = datetime.now()
        timename = timenow.strftime('%d%m%y%H%M%S')

        image_path = f"capture/history/{timename}.png"
        pyautogui.screenshot(
            image_path,
            region=region_predmet
        )

        print("Скриншот предмета сделан")

        # --- OCR ---
        result = scanner.readtext(image_path, detail=0)

        if len(result) < 2:
            print("OCR не распознал предмет")
            click_button("capture/ok.png", region=region_predmet)
            continue

        raw_name = result[1]
        predmet = raw_name.replace(' ', '_')

        print(f"Найден предмет: {predmet}")

        # --- Проверка черного списка ---
        # if is_blacklisted(predmet):
        #     print("Предмет в черном списке")
        #
        #     putButton('capture/cancel.png', 0.8, 3)
        #     putButton('capture/ok.PNG', 0.8, 5)
        #     continue

        # --- Добавление в БД найденных предметов ---
        # --- 1. ВСЕ найденные предметы ---
        add_found_item(
            location=loc,
            name=predmet,
            image_path=image_path
        )
        print("Предмет записан в журнал находок")

        # --- 2. ТОЛЬКО уникальные предметы ---
        added_unique = add_unique_item(
            location=loc,
            old_name=raw_name,
            new_name="*",
            image_path=image_path
        )

        if added_unique:
            print("Новый уникальный предмет добавлен")
        else:
            print("Такой предмет уже есть, пропуск")

        click_button("capture/ok.png")

def test():
    compare_with_folder()

def screenshot_region(region: tuple, save_dir: str, name: str | None = None) -> str:
    """
    Делает скриншот области экрана и сохраняет в файл.

    :param region: (x, y, width, height)
    :param save_dir: папка для сохранения
    :param name: имя файла (без .png), если None — генерируется автоматически
    :return: путь к сохранённому файлу
    """

    if name is None:
        name = datetime.now().strftime('%Y%m%d_%H%M%S')

    path = f"{save_dir}/{name}.png"

    print(f"[SHOT] Делаем скриншот области {region}")
    screenshot = pyautogui.screenshot(region=region)
    screenshot.save(path)

    print(f"[SHOT] Скриншот сохранён: {path}")
    return path
