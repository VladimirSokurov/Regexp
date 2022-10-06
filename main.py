from pprint import pprint
import re
import csv
from collections import Counter

pattern1 = r'(\w+)(\s\w+)?(\s\w+)?;(\w+)?(\s\w+)?;(\w+)?;(\w+)?;((\w*[–\s]*)*)?;((\+)?(7|8)\s?(\d{3})?(\d{3})?(\d{2})?(\d{2})?(\(\d+\))?\s?[-\s]?(\d*)[-\s]?(\d*)[-\s]?(\d*)\s?(\()?(\w+(\.)?)?\s?(\d+)?(\))?)?;(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b)?'
pattern2 = r'(\+)?(7|8)\s?(\d{3})?(\d{3})?(\d{2})?(\d{2})?(\((\d+)\))?\s?[-\s]?(\d*)[-\s]?(\d{2})[-\s]?(\d{2})\s?(\()?(\w+(\.)?)?\s?(\d+)?(\))?'
sub_pattern_1 = r'+7(\8\3)\9\4-\10\5-\11\6 \13\15'
sub_pattern_2 = r'+7(\8\3)\9\4-\10\5-\11\6'


def open_phonebook(name):
    with open(name) as f:
        rows = csv.reader(f, delimiter=",")
        contacts_list = list(rows)
    return contacts_list


def add_f(dict, key: str, result, group_number):
    if result.group(group_number):
        text = result.group(group_number)
        dict[key] = f'{text.strip()};'


def add_new_contacts_list(contacts_list):
    new_contacts_list = []
    for id, i in enumerate(contacts_list):
        if id != 0:
            new_l = []
            new_dict = {}
            result = re.search(pattern1, i[0])
            add_f(new_dict, 'lastname', result, 1)
            add_f(new_dict, 'firstname', result, 2)
            add_f(new_dict, 'firstname', result, 4)
            add_f(new_dict, 'surname', result, 3)
            add_f(new_dict, 'surname', result, 5)
            add_f(new_dict, 'surname', result, 6)
            add_f(new_dict, 'organization', result, 7)
            add_f(new_dict, 'position', result, 8)
            add_f(new_dict, 'phone', result, 10)
            add_f(new_dict, 'email', result, 26)
            new_l.append(result.group())
            new_contacts_list.append(new_dict)
    return new_contacts_list


def change_phone_pattern(new_contacts_list, pattern2, sub_pattern_1, sub_pattern_2):
    for j in new_contacts_list:
        if j.get('phone'):
            result2 = re.search(pattern2, j.get('phone'))
            if len(j.get('phone')) > 16:
                sub_res = re.sub(pattern2, sub_pattern_1, j.get('phone'))
            else:
                sub_res = re.sub(pattern2, sub_pattern_2, j.get('phone'))
            j['phone'] = sub_res
    changed_new_contacts_list = new_contacts_list
    return changed_new_contacts_list


def count_lastnames_dict(changed_new_contacts_list):
    lastnames_list = []
    for k in changed_new_contacts_list:
        lastnames_list.append(k['lastname'])
    counter = Counter(lastnames_list)
    return counter


def add_unique_lastnames_list(counter):
    unique_lastnames_list = []
    for k, v in counter.items():
        if v > 1:
            unique_lastnames_list.append(k)
    return unique_lastnames_list


def update_doubles(new_contacts_list, unique_lastnames_list):
    for id1, contact in enumerate(new_contacts_list):
        if contact['lastname'] in unique_lastnames_list:
            lastname = contact['lastname']
            double = contact
            for id2, contact2 in enumerate(new_contacts_list):
                if contact2['lastname'] == lastname:
                    if id2 != id1:
                        contact2.update(double)
    updated_new_contacts_list = new_contacts_list
    return updated_new_contacts_list


def remove_doubles(counter, updated_new_contacts_list):
    for key, value in counter.items():
        if value > 1:
            for j in range(value - 1):
                for i in updated_new_contacts_list:
                    if i['lastname'] == key:
                        updated_new_contacts_list.remove(i)
                        break
    new_contacts_list_ = updated_new_contacts_list
    return new_contacts_list_


def set_finish_list(contacts_list, new_contacts_list_):
    finish_list = []
    finish_list.append(contacts_list[0])
    for i in new_contacts_list_:
        inner_list = [";", ";", ";", ";", ";", ";", ";"]
        joined_inner_list = []
        for key, value in i.items():
            if key == "lastname":
                inner_list.pop(0)
                inner_list.insert(0, value)
            if key == "firstname":
                inner_list.pop(1)
                inner_list.insert(1, value)
            if key == "surname":
                inner_list.pop(2)
                inner_list.insert(2, value)
            if key == "organization":
                inner_list.pop(3)
                inner_list.insert(3, value)
            if key == "position":
                inner_list.pop(4)
                inner_list.insert(4, value)
            if key == "phone":
                inner_list.pop(5)
                inner_list.insert(5, value)
            if key == "email":
                inner_list.pop(6)
                inner_list.insert(6, value)
        joined_inner_string = "".join(inner_list)
        joined_inner_list.append(joined_inner_string)
        finish_list.append(joined_inner_list)
    return finish_list


def get_phonebook(new_name):
    with open(new_name, "w") as f:
        datawriter = csv.writer(f, delimiter=',')
        datawriter.writerows(finish_list)


if __name__ == "__main__":
    contacts_list = open_phonebook("phonebook_raw.csv")
    new_contacts_list = add_new_contacts_list(contacts_list)
    changed_new_contacts_list = change_phone_pattern(new_contacts_list, pattern2, sub_pattern_1, sub_pattern_2)
    counter = count_lastnames_dict(changed_new_contacts_list)
    unique_lastnames_list = add_unique_lastnames_list(counter)
    updated_new_contacts_list = update_doubles(new_contacts_list, unique_lastnames_list)
    new_contacts_list_ = remove_doubles(counter, updated_new_contacts_list)
    finish_list = set_finish_list(contacts_list, new_contacts_list_)
    get_phonebook("phonebook.csv")
