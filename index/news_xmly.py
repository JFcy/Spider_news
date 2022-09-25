# author:冯重阳
# @File：news_xmly.py
import requests #爬取网页数据的包
import re   #正则提取
import os   #创建文件夹
import sqlite3  #数据库

#用来存放音频信息的类，
class music_info:
    #UA伪装，以浏览器身份发起请求
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Wi n64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'
    }
    #爬取的网址，喜玛拉雅，新闻联播文件信息的存放网址
    url_generate_part1='https://www.ximalaya.com/revision/album/v1/getTracksList?albumId=31923706&pageNum='
    url_generate_part2='&sort=1'
    #姓名和id的正则提取式
    os_name = '"title":"(.*?)"'
    os_id = '"trackId":(.*?),'

#用来存放对数据库操作的类
class db_coporate:
    #数据库的路径
    db_path = "../新闻联播数据.db"
    #对数据库的插入操作
    # 创建数据库
    def create_db(self):
        conn = sqlite3.connect('../新闻联播数据.db')
        c = conn.cursor()
        # 创建表，来存储每一个音频的网址。减少以后的下载时获从总网页爬取id，从id爬取json，从json重提取网址的速度
        sql_create = '''
        create table if not exists news_data(
        id int primary key not null,
        name int not null,
        url text not null
        )
        '''
        # 执行创建操作
        c.execute(sql_create)
        # 提交操作
        conn.commit()
        conn.close()

    def insert(self,id_list,url):
        #连接数据库
        conn = sqlite3.connect(self.db_path)
        #获得操作的游标
        c = conn.cursor()
        #拼接sql操作语言
        for num in range(0,len(id_list)):
            a = '"' + url[num] + '"'
            sql = '''
            insert OR IGNORE into news_data(id,name,url)
            values(%d,%d,%s)'''%(num + 1,id_list[num],a)
            #执行操作，把网址和名字存入数据库
            c.execute(sql)
            #print(sql)
            #print(name[num]," record successful !!")
        #按照姓名做好排序
        sql_sort = '''
        select * from news_data
        order by name desc
        '''
        c.execute(sql_sort)
        conn.commit()
        conn.close()


    def selectinfo(self,id):
        # 连接数据库
        conn = sqlite3.connect(self.db_path)
        # 获得操作的游标
        c = conn.cursor()
        # 拼接sql操作语言
        sql = '''select name ,url from news_data where id <= %d'''%(int(id))
        c.execute(sql)
        result = c.fetchall()
        return result

#将数据下载到文件夹中
def data_save(music_data,name):
    #创建文件夹
    with open("./新闻联播音频文件/" + name ,'wb') as fp:
        #写入数据
        fp.write(music_data)
    print(name," finish!!!")

#从最初网页中解析获取音频的id和name
def Getinfo(number):
    #用来存储id和姓名的列表
    id_list = []
    name_list = []
    #逐页爬取所需要的信息
    for num in range(1,int(number+1)):
        #拼接网址
        url = music_info.url_generate_part1+str(num)+music_info.url_generate_part2
        #得到含有id值的网页数据
        tot = requests.get(url=url,headers=music_info.headers).text
        #利用re和正则表达式来解析初id和姓名
        id_list = id_list + re.findall(music_info.os_id,tot,re.S)
        name_list = name_list + re.findall(music_info.os_name,tot,re.S)
    return id_list,name_list

#通过拼接还原音频文件所在的网址，并进行爬取
def Get_music_data(id_list,name_list):
    #存储总的音频信息
    music_src = []
    for each in range(len(id_list)):
        #通过id来获取json，json重含有音频网址
        music_src_url='https://www.ximalaya.com/revision/play/v1/audio?id='+str(id_list[each])+'&ptype=1'
        #根据id拼接单独网址，发起请求，获取json数据
        music_src_response = requests.get(url=music_src_url,headers=music_info.headers).json()
        #在json数据重，取出对应的音频的网址
        music_src.append(music_src_response["data"]["src"])
        print(name_list[each],"成功获取信息!!")
        #在音频网址重，下载音频
        # music_data = requests.get(url=music_src,headers=music_info.headers).content
        # #把音频下载下来，保存到指定路径下
        # data_save(music_data,name_list[each])
    return music_src



def download_news(number):
    if not os.path.exists("../新闻联播音频文件"):
        os.mkdir("../新闻联播音频文件")
    db_coporate.create_db(db_coporate)
    pages = int(number)/30
    message = Getinfo(pages)
    id_list = message[0]
    name_list = message[1]
    url_list = Get_music_data(id_list,name_list)
    id_list = []
    for name in name_list:
        id_list.insert(0,int(name.split(' ')[1]))
    print(id_list)
    db_coporate.insert(db_coporate,id_list,url_list)
    return name_list




