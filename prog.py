import os, sys, sqlite3

print('Данная программа работает с БД vuz.sqlite, состоящей из двух таблиц vuzkart и vuzstat.')
print('Программа предназначена для выполнения следующих функций:')
print('* отображение вузов, осуществляющих заочное обучение в выбранном субъекте РФ;')
print('* отображение распределения количества студентов по профилям, в выбранном федеральном округе.')
print('\n')

dbname = 'vuz.sqlite'

while True:
    vvod = input('Вы хотите выйти из программы [yes/no]: ')
    if vvod == 'yes':
        sys.exit()
    else:
        if (os.path.isfile(dbname)):
            break
        else:
            print('Файла с именем vuz.sqlite не существует')

print('\n')

con = sqlite3.connect(dbname)
cur = con.cursor()

def nazv_pol(tblname):
    """
    Функция для получения имён полей таблицы
    tblname – имя таблицы
    Возвращаемое значение: кортёж имён полей таблицы
    """
    cur.execute(f"PRAGMA table_info({tblname})")
    return tuple(x[1] for x in cur.fetchall())

def otobr(dbname): # vuzkart не очень
    """
    Функция для вывода таблицы БД на экран
    dbname – имя БД
    tblname – имя таблицы
    Возвращаемого значения нет
    """
    tblname = input('Введите имя таблицы: ')
    sql = 'SELECT * FROM {}'.format(tblname)
    data = cur.execute(sql).fetchall()
    print('Таблица: ',tblname,' из БД ',dbname)
    if tblname == 'vuzkart':
        print('{:^10} | {:^105} | {:^215} | {:^20} | {:^50} | {:^12} | {:^70} | {:^25} | {:^20} | {:^32} | {:^32} | {:^40} | {:^20} | {:^20} | {:^20} | {:^35} | {:^8} | {:^5}'.format(*nazv_pol(tblname)))
        print('-'*795)
        for d in data:
                print('{:^10} | {:^105} | {:^215} | {:^20} | {:^50} | {:^12} | {:^70} | {:^25} | {:^20} | {:^32} | {:^32} | {:^40} | {:^20} | {:^20} | {:^20} | {:^35} | {:^8} | {:^5}'.format(*d))
    else:
        print('{:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10}'.format(*nazv_pol(tblname)))
        print('-'*205)
        for d in data:
                print('{:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10}'.format(*d))


def choose_sub():
    """
    Функция для выбора субъекта РФ и отображения полных наименований вузов, осуществляющих в нём заочное обучение.
    Возвращаемого значения нет
    """
    
    sql_spis = f"""\
    SELECT DISTINCT vuzkart.oblname
    FROM vuzkart join vuzstat ON vuzkart.codvuz=vuzstat.codvuz
    ORDER BY vuzkart.oblname
    """
    spis = cur.execute(sql_spis).fetchall()
    print('{:^35}'.format('Список субъектов РФ'))
    print('-'*40)
    for s in spis:
        print('{:^35}'.format(*s))
    print('\n')
    flag = True
    while flag:
        obl = input('Введите субъект: ')
        for x in spis:
                if obl in x[0]:
                        flag = False
                        break
        else:
                print('Такого субъекта РФ нет')
    print('\n')
    sql_filter = f"""\
    SELECT vuzkart.z1
    FROM vuzkart join vuzstat ON vuzkart.codvuz=vuzstat.codvuz
    WHERE vuzkart.oblname LIKE '%{obl}%' AND ST_Z > 0
    """
    data = cur.execute(sql_filter).fetchall()
    print('{:^70}'.format('Полное наименование вуза'))
    print('-'*75)
    for d in data:
        print('{:^70}'.format(*d))

def choose_okr():
    """
    Функция для выбора федерального округа РФ или всех округов, и отображение таблицы распределения количества студентов по профилям в нём.
    Возвращаемого значения нет
    """
    sql_spis = f"""\
    SELECT DISTINCT vuzkart.region
    FROM vuzkart join vuzstat ON vuzkart.codvuz=vuzstat.codvuz
    ORDER BY vuzkart.region
    """
    spis = cur.execute(sql_spis).fetchall()
    spis.append(('Все              ',))
    print('{:^35}'.format('Список федеральных округов РФ'))
    print('-'*40)
    for s in spis:
        print('{:^35}'.format(*s))
    print('\n')
    flag = True
    while flag:
        fed_okr = input('Введите федеральный округ или \"Все\": ')
        for x in spis:
                if fed_okr in x[0]:
                        flag = False
                        break
        else:
                print('Такого федерального округа РФ нет')
    print('\n')
    names = ('num','prof','STUD','proc')
    if fed_okr == 'Все':
        cond = ''
    else:
        cond = f'WHERE vuzkart.region LIKE \'%{fed_okr}%\''
    sql_filter = f"""\
    WITH studs AS
    (
    SELECT vuzkart.prof AS {names[1]}, vuzstat.STUD AS {names[2]}
    FROM vuzkart join vuzstat ON vuzkart.codvuz=vuzstat.codvuz
    {cond}
    )

    SELECT ROW_NUMBER() OVER(ORDER BY {names[1]} ASC) AS {names[0]}, {names[1]}, SUM({names[2]}) AS {names[2]}, ROUND(SUM({names[2]})*100.0/(SELECT SUM({names[2]}) FROM studs),2) AS {names[3]}
    FROM studs
    GROUP BY {names[1]}
    """
    
    data = cur.execute(sql_filter).fetchall()
    sum_stud = 0
    for d in data: sum_stud+=d[2]
    print('{:^10} | {:^10} | {:^15} | {:^10}'.format(*names))
    print('-'*50)
    for d in data:
        print('{:^10} | {:^10} | {:^15} | {:^10}'.format(*d))
    print('{:^10} | {:^10} | {:^15} | {:^10}'.format(*['','Все',sum_stud,'']))

res = -1
while res != 0:
    print('\n')
    print('Меню программы:')
    print('0 - Завершение работы с программой.',
      '1 - Отображение текущего содержимого одной из таблиц на выбор.',
      '2 - Выбор субъекта РФ и отображение полных наименований вузов, осуществляющих в нём заочное обучение.',
      '3 - Выбор федерального округа РФ или всех округов, и отображение таблицы распределения количества студентов по профилям в нём.',sep='\n')
    print('\n')
    res = int(input('Введите номер операции:'))
    if res == 1:
        otobr(dbname)
    elif res == 2:
        choose_sub()
    elif res == 3:
        choose_okr()
    else:
        cur.close()
        con.close()
        print('Завершение работы c программой!')
