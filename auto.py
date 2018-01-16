import http.client
import requests
import json
from bs4 import BeautifulSoup
import time
from operator import itemgetter

def output_log(ms):
    with open('outms.log', 'a',encoding='utf-8') as file:
        file.write(time.ctime() + ':   ' + ms + '\n')


def get_setcookie(response):
    res_headers = str(response.headers)
    res_headlist = res_headers.split('\n')
    key_cookies = ''
    for x in res_headlist:
        if x[:10] == 'Set-Cookie':
            x_ = x.split(':')
            if key_cookies == '':
                key_cookies = '%s' % x_[1]
            else:
                key_cookies = key_cookies + ';%s' % x_[1]
    return key_cookies


def generate_cookies(cookie):
    cookies = {}
    x = cookie.split('; ')
    for y in x:
        z = y.split('=')
        z[0] = z[0].strip()
        if z[0] == 'path':
            continue
        else:
            cookies[z[0]] = z[1]
    return cookies


def generate_headers(cookies=None):
    if cookies == None:
        headers = {
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'Accept-Encoding': "gzip, deflate",
            'Accept-Language': "zh-CN,zh;q=0.9",
            'Cache-Control': "no-cache",
            'Connection': "keep-alive",
            'Host': "zb.mangsou.com",
            'Upgrade-Insecure-Requests': "1",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36",
        }

    else:
        headers = {
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'Accept-Encoding': "gzip, deflate",
            'Accept-Language': "zh-CN,zh;q=0.9",
            'Cache-Control': "no-cache",
            'Connection': "keep-alive",
            'Host': "zb.mangsou.com",
            'Upgrade-Insecure-Requests': "1",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36",
            'Cookie': cookies
        }
    return headers

def output_time(func):
    def wrapper(*args,**kw):
        t1 = time.time()
        res = func(*args, **kw)
        t2 = time.time()
        print('【耗时】%s函数耗时%s' % (func.__name__,t2-t1))
        return res
    return wrapper

class User(object):
    def __init__(self,username, password):
        self.username = username
        self.password = password
        conn = http.client.HTTPConnection("zb.mangsou.com")
        # 获得必要cookies
        self.headers_1 = generate_headers()
        conn.request("GET", "/gwf?url=/user/login", headers=self.headers_1)
        res_1 = conn.getresponse()
        self.key_cookies = get_setcookie(res_1)
        conn.close()
        # 获得group_id
        self.group_id = self.key_cookies.split('; ')[2]
        # 获取PHPSESSID
        headers_2 = generate_headers(self.key_cookies)
        conn.request('GET', '/user/login', headers=headers_2)
        res_2 = conn.getresponse()
        self.phpsessid = get_setcookie(res_2)
        conn.close()

    @output_time
    def login(self):
        # 登陆
        # username = ''
        # password = ''
        # headers_3 = generate_headers(key_cookies + ';' + phpsessid)
        #
        # payload = "username=team021&password=team021s&" + group_id
        # headers_2 = generate_headers(key_cookies + ';' + phpsessid)
        # conn.request('POST', '/user/login_ok', payload, headers_3)
        # res_3 = conn.getresponse()
        # print(res_3.read().decode('ISO-8859-15'))
        # conn.close()
        self.url_3 = 'http://zb.mangsou.com/user/login_ok'
        payload = "username=%s&password=%s&%s" % (self.username, self.password, self.group_id)
        self.headers_3 = generate_headers()
        self.headers_3['Content-Type'] = "application/x-www-form-urlencoded"
        self.headers_3['Content-Length'] = "77"
        self.cookies_3 = generate_cookies(self.key_cookies + ';' + self.phpsessid)
        self.ultimate_cookies = self.cookies_3
        self.ultimate_headers = generate_headers()

        res_3 = requests.request('POST', self.url_3, data=payload, headers=self.headers_3, cookies=self.cookies_3)
        res_text = res_3.text
        if 'group_id' in res_text:
            return True
        else:
            return False
    @output_time

    # 返回撰写和推广的可选项
    def get_index(self):
        url_index = 'http://zb.mangsou.com/?' + self.group_id
        res_4 = requests.get(url_index, headers=self.ultimate_cookies, cookies=self.ultimate_cookies)
        soup = BeautifulSoup(res_4.content, 'html.parser')
        div_tasks = soup.select('div.writing_task')
        zhuanxie_index = div_tasks[0].select('ul li a')
        tuiguang_index = div_tasks[1].select('ul li a')
        zhuanxie_options = []
        tuiguang_options = []

        for x in zhuanxie_index:
            name = x.select('div.task_list h3 em')[0].string
            href = x.get('href')
            zhuanxie_options.append([name, href])

        for x in tuiguang_index:
            name = x.select('div.task_list h3 em')[0].string
            href = x.get('href')
            tuiguang_options.append([name, href])

        return [zhuanxie_options, tuiguang_options]
    @output_time

    def accept_task(self,task):
        headers = {
            'Accept': "application/json, text/javascript, */*; q=0.01",
            'Accept-Encoding': "gzip, deflate",
            'Accept-Language': "zh-CN,zh;q=0.9",
            'Connection': "keep-alive",
            'Content-Type': "application/x-www-form-urlencoded",
            'Host': "zb.mangsou.com",
            'Origin': "http://zb.mangsou.com",
            'Referer': "http://zb.mangsou.com/taskrelease?name=%E5%8F%91%E5%B8%83%E7%B1%BB%EF%BC%88%E4%B8%80%E5%AF%B9%E4%B8%80%EF%BC%89&g_id=93",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36",
            'X-Requested-With': "XMLHttpRequest",
        }

        # headers = self.ultimate_headers
        # headers['Content-Type'] = 'application/x-www-form-urlencoded'
        # headers['X-Requested-With'] = 'XMLHttpRequest'

        if task['index_type'] == '3':
            url = 'http://zb.mangsou.com/taskreleaseto/get_task'
            # task_dw = task
            # task_dw.pop('price')
            # task_dw.pop('title')
            # print(task_dw)
            # payload =  "order_id=%s&task_type=%s&uid=%s&group_id=%s" % (task['order_id'],task['task_type'], task['uid'], task['group_id'])
            payload = "order_id=%s&task_type=%s&uid=%s&group_id=%s" % (task['order_id'], task['task_type'], task['uid'], task['group_id'])
        elif task['index_type'] == '2':
            url = 'http://zb.mangsou.com/taskrelease/get_task'
            payload = "task_id=%s&task_type=%s&uid=%s&r_url=%s" % (task['task_id'], task['task_type'], task['uid'], task['r_url'])
            headers['Accept'] = "application/json, text/javascript, */*; q=0.01"
        elif task['index_type'] == '3a':
            url = 'http://zb.mangsou.com/taskreleaseto/get_tasks'
            payload = "order_id=%s&task_type=%s&uid=%s&group_id=%s" % (task['order_id'], task['task_type'], task['uid'], task['group_id'])


        # elif task['index_type'] == '1':
        # payload = 'task_type=%s&task_id=%s&uid=%s&r_url=%s' % (task['task_type'], task['task_id'], task['uid'], task['r_url'])

        # post_headers['Content-Type'] = "application/x-www-form-urlencoded"
        # post_headers['X-Requested-With'] = 'XMLHttpRequest'
        res = requests.request('POST', url, data=payload, headers=headers, cookies=self.ultimate_cookies)
        res_json = json.loads(res.text)
        return res_json
    @output_time

    def get_money(self):
        url = 'http://zb.mangsou.com/user/get_api_money'
        res = requests.request('GET', url, headers=self.ultimate_headers, cookies=self.ultimate_cookies)
        money = json.loads(res.text)
        return money
    @output_time

    def get_static(self, href):
        if href == 'taskrelease?name=发布类（一对一）&g_id=93':
            index_type = '2'
        elif href == 'taskreleaseto?name=发布类（一对多）&g_id=94':
            index_type = '3'
        elif href == 'taskwrite?name=撰写类&g_id=45':
            index_type = '1'
        else:
            return 'error'
        url = 'http://zb.mangsou.com/' + href
        res = requests.request('GET', url, headers=self.ultimate_headers, cookies=self.ultimate_cookies)
        soup = BeautifulSoup(res.content, 'html.parser')
        pages = soup.select('ul.fl li a')

        page_num = int(pages[-1].string)
        # tasks = []
        # page_num = 1
        tasks = self.get_tasks(soup, index_type)
        return [tasks, page_num,index_type]
        # if page_num <= 1 :
        #     tasks.append(self.get_tasks(soup,index_type))
        # else:
        #     tasks.append(self.get_tasks(soup,index_type))
        #     #开始读取第二页以上的内容
        #     pages = range(2, page_num+1)
        #     for x in pages:
        #         url_page = 'http://zb.mangsou.com/%s&p=%s' % (href, x)
        #         res_page = requests.request('GET', url_page, headers=self.ultimate_headers, cookies=self.ultimate_cookies)
        #         soup_page = BeautifulSoup(res_page.content, 'html.parser')
        #         tasks.append(self.get_tasks(soup_page, task_type))
        # return tasks
    @output_time

    def get_tasks(self, soup, index_type):
        # 价格、标题、发布时间、剩余时间、要求、任务编号、发布频道
        tasks_dict = []
        soup_tasks = soup.select('tr.sear_bo_shade')
        # print(soup_tasks)
        # i = 1
        for x in soup_tasks:
            if index_type == '3' or index_type == '3a':
                counts = x.select('td div p span')
                ar_counts = int(counts[0].string)
                counts = int(counts[1].string)
                can_counts = counts - ar_counts

                s_price = float(x.select('td span')[0].string[1:])
                price = s_price * counts
                can_price = s_price * can_counts
                pindao = x.select('ul.result_com li a')
                if len(pindao) >= 1:
                    pindao = pindao[0].get('href')
                else:
                    pindao = ''
            elif index_type == '2':
                price = x.select('td span')[0].string[1:]
                pindao = x.select('ul.result_com li')
                if len(pindao) >= 1:
                    pindao = pindao[2].get_text()
                else:
                    pindao = ''

            title = x.select('td div h2')[0].string
            ids = x.select('td div a.task_btn')
            if len(ids) > 1:
                index_type = '3a'
            id = ids[0].get('onclick')[11:-1]

            id_list = id.split(',')
            if index_type == '1':
                order_id = id_list[0]
                type = id_list[1]
                uid = id_list[2]
                tasks_dict.append({'pindao':pindao,'price': price, 'title': title, 'order_id': order_id, 'task_type': type, 'uid': uid, 'index_type': index_type})
            elif index_type == '2':
                task_id = id_list[0]
                type = id_list[1]
                uid = id_list[2]
                r_url = id_list[3][1:-1]
                tasks_dict.append({'pindao':pindao,'price': price, 'title': title, 'task_id': task_id, 'task_type': type, 'uid': uid, 'r_url': r_url, 'index_type': index_type})
            elif index_type == '3' or index_type == '3a':
                order_id = id_list[0]
                type = id_list[1]
                uid = id_list[2]
                gp_id = id_list[3][1:-1]
                tasks_dict.append({'can_price':can_price,'can_counts':can_counts,'ar_counts': ar_counts,'s_price': s_price, 'counts': counts, 'pindao':pindao, 'price': price, 'title': title, 'order_id': order_id, 'task_type': type, 'uid': uid, 'group_id': gp_id, 'index_type': index_type})
        return tasks_dict
    @output_time

    def tasks_filter_accept(self,tasks,s,c,p):

        i = {'yes':0, 'no':0}
        match_list = []
        with open('pindao_keywords.txt', 'r') as file:
            while True:
                line = file.readline()
                if not line:
                    break
                match_list.append(line.strip('\n'))
        if len(match_list) < 1:
            print('【警告】在pindao_keywords.txt文件中未发现相关数据，请补充！')
        if len(tasks) >= 1:
            # print(x['pindao'])
            # find_tasks = [x for x in tasks if 'qq.com' in x['pindao'] or '163.com' in x['pindao'] or 'toutiao.com' in x['pindao']]
            tasks = sorted(tasks, key=itemgetter('can_price'), reverse=True)
            for x in tasks:
                # print(x['price'], x['counts'])
                # 从这里开始匹配频道链接
                pindao = x['pindao']
                for y in match_list:
                    if y in pindao:
                        index_type = x['index_type']
                        if index_type == '3' or index_type == '3a':
                            counts = x['counts']
                            s_price = x['s_price']
                            price = x['price']
                            print('【★重要★】',x['can_counts'], counts , c[0],c[1])
                            if counts >= c[0] and counts <= c[1] and s_price >= s[0] and s_price <= s[1] and price >= p[0] and price <= p[1]:

                                res = self.accept_task(x)
                                output_log('%s 单价：%s ，数量：%s' % (res['msg'], s_price, counts))
                                if '领取成功' in res['msg']:
                                    i['yes'] += 1
                                else:
                                    i['no'] += 1
                                break
                            else:
                                break

                        else:
                            res = self.accept_task(x)
                            output_log('%s 普通任务' % res['msg'])
                            if '领取成功' in res['msg']:
                                i['yes'] += 1
                            else:
                                i['no'] += 1
                            break
                # 从这里开始匹配其他的

            return i
        else:
            return i

    def logout(self):
        url_logout = 'http://zb.mangsou.com/user/signout?' + self.group_id
        res = requests.request('GET', url_logout, headers=self.ultimate_headers, cookies=self.ultimate_cookies)
        return res.text

# test
def test_accept_task():
    a = User('team021', 'team021s')
    a.login()
    index = a.get_index()
    href = index[0][1][1]
    tasks = a.get_static(href)
    for n in tasks:
        for x in n:
            print(x['title'], x['price'],x['task_id'])
    i = input()
    # print(tasks[0][int(i)])
    res = a.accept_task(tasks[0][int(i)])
    print(res)
    a.logout()


# def test_time():
#     user = User('team021', 'team021s')
#     print('准备登陆...')
#     print(user.login())
#
#     page = requests.get('http://zb.mangsou.com/taskrelease?name=%E5%8F%91%E5%B8%83%E7%B1%BB%EF%BC%88%E4%B8%80%E5%AF%B9%E4%B8%80%EF%BC%89&g_id=93')
#     soup = BeautifulSoup(page.content)
#     user.get_tasks(soup,'2')
#
#     test_time()



# 抓取
# cookies = headers_3.pop('Cookie')
# a = cookies.split(';')
# cookies = {}
# for x in a:
#     y = x.split('=')
#     if y[0] == 'path':
#         continue
#     cookies[y[0]] = y[1]

