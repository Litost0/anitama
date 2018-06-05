import requests
import json
import re
import sqlite3
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

from pylab import mpl

'''发送HTTP请求'''
def crawler(url):
    resp = requests.get(url)

    if resp.status_code != 200:
        print('Error code: {}'.format(res.status_code))
        return None

    return resp.content

'''解析HTML'''
def parser(url_lag):
    url = 'http://www.anitama.cn'
    chunk_list = []

    html = crawler(url+url_lag)
    if not html:
        return None

    soup = BeautifulSoup(html)
    list_soup_id = soup.find('div', attrs={'id': 'area-article-channel'})
    list_soup_cls = list_soup_id.find('div', attrs={'class': 'inner'})

    for list_soup_a in list_soup_cls.find_all('a', attrs={'class': 'item'}):
        try:            
            channel = list_soup_a.find('span', attrs={'class': 'channel'})
            author = list_soup_a.find('span', attrs={'class': 'author'})
            title = list_soup_a.find('h1')
            chunk_list.append([x.getText() for x in [channel, author, title]])
        except AttributeError as e:
            print('Not found: {}'.format(e))

    next_page = list_soup_cls.find('div', attrs={'class': 'area-pager'})
    next_url_lag = next_page.find('a', attrs={'class': 'pager pager-fores'})
    if next_url_lag:
        return chunk_list, next_url_lag['href']
    else:
        return chunk_list, None

"""写入到文件"""
def write_file(page_lim=20):
    url_lag = '/channel'
    cnt = 0
    with open('anitama.txt', 'w') as f:   
        while url_lag and cnt < page_lim:
            chunk_list, url_lag = parser(url_lag)
            cnt += 1
            for chunk in chunk_list:
                f.write('| |'.join(chunk)+'\n')

"""存入数据库"""
def write_db(page_lim=5):
    url_lag = '/channel'
    cnt = 0
    conn = sqlite3.connect('anitama.db')
    cursor = conn.cursor()
    cursor.execute('drop table anitama') # 删库啦
    cursor.execute('create table anitama (channel varchar(100), author varchar(100), title varchar(100))')
    while url_lag and cnt < page_lim:
        chunk_list, url_lag = parser(url_lag)
        cnt += 1
        for chunk in chunk_list:  # chunk = [channel, author, title]
            sql_se = 'insert into anitama (channel, author, title) values (\'{0[0]}\', \'{0[1]}\', \'{0[2]}\')'.format(chunk)
            cursor.execute(sql_se)

    cursor.close()
    conn.commit()
    conn.close()


def plot_bar():
    mpl.rcParams['font.sans-serif'] = ['FangSong'] # 确保中文正确输出
    mpl.rcParams['axes.unicode_minus'] = False

    channel_dict = {}
    author_dict = {}
    with open('anitama.txt', 'r') as f:
        for line in f.readlines():
            item_list = line.split('| |')
            channel_dict[item_list[0]] = channel_dict.get(item_list[0], 0) + 1 # Vote
            author_dict[item_list[1]] = author_dict.get(item_list[1], 0) + 1

    sorted_channel = sorted(channel_dict.items(), key=lambda item: item[1], reverse=True)
    sorted_author = sorted(author_dict.items(), key=lambda item: item[1], reverse=True)
    channel_ran = range(len(sorted_channel))
    author_ran = range(len(sorted_author))
    
    '''以下是作图'''
    fig = plt.figure()

    ax1 = fig.add_subplot(211)
    channel_list = [sorted_channel[i][0] for i in channel_ran]
    vote_list = [sorted_channel[i][1] for i in channel_ran]
    plt.xticks(channel_ran, channel_list)
    plt.bar(channel_ran, vote_list)

    ax2 = fig.add_subplot(212)
    author_list = [sorted_author[i][0] for i in author_ran]
    vote_list_2 = [sorted_author[i][1] for i in author_ran]
    plt.xticks(author_ran, author_list)
    plt.bar(author_ran, vote_list_2)

    plt.show()



if __name__ == '__main__':
    #write_file()
    #write_db()
    plot_bar()


