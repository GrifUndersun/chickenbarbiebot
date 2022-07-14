import bs4
import requests
import json


# загрузить из json
with open('groups_data.json', 'r') as file:
    data = json.load(file)


def content_in_text(cnt):
    z = ''
    try:
        for x in cnt:
            s = (x.getText().strip())
            s = s.replace('\t', '')
            s = s.replace('\n', '')
            while "  " in s:
                s = s.replace("  ", " ")
            z += s
    except:
        z = ''
    return z


def get_siteID(groupNum):
    try:
        for group_dict in data:
            if group_dict['RealId'] == int(groupNum):
                return group_dict['SiteId']
    except:
        return -1


def get_groupName(groupNum):
    try:
        for group_dict in data:
            if group_dict['RealId'] == int(groupNum):
                return group_dict['Name']
    except:
        return -1


def get_timetable(groupNum):
    groupID = get_siteID(groupNum)
    rslt = {}
    s = requests.get(f'https://ruz.narfu.ru/?timetable&group={groupID}')
    s.encoding = s.apparent_encoding
    b = bs4.BeautifulSoup(s.text, "html.parser")
    content = b.find('div', class_='row tab-pane active')
    day_content = content.findAll('div', class_='list')
    for i in day_content:
        day = content_in_text(i.find('div', class_='dayofweek'))
        timetable_content = i.findAll('div', class_='timetable_sheet')
        timetable = ''
        for x in timetable_content:
            num_para = content_in_text(x.find('span', class_="num_para"))
            time_para = content_in_text(x.find('span', class_='time_para'))
            kind_of_work = content_in_text(x.find('span', class_='kindOfWork'))
            discipline = content_in_text(x.find('span', class_='discipline'))
            group = content_in_text(x.find('span', class_='group'))
            auditorium = content_in_text(x.find('span', class_='auditorium'))
            if discipline == '':
                table_str = ''.join('\n{}) Нет занятий\n'.format(num_para))
            else:
                table_str = ''.join('\n{}) <b>{}</b>\n<i>{}</i>\n{}\n{}\n<code>{}</code>\n'.format(num_para, time_para, kind_of_work, discipline,
                                                           group, auditorium))
            timetable += table_str
        if timetable == '':
            rslt[day] = '\nВ этот день нет пар\n'
        else:
            rslt[day] = timetable

    return rslt


def print_timetable(timetable):
    days = []
    table = []
    for key, value in timetable.items():
        days.append(key)
        table.append(timetable[key])

    return days, table


if __name__ == '__main__':
    print(get_timetable(151115))


