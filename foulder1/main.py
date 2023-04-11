"""
1. Стоимость = 8 баллов. 
Трассировка автономных систем. Пользователь вводит доменное имя или IP адрес. 
Осуществляется трассировка до указанного узла (например, с использованием tracert), т. е. мы узнаем IP адреса маршрутизаторов, через которые проходит пакет. 
Необходимо определить к какой автономной системе относится каждый из полученных IP адресов маршрутизаторов.
Для определения номеров автономных систем обращаться к базам данных региональных интернет регистраторов.

Выход: для каждого IP-адреса – вывести результат трассировки (или кусок результата до появления ***), 
для "белых" IP-адресов из него указать номер автономной системы.
"""

import sys
import re
import subprocess
from urllib.request import urlopen

ip_regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"


def print_results(results):
    for i in results:
        print(''.join(item.ljust(20) for item in i))


def AS(ip):
    url = "https://www.nic.ru/whois/?ipartner=3522&adv_id=41_hq&utm_source=yandexdirect&utm_medium=cpc&utm_campaign" \
          "=whois_hq&utm_content=%7Cc%3A73068465%7Cg%3A5161777585%7Cb%3A13786192288%7Ck%3A43976711085%7Cst%3Asearch" \
          "%7Ca%3Ano%7Cs%3Anone%7Ct%3Apremium%7Cp%3A2%7Cr%3A43976711085%7Cdev%3Adesktop&_openstat" \
          "=ZGlyZWN0LnlhbmRleC5ydTs3MzA2ODQ2NTsxMzc4NjE5MjI4ODt5YW5kZXgucnU6cHJlbWl1bQ&yclid=16113620015265087487" \
          "&searchWord=" + ip
    page = urlopen(url).read().decode('utf-8')
    page = page[page.find('<div class="_3U-mA _23Irb">'):page.find('% This query was served by the RIPE Database '
                                                                   'Query Service version 1.106')]
    org = page.find('origin:')
    if org == -1:
        return "None"
    page = page[org:]
    mnt = page.find("mnt-by:")
    autonomous_system = page[:mnt]
    autonomous_system = "".join(autonomous_system.split())
    return autonomous_system.replace("origin:", "")


def tracert(clientInput):
    process = subprocess.Popen(["tracert", clientInput], stdout=subprocess.PIPE, universal_newlines=True)
    out, err = process.communicate()
    out = out[out.find(":") + 3:]
    ip = re.findall(ip_regex, out)
    if len(ip) == 0:
        print("Unable to resolve target system name", clientInput)
        sys.exit()
    results = [["№", "IP", "AS"]]
    for i in range(len(ip)):
        results.append([str(i + 1), ip[i], AS(ip[i])])
    print_results(results)


if __name__ == '__main__':
    tracert(input("Insert IP address or domain name: "))
