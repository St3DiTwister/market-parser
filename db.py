import sqlite3

import messageSender


def add_db(skins):
    con = sqlite3.connect('db.sqlite')
    cur = con.cursor()
    for skin in skins:
        cur.execute(f"SELECT * FROM skins WHERE name=?", (skin['name'], ))
        find = list(map(list, cur.fetchall()))
        if not find:
            cur.execute(f"INSERT INTO skins (name, url, old_price, new_price, dif) VALUES (?, ?, ?, ?, ?)", (skin['name'], skin['url'], float(skin['price']), 0, 0))
            con.commit()
        else:
            if find[0][4] == 0:
                if find[0][3] != float(skin['price']) and float(skin['price']) != 0.0:
                    cur.execute(f"UPDATE skins SET new_price = ? WHERE name=?", (float(skin['price']), skin['name']))
                    con.commit()
                    dif = (float(skin['price']) - find[0][3])
                    cur.execute(f"UPDATE skins set dif = {dif} WHERE name=?", (skin['name'],))
                    con.commit()
                else:
                    pass
            else:
                if find[0][4] != float(skin['price']):
                    cur.execute(f"UPDATE skins SET old_price = {find[0][4]}, new_price=? WHERE name=?", (float(skin['price']), skin['name']))
                    con.commit()
                    dif = (float(skin['price']) - find[0][3])
                    cur.execute(f"UPDATE skins set dif = {dif} WHERE name=?", (skin['name'],))
                    con.commit()
                    cur.execute(f"UPDATE skins SET sended=0 WHERE name=?", (skin['name'],))
                    con.commit()
                else:
                    pass

                profit = (find[0][3] - (find[0][3] * 0.15)) - float(skin['price'])
                if profit > 150 and 'Наклейка' not in find[0][1] and find[0][-1] != 1 and find[0][4] < 3000:
                    messageSender.send_message([find[0][1], find[0][2], f'Старая цена: {find[0][3]}', f'Новая цена: {find[0][4]}', f'Разница: {(float(skin["price"]) - find[0][3])}', f'Прибыль: {profit}'])
                    cur.execute(f"UPDATE skins SET sended=1 WHERE name=?", (skin['name'], ))
                    con.commit()

    cur.close()
    con.close()

    return 1


def db_results():
    con = sqlite3.connect('db.sqlite')
    cur = con.cursor()
    cur.execute(f"SELECT * FROM skins WHERE dif<0")
    find = list(map(list, cur.fetchall()))
    cur.close()
    con.close()
    if not find:
        return 0
    else:
        return find