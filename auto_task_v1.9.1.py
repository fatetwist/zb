import time
import auto as zb
from configparser import ConfigParser
import os
from threading import Thread,Lock,current_thread
import requests
from bs4 import BeautifulSoup





def login_input():
    username = input('输入用户名：')
    password = input('输入密码：')
    user.username = username
    user.password = password


    if user.login() == True:
        print('登陆成功！')
        remember = input('是否记住账号密码？是Y/否N')
        if remember == 'Y' or 'y':
            # mknod = open('key_info.cfg', 'w')
            # # mknod.write('[user]\n')
            # # mknod.write('username=\n')
            # # mknod.write('password=\n')
            # mknod.close()
            with open('key_info.cfg', 'w') as cfgfile:
                config.add_section('user')
                config.set('user', 'username', username)
                config.set('user', 'password', password)
                config.write(cfgfile)
            # config.write('key_info.cfg')
            # config.set('user','username', username)
            # config.set('user','password', password)

    else:
        print('账号或密码错误！')
        login_input()


def login_remember():
    if user.login() == True:
        print('使用已保存的账号密码登陆成功！')
    else:
        print('账号已经过期，请重新登陆！')
        login_input()




def static_async(href,thr_num):
    while True:
        page_static = user.get_static(href)
        tasks_first_page = page_static[0]
        page_num = page_static[1]
        index_type = page_static[2]

        page_num_before = flash_global['page_num']
        flash_global['href'] = href
        flash_global['page_num'] = page_num
        flash_global['tasks_first_page'] = tasks_first_page
        flash_global['static_times'] += 1
        static_times = flash_global['static_times']
        print('【目录监控中】 已经进行%s次 , 当前目录有%s页' % (static_times, page_num))
        if static_times == 1 or page_num_before != page_num:
            for n in range(thr_num):
                flash_global[n] = {'times': {}}
                for x in range(page_num):
                    thr = Thread(target=tasks_async, args=(n, x, page_num, href, index_type,))
                    thr.start()
        time.sleep(5)


def tasks_async(n,m,page_num,href,index_type):
    while True:
        try:
            if flash_global['page_num'] != page_num:
                break
            try:
                flash_global[n]['times'][m] += 1
                ar_time = flash_global[n]['times'][m]
            except KeyError:
                flash_global[n]['times'][m] = 1
                ar_time = flash_global[n]['times'][m]
            if ar_time == 1:
                tasks = flash_global['tasks_first_page']
                res_accept = user.tasks_filter_accept(tasks,[0,99999],[0,99999],[0,99999])
            else:
                url = 'http://123.56.66.102/%s&p=%s' % (href, m+1)
                res = requests.request('GET', url, headers=user.ultimate_headers, cookies=user.ultimate_cookies)
                soup = BeautifulSoup(res.content, 'html.parser')
                tasks = user.get_tasks(soup, index_type)
                res_accept = user.tasks_filter_accept(tasks,[0,99999.999],[0,99999],[0,99999])
            print('【页面线程%s-%s】正在进行中，获取到%s个任务，已经进行%s次搜寻' % (n+1, m+1, len(tasks), ar_time), res_accept)
        except BaseException as e:
            print('【错误】本次搜寻出了点错误哦，已经重启线程。%s ' % e)


def start(thr_num):
    # for x in range(thr_num):
    #     flash_global[x] = {'times':{}}
    print('【全部】正在部署线程...')
    thr = Thread(target=static_async, args=(href, thr_num,))
    thr.start()
    print('【全部】线程部署完毕！已经安排任务，正在等待网页响应...')

def start_2(thr_num):
    print('正在部署线程...')
    for n in range(thr_num):
        flash_global[n] = {'times':0}
        thr = Thread(target=get_tasks_async_2, args=(n,))
        thr.start()
    print('线程部署完毕!')


def get_tasks_async_2(n):
    while True:
        try:
            t1 = time.time()
            spec_url = 'http://123.56.66.102/taskreleaseto/index?name=发布类（一对多）&orderby=3&task_status=1&group_id=0&g_id=&t=1515896378214%s214' % time.time()
            res_content = requests.request('GET', spec_url, headers=user.ultimate_headers, cookies=user.ultimate_cookies).content
            spec_soup = BeautifulSoup(res_content, 'html.parser')
            tasks = user.get_tasks(spec_soup, '3')
            t2 = time.time()
            print('[耗时]访问网页',t2-t1)
            result = user.tasks_filter_accept(tasks,s_price_round,counts_round,price_round)
            flash_global[n]['times'] += 1
            ar_times = flash_global[n]['times']

            print('【线程%s】已经完成%s次搜寻!此次发现了%s个任务，结果：' % (n+1,ar_times,len(tasks)), result)
        except BaseException:
            print('【线程%s】出了点错误哟，已经重启线程' % str(n+1))





if __name__ == '__main__':
    import win_unicode_console
    win_unicode_console.enable()


    print('=====================正在准备开始=====================')

    res_validator = requests.get('http://120.79.9.56/validator.html')
    t = res_validator.text.strip()
    if t != 'yes':
        print('程序错误！！即将退出！！')
    else:


        config = ConfigParser()
        config.read('key_info.cfg')
        user = zb.User('', '')

        try:
            user.username = config.get('user', 'username')
            user.password = config.get('user', 'password')
            login_remember()
        except BaseException:
            login_input()

        print('======================选择类型=========================')
        print('索引：')
        print('1、撰写类')
        print('2、发布类（一对一）')
        print('3、发布类（一对多）')
        print('======================================================')
        index = '3'
        if index == '1':
            href = 'taskwrite?name=撰写类&g_id=45'
        elif index == '2':
            href = 'taskrelease?name=发布类（一对一）&g_id=93'
        elif index == '3':
            href = 'taskreleaseto?name=发布类（一对多）&g_id=94'
        else:
            index = '3'
            href = 'taskreleaseto?name=发布类（一对多）&g_id=94'
        print('你选择的是：%s' % index)
        print('=====================选择模式===========================')
        print('1、全局监控模式')
        print('2、死盯价格最高页面模式')
        print('=======================================================')
        mode = '2'
        if mode != '1' and mode != '2':
            mode = '2'
            print('您的输入有误，默认选择：2')
        print('你选择的是：%s' % mode)

        if mode == '1':
            flash_global = {'page_num': 0, 'static_times': 0}
            lock = Lock()
            thr_num = input('请输入线程倍数：')
            if thr_num.isdigit():
                thr_num = int(thr_num)
            else:
                print('输入有误！已默认为您安排3个线程。')
                thr_num = 3
            start(thr_num)  # 用这个函数来布置线程

        else:

            flash_global = {}

            try:
                s_price_round = config.get('round', 's_price_round')
                counts_round = config.get('round', 'counts_round')
                price_round = config.get('round', 'price_round')
            except BaseException:
                print('======开始输入范围信息，格式千万不能错哦！======')
                s_price_round = input('输入单价范围（格式：最小值-最大值）：')
                counts_round = input('输入数量范围（格式：最小值-最大值）：')
                price_round = input('输入总价范围（格式：最小值-最大值）：')
                with open('key_info.cfg', 'w') as cfgfile:
                    config.add_section('round')
                    config.set('round', 's_price_round', s_price_round)
                    config.set('round', 'counts_round', counts_round)
                    config.set('round', 'price_round', price_round)
                    config.write(cfgfile)

            print(s_price_round, counts_round, price_round)
            try:
                s_price_round = [float(x) for x in s_price_round.split('-')]
                counts_round = [float(x) for x in counts_round.split('-')]
                price_round = [float(x) for x in price_round.split('-')]

                print('[成功] 系统已经接受范围信息(已记住,如果重新输入请修改目录文件key_info.cfg)：单价%s~%s,数量%s~%s,总价%s~%s' % (s_price_round[0],s_price_round[1],counts_round[0],counts_round[1],price_round[0],price_round[1]))
            except:
                print('[警告] 格式输入错误! 3秒后退出程序!')
                time.sleep(3)
                exit(0)
            thr_num = '3'
            if thr_num.isdigit():
                thr_num = int(thr_num)
            else:
                print('输入有误！已默认为您安排3个线程。')
                thr_num = 3
            start_2(thr_num)

