from shapely.geometry import Polygon
from shapely.geometry import box
import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image


model = YOLO('./web/best.pt')


def check_alert(results):
    file_path = './web/danger_zones/danger_Pgp-com2-K-1-0-9-36.txt'

    with open(file_path, 'r') as file:
        content = file.read()

    coordinates_str = content.split("\n")[:-1]
    polygon_coordinates = [
        tuple(map(int, coord.strip("[],").split(','))) for coord in coordinates_str]

    polygon = Polygon(polygon_coordinates)

    flag = False
    for result in results:

        hy = result.boxes.xywh.cpu().numpy()
        x, y, w, h = hy[0]

        # Вычисляем координаты вершин прямоугольника
        xmin, ymin, xmax, ymax = x, y, x + w, y + h

        # Создаем прямоугольник через Shapely
        rectangle = box(xmin, ymin, xmax, ymax)
        intersection_area = polygon.intersection(rectangle).area

        # Найдите площадь прямоугольника
        rectangle_area = rectangle.area

        # Рассчитайте процент перекрытия
        overlap_percentage = (intersection_area / rectangle_area) * 100

        flag = flag or overlap_percentage <= 15

    return flag


def alert(photo, img_path):
    cv2.imwrite(f'./alert/{img_path.name}', photo)


@st.cache_data
def find_danger(photos):
    progress_text = "Обработка фоток. Пожалуйста подождите."
    count_photos = len(photos)
    bar = st.progress(0, text=progress_text)

    new_photos = []
    for i, photo in enumerate(photos, 1):
        pil_image = Image.open(photo)
        pil_image = pil_image.resize((1280, 720))
        results = model.track(pil_image, persist=True, verbose=False)
        res_plotted = results[0].plot()
        if check_alert(results):
            alert(res_plotted, photo)
        res_plotted = cv2.cvtColor(res_plotted, cv2.COLOR_BGR2RGB)
        new_photos.append(res_plotted)
        bar.progress(int(i / count_photos * 100), text=progress_text)

    bar.empty()

    return new_photos


def main():
    st.title("Поиск опасных ситуаций")

    photos = st.file_uploader(
        "Загрузите фото", type=["jpg", "png"], accept_multiple_files=True)

    if photos:
        new_photos = find_danger(photos)
        current_image_index = 1
        if len(new_photos) - 1:
            current_image_index = st.slider(
                "Выберите изображение", 1, len(new_photos), 1)
        st.image(new_photos[current_image_index - 1],
                 caption=f"Изображение {current_image_index}", use_column_width=True)


if __name__ == "__main__":
    main()
