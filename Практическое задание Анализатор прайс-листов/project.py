import os
import json

import pandas as pd


class PriceMachine():

    def __init__(self):
        self.data = []
        self.result = []
        self.name_length = 0

    def load_prices(self, file_path='catalog/'):
        '''
            Сканирует указанный каталог. Ищет файлы со словом price в названии.
            В файле ищет столбцы с названием товара, ценой и весом.
            Допустимые названия для столбца с товаром:
                товар
                название
                наименование
                продукт

            Допустимые названия для столбца с ценой:
                розница
                цена

            Допустимые названия для столбца с весом (в кг.)
                вес
                масса
                фасовка
        '''
        product_columns = ['товар', 'название', 'наименование', 'продукт']
        price_columns = ['розница', 'цена']
        weight_columns = ['вес', 'масса', 'фасовка']

        # Проходимся по всем файлам в каталоге
        for filename in os.listdir(file_path):
            if 'price' in filename.lower():  # Проверяем наличие слова 'price'
                full_path = os.path.join(file_path, filename)
                try:
                    df = pd.read_csv(full_path, encoding='utf-8')  # Читаем .csv файлы с помощью pandas
                    # Находим столбец с названием продукта
                    product_col = next((col for col in df.columns if col.lower() in product_columns), None)
                    if product_col is None:
                        continue  # Если нет нужного столбца, пропускаем файл

                    # Находим столбец с ценой
                    price_col = next((col for col in df.columns if col.lower() in price_columns), None)
                    if price_col is None:
                        continue

                    # Находим столбец с весом
                    weight_col = next((col for col in df.columns if col.lower() in weight_columns), None)
                    if weight_col is None:
                        continue

                    # Извлекаем данные из столбцов
                    products = df[product_col].values.tolist()
                    prices = df[price_col].values.tolist()
                    weights = df[weight_col].values.tolist()

                    # Добавляем данные в список self.data
                    for i in range(len(products)):
                        self.data.append({
                            'product_name': products[i],
                            'price': float(prices[i]),
                            'weight': float(weights[i]),
                            'file_name': filename,
                            'price_per_kg': round(float(prices[i] / weights[i]), 2)
                        })

                    print(f"Успешно загружены данные из файла {filename}")
                except Exception as e:
                    print(f"Произошла ошибка при загрузке данных из файла {filename}: {e}")

    def export_to_html(self, fname='output.html'):
        result = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
                <style>
        table {
            border-collapse: collapse;
            width: 100%;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        tr:nth-child(even) {background-color: #f2f2f2;}
        th {
            background-color: #4CAF50;
            color: white;
        }
    </style>
        </head>
        <body>
            <table>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        """
        # Добавляем строки данных
        for number, item in enumerate(self.result):
            result += f'''
                <tr>
                    <td>{number + 1}</td>
                    <td>{item['product_name']}</td>
                    <td>{item['price']}</td>
                    <td>{item['weight']}</td>
                    <td>{item['file_name']}</td>
                    <td>{item['price_per_kg']}</td>
                </tr>
        '''
        result += """
            </table>
        </body>
        </html>
        """
        with open(fname, 'w', encoding='utf-8') as file:  # Перезаписываем html файл
            file.write(result)

    def find_text(self, text: str):
        found_products = []

        # Производим поиск нужных продуктов по названию и сортируем их по цене за кг.
        for product in self.data:
            if text.lower() in product['product_name'].lower():
                found_products.append(product)
                found_products = sorted(found_products, key=lambda x: float(x['price_per_kg']))

        # Формируем таблицу для вывода результатов
        if found_products == []:
            print(f'Товар {text} не найден')
            return
        else:
            print('{:<3} {:<30} {:<10} {:<5} {:<15} {:<10}'.format(
                '№', 'Наименование', 'цена', 'вес', 'файл', 'цена за кг.'
            ))
            for i, item in enumerate(found_products, start=1):
                print(
                    f''
                    f'{i:<3} '
                    f'{item["product_name"]:<30} '
                    f'{int(float(item["price"])):<10} '
                    f'{float(item["weight"]):<5} '
                    f'{item["file_name"]:<15} '
                    f'{item['price_per_kg']:.2f}')
            self.result += found_products  # Добавляем найденные и отсортированные товары в общий список


pm = PriceMachine()
pm.load_prices()
while True:
    query = input("Введите название товара для поиска (или 'exit' для завершения программы): ")
    if query == 'exit':
        break
    else:
        pm.find_text(query)
print('the end')
pm.export_to_html()
