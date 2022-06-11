import pickle


BOT_TOKEN = "5525263494:AAHwvyyNJRTG2zXGyXyTxCL3YVbJT2q8Sp8"
admin_id = 386581481


def open_usersDB():
    with open('database_user_number_group.data', 'rb') as f:
        users = pickle.load(f)
    return users


def save_usersDB(id, number):
    usersDB = open_usersDB()
    usersDB[id] = number

    with open('database_user_number_group.data', 'wb') as f:
        pickle.dump(usersDB, f)

    return usersDB