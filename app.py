# регулярки
#import re, urllib
#import uuid


import hashlib
import sqlite3
from flask import Flask, redirect, render_template, request

app = Flask(__name__)



try:
    sqlite_conn = sqlite3.connect('links.sqlite')
    cursor = sqlite_conn.cursor()
except sqlite3.Error:
    print('ОШИБКА БД!!!')


try:
    querry = '''CREATE TABLE LinkCrap (full_link TEXT,short_link TEXT)'''
    cursor.execute(querry)
    sqlite_conn.commit()
    cursor.close()
except sqlite3.OperationalError:
    pass


#Метод для получения короткой ссылки
def get_short_link(long_link):
    while True:
        try:
            cursor = sqlite_conn.cursor()
            check = cursor.execute('''SELECT full_link FROM LinkCrap''')
            if long_link in check:
                short_link = cursor.execute('''SELECT short_link FROM LinkCrap WHERE full_link =?''',(long_link,))
                cursor.close()
            else:
                short_link = hashlib.md5(long_link.encode()).hexdigest()[:8]
                cursor.execute('''INSERT INTO LinkCrap (full_link,short_link) VALUES (?,?)''', (long_link, short_link,))
                sqlite_conn.commit()
                cursor.close()
            return short_link

        except:
            pass


# Заглавная страница
# Здесь пользователь вводит URL + проверка + дополнение в бд и получение сокращенной ссылки пользователю
@app.route('/', methods=["GET", "POST"])
def que():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        link_input = request.form.get("longlinkinput")
        short_link = get_short_link(link_input)
        return render_template("index.html", resultat = short_link)


#Метод который перенаправляет с короткой на длинную ссылку.
@app.route('/<short_link>')
def short_link_redirect(short_link):
    try:
        cursor = sqlite_conn.cursor()
        tmp = cursor.execute('''SELECT full_link FROM LinkCrap WHERE short_link = ?''',(short_link,))
        return redirect(tmp)
        cursor.close()
    except:
        return "Такой ссылки не существует"


if __name__ == '__main__':
    app.run(host='0.0.0.0')