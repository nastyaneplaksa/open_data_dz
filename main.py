import re
import pandas as pd


df = pd.read_csv('audible_uncleaned.csv')
df.info()


#Смотрим, сколько уникальных значений содержится в каждом столбце
for col in df.columns:
    print(f'{col}: {df[str(col)].nunique()}')

#В столбце с автором (author) должно быть укзано только имя и фамилия.
#В исходных данных писутствует приставка "Написан:"
#(например, Writtenby:GeronimoStilton). Избавимся от этого.

#AUTHOR

#Посмотрим на уникальные значения столбца author:
df['author'].unique()
print(df['author'])

#Удаляем writtenby:
def rem_writby(text):
    return ' '.join(re.sub( r"([A-Z])", r" \1", text[10:]).split())

#Формируем читаемый список из имен и фамилий.
#Ограничим список первыми 20 авторами
author_list = []
for i in df['author']:
    author_list.append(rem_writby(i))
print(author_list[0:20])

#Теперь авторы книги записаны без приставки 'whittenby' и
#имена с фамилиями разделены пробелами.
#Перенесем исправленные и хорошо читаемые имена авторов
#а колонку authors, а изначальную колонку author удалим.

#Новая колонка authors
author_column = pd.Series(author_list)
df = df.assign(authors=author_column)
print(df)

#Удаление старой колонки author
df = df.drop('author', axis=1)
print(df)

#NARRATOR

#В столбце с рассказчиком/актером озвучки аудиокниги (narrator) 
#должно быть укзано только имя и фамилия.
#В исходных данных писутствует приставка "Рассказан/Озвучен:"
#(например, Narratedby:BillLobely). Избавимся от этого.

#Посмотрим на уникальные значения столбца narrator:
df['narrator'].unique()
print(df['narrator'])

#Удаляем narratedby:
def rem_natby(text):
    return ' '.join(re.sub( r"([A-Z])", r" \1", text[11:]).split())


#Формируем читаемый список из имен и фамилий.
#Ограничим список первыми 20 рассказчиками
nat_list = []
for i in df['narrator']:
    nat_list.append(rem_natby(i))
print(nat_list[0:20])


#Теперь рассказчики аудиокниг записаны без приставки 'narratedby',
#имена и фамилии разделены пробелами.
#Перенесем исправленные и хорошо читаемые имена рассказчиков
#а колонку narrators, а изначальную колонку narrator удалим.

#Новая колонка narrators
narrator_column = pd.Series(nat_list)
df = df.assign(narrators=narrator_column)
print(df)

##Удаление старой колонки narrator
df = df.drop('narrator', axis=1)
print(df)

#TIME

#Заменим занчения, которые меньше 1 минуты
#на полминуты
df = df.replace(['Less than 1 minute'], '1')
df.loc[df['time'] == 'Less than 1 minute']
print(df)

#Эти функции обрабатывают время в нужном числе;
#x минута или x минуты, аналогично с часами
def rm_mins(text):
    text.remove('mins')
    return text
    
def rm_min(text):
    text.remove('min')
    return text  

def sixty_hr(text):
    text[text.index('hr')] = '60'
    return text

def sixty_hrs(text):
    text[text.index('hrs')] = '60'
    return text


#Убирает min и mins, 
#преобразуем hr и hrs в численный формат int
time_list = []
for i in df['time']:
    i = i.split()
    if 'mins' in i:
        i = rm_mins(i)
    elif 'min' in i:
        i = rm_min(i)
    if 'hr' in i:
        i = sixty_hr(i)
    elif 'hrs' in i:
        i = sixty_hrs(i) 
    try:
        i.remove('and')
        time_list.append(i)
    except ValueError:
        #Выбрасываем исключение
        time_list.append(i)

#Cписок output будет содержать значения времени в минутах
#для каждого элемента списка time_list
output = []
for i in time_list:
    if '60' in i:
        output.append((int(i[i.index('60') - 1]) * int(60)) + int(i[-1]))
    else:
        output.append(int(i[0]))

#Присваиваем значение списку, потом серии
time = pd.Series(output)
#Новая колонка audible_time_in_m
df = df.assign(audible_time_in_m=time)
#Удаляем старую колонку time
df = df.drop('time', axis=1)
print(df)

#STARS

#Находит все числа в тексте и возвращает их в виде списка чисел.
#Функция для нахождения чисел среди текста
def rm_num(text):
    return re.findall(r'\d+', text)

#Цикл проходит по всему столбцу рейтинга, ищет только числовые
#значения и созраняет их в список,
#ограничим список первыми 20 значениями
rating_list = list()
for i in df['stars']:
    rating_list.append(rm_num(i))
rating_list[0:20]

#Получим списки rating и raters, содержащие рейтинги и
#количество рецензентов для каждого элемента из списка rating_list.
rating = list()
raters = list()
for i in rating_list:
    if len(i) == 4:
        rating.append(float(f'{i[0]}.{i[1]}'))
        raters.append(int(i[3]))
    elif len(i) == 3:
        rating.append(float(i[0]))
        raters.append(int(i[2]))
    else:
        rating.append(0.0)
        raters.append(0)

#Присваиваем значение списку, потом серии
rated_series = pd.Series(rating)
#Новая колонка audible_rating
df = df.assign(audible_rating=rated_series)
print(df)

rater_series = pd.Series(raters)
#Новая колонка rater_number
df = df.assign(rater_number=rater_series)
print(df)

#Удаляем колонку stars
df = df.drop('stars',axis=1)
print(df)

#Применяем индексацию для данных, выбраем только указанные столбцы
df = df[['name', 'authors', 'narrators' ,'audible_time_in_m', 'releasedate',
        'language', 'price', 'audible_rating', 'rater_number']]

#Метода выполняет автоматическое преобразование типов данных во всем df
df = df.convert_dtypes()

#Метод factorize() - факторизация категориальных столбцов.
#Присваиваем уникальные числовые значения
#каждому уникальному элементу в столбце исходного фрейма данных.
#Столбцы author_id, narrator_id, name_id и language_id содержат преобразованные
#числовые идентификаторы соответствующих категориальных столбцов.
df['author_id'] = pd.factorize(df['authors'])[0] + 1
df['narrator_id'] = pd.factorize(df['narrators'])[0] + 1
df['name_id'] = pd.factorize(df['name'])[0] + 1
df['language_id'] = pd.factorize(df['language'])[0] + 1

#Cнова применяем convert_dtypes() для обновления типов данных
#с учетом новых столбцов.
df = df.convert_dtypes()
print(df)

#PRICE

#Получим список цен в формате float или нулевое значение
#для бесплатного контента.
price_list = []
for i in df['price']:
    if i == 'Free':
        price_list.append(0.0)
    else:
        i = i.replace(',', '')
        price_list.append(i)
#Присваиваем значение списку, потом серии
price_series = pd.Series(price_list)
#Новая колонка exact_price
df = df.assign(exact_price=price_series)

#Тип данных float, так как не все цены могут быть целым числом
df['exact_price'] = df['exact_price'].astype(float)
#Удаляем колонку price
df = df.drop('price', axis=1)
print(df)

#MONTH, YEAR

#Из общей даты отбираем месяц и год
month_list = []
year_list = []

for i in df['releasedate']:
    month_list.append(i[3:5])
    year_list.append(i[6:])

#Присваиваем значение списку, потом серии
month_series = pd.Series(month_list)
#Новая колонка month
df = df.assign(month=month_series)
print(df)

year_series = pd.Series(year_list)
#Новая колонка year
df = df.assign(year=year_series)
print(df)

#Добавим id колонки, как делали до этого
df['month_id'] = pd.factorize(df['month'])[0] + 1
df['year_id'] = pd.factorize(df['year'])[0] + 1
df = df.convert_dtypes()
print(df)

#Посмотрим, что в итоге получилось 16 столбцов
print(df.info())
