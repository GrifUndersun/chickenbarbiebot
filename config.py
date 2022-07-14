import json
import pickle

BOT_TOKEN = "5484451365:AAEaqEH0HdWlLbTnbeScuvQAPmzRYyEg4zs"
WEATHER_TOKEN = "2a37cb4a5c54181fc3985e431b76e256"
admin_id = 386581481


def findUser(data, code, cond, give):
    for x in data:
        if x[code] == cond:
            return x[give]


def open_usersDB(filename):
    try:
        with open(filename, 'r') as f:
            usersDB = json.load(f)
        return usersDB
    except Exception as e:
        print(e)
        users = []
        return users


def save_usersDB(filename, teleid, number, value):
    usersDB = open_usersDB(filename)
    new_db = []
    for x in usersDB:
        if x['id'] != int(teleid):
            new_db.append(x)

    new_db.append({
        'id': int(teleid),
        'group': int(number),
        'mailing': bool(value)
    })
    with open(filename, 'w') as f:
        json.dump(new_db, f)
    result = open_usersDB(filename)
    return result


if __name__ == '__main__':
    print(save_usersDB('database_students.json', admin_id, 151115, 0))
    print(open_usersDB('database_students.json'))
