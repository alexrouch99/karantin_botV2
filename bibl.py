import cv2
import numpy as np
import pyautogui
import time
from datetime import datetime, timedelta


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

