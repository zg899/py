# executablePath=r'C:\Users\gang\AppData\Local\Chromium\Application\chrome.exe',

import asyncio
from pyppeteer import launch
from pyppeteer.errors import TimeoutError, PageError, NetworkError
from pyppeteer import errors as pyppeteer_errors

from fake_useragent import UserAgent
import random
import datetime
import uuid
import tempfile
import shutil
import string  # 确保这行被添加
import urllib.parse
import time
import aiohttp  # 假设使用 aiohttp 进行异步HTTP请求
import os
from time import sleep


# 定义一组PC浏览器的用户代理字符串
pc_user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    # 添加更多PC浏览器的用户代理字符串...
]


'''
url_1 = "https://www.agoda.com/ja-jp/mimaru-tokyo-hatchobori/hotel/tokyo-jp.html?"  # 目标酒店
start_date = "2024-09-16" # 开始日期
num_days = 30 # 连续确认天数
los_num = 1 # 连住天数
adults_num = 2 # 成人数量
'''
txt_file_name = "D_1.txt" # 有效地址

# 异步等待并打印倒计时
async def async_countdown(message, seconds):
    print(f"{message} 等待时间 {seconds} 秒。")
    while seconds:
        print(f"剩余等待时间: {seconds} 秒", end='\r')
        await asyncio.sleep(1)
        seconds -= 1
    print()
    

# 创建 tag 
def generate_tag():
    # 生成一个随机的UUID
    tag = uuid.uuid4()
    # 将UUID转换为字符串
    return str(tag)
    
    
# 生成随机时间的函数
def generate_random_time(min_seconds, max_seconds):
    return random.randint(min_seconds, max_seconds)
    
#创建 7位数字 cid
def generate_random_seven_digit_number():
    # 生成一个范围在1000000(含)到9999999(含)之间的随机整数
    return random.randint(1821104, 1944904)

# 使用函数
random_number = generate_random_seven_digit_number()

# 创建随机sessionid
def generate_search_request_id():
    # 生成一个随机的UUID
    search_request_id = uuid.uuid4()
    # 转换为字符串并返回
    return search_request_id

# 使用函数
random_search_request_id = generate_search_request_id()

# 随机创建 ds 
def generate_random_ds_param(length=16):
    # 生成随机字符串，包含大小写字母和数字
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    # URL编码，这里以加号+为例，根据实际需求可能需要调整
    encoded_str = urllib.parse.quote_plus(random_str)
    return encoded_str

# 从txt文件读取URL列表
'''
def read_urls_from_file():
    try:
        with open(txt_file_name, "r") as file:
            urls = file.read().splitlines()
        return urls
    except FileNotFoundError:
        return []
'''
def read_urls_from_file(file_name):
    try:
        with open(file_name, "r") as file:
            urls = file.read().splitlines()
        return urls
    except FileNotFoundError:
        return []

# 更新或移除在txt文件中的URL

def update_find_file(found, current_url):
    filename = txt_file_name
    try:
        with open(filename, "r+") as file:
            lines = file.read().splitlines()
            # 解析并比较 URL 中的 checkin 日期和 cid 参数
            current_params = {param.split('=')[0]: param.split('=')[1] for param in current_url.split('?')[1].split('&') if param.split('=')[0] in ['checkIn', 'cid']}
            should_add = True  # 默认情况下，添加当前 URL
            for line in lines:
                existing_params = {param.split('=')[0]: param.split('=')[1] for param in line.split('?')[1].split('&') if param.split('=')[0] in ['checkIn', 'cid']}
                # 如果找到一个现有的 URL 与当前 URL 的 checkin 日期和 cid 都相同，则不添加当前 URL
                if existing_params == current_params:
                    should_add = False
                    print(f"相似的 URL 已存在，未添加 {current_url}")
                    break  # 找到匹配项后退出循环
            if should_add and found:
                file.write(f"{current_url}\n")
                print(f"URL {current_url} 已添加到文件 {filename}。")
            elif not found:
                print(f"这次查询没找到 28043！但是地址还保留着")
    except FileNotFoundError:
        # 如果文件不存在并且发现了元素，创建文件并添加 URL
        if found:
            with open(filename, "w") as file:
                file.write(f"{current_url}\n")
                print(f"文件 {filename} 已创建并添加了URL {current_url}。")


# 生成URL列表
def generate_urls(base_url, start_date, num_days, los_num, adults_num):
    
    urls = []  # 初始化URL列表
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    print(f"计划任务：从 {start_date.strftime('%Y-%m-%d')} 开始，跑到 {(start_date + datetime.timedelta(days=num_days - 1)).strftime('%Y-%m-%d')}。")
    
    for day in range(num_days):
        date = start_date + datetime.timedelta(days=day)
        date_str = date.strftime("%Y-%m-%d")
        cid = generate_random_seven_digit_number()  # 对于每个URL，生成新的CID
        search_request_id = generate_search_request_id()  # 对于每个URL，生成新的searchrequestid
        tag = generate_tag()  # 生成新的tag
        ds = generate_random_ds_param()  # 生成随机的ds参数

        # 拼接URL
        url = (f"{base_url}finalPriceView=2&isShowMobileAppPrice=false&cid={cid}&numberOfBedrooms=&familyMode=false&"
               f"adults={adults_num}&children=0&rooms=1&maxRooms=0&checkIn={date_str}&isCalendarCallout=false&"
               f"childAges=&numberOfGuest=0&missingChildAges=false&travellerType=1&showReviewSubmissionEntry=false&"
               f"currencyCode=JPY&isFreeOccSearch=false&tag={tag}&isCityHaveAsq=false&los={los_num}&"
               f"searchrequestid={search_request_id}&ds={ds}")
        urls.append(url)  # 将生成的URL添加到列表中

    return urls  # 循环结束后返回整个URL列表
    
# 模拟滚动到页面底部
async def slow_scroll_to_bottom(page):
    await page.evaluate('''async () => {
        await new Promise((resolve, reject) => {
            var totalHeight = 0;
            var distance = 100;
            var timer = setInterval(() => {
                var scrollHeight = document.body.scrollHeight;
                window.scrollBy(0, distance);
                totalHeight += distance;

                if(totalHeight >= scrollHeight){
                    clearInterval(timer);
                    resolve();
                }
            }, 100);
        });
    }''')
    # 等待一段时间以确保滚动操作完成
    await page.waitFor(12000)  # 请确保这里使用的是 pyppeteer 支持的方法
    
# 使用代理服务器访问并操作指定URL的异步函数
async def visit_and_operate_url(url, proxy_host, proxy_port, proxy_user, proxy_pass, browser):
        start_time = datetime.datetime.now()
        print(f"v函数开始时间：{start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("开启 visit_and_operate_url函数")
        print(f"本次使用文件：{txt_file_name}") 
        button_found = False  # 初始化按钮发现状态
  
        # 定义等待时间
        found_button_wait_time = generate_random_time(10,20)  # 发现按钮后的等待时间（秒）
        not_found_button_wait_time = generate_random_time(10,20)  # 未发现按钮时的等待时间（秒）
        
        page = await browser.newPage()
        
        # 设置代理认证
        await page.authenticate({'username': proxy_user, 'password': proxy_pass})
         # 设置英文请求头
        await page.setExtraHTTPHeaders({
            'Accept-Language': 'en-US,en;q=0.9'
        })
        
        # 过滤图片加载
        '''
        await page.setRequestInterception(True)
        async def intercept_request(req):
            if req.resourceType() in ['image', 'stylesheet']:
                await req.abort()
            else:
                await req.continue_()
    
        page.on('request', intercept_request)
        '''
        # 打印当前IP和请求头信息
        try:
            await page.goto('http://httpbin.org/ip', {'timeout': 60000})  # 修改这里
            ip_info = await page.evaluate('() => document.body.textContent')
            print(f"当前 IP: {ip_info}")

        except TimeoutError:
            print("展示IP页面加载超时, 继续执行后续操作")

        try:
            await page.goto('http://httpbin.org/headers', {'timeout': 60000})  # 修改这里
            headers_info = await page.evaluate('() => document.body.textContent')
            print("请求头：", headers_info)

        except TimeoutError:
            print("展示请求头页面加载超时，继续执行后续操作")

        # 记录任务开始时间
        print(f"v函数 try 开始时间：{start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        try:
            print(f"正在访问: {url}")
            await page.goto(url, {'timeout': 60000}) #60秒
            # 模拟页面滚动到底部
            print("开始滚动页面")
            await slow_scroll_to_bottom(page)
            print("滚动页面结束")
            
            # 等待随机时间
            wait_time = generate_random_time(10, 20)
            await async_countdown("完成滚动，开始随机等待", wait_time)

            # 尝试找到并点击指定按钮
            try:
                await page.waitForSelector('button[data-element-supplier-id="28043"]', timeout=48000) #等待48秒
                print("✿✿✿✿✿ 发现 28043 即将点击 ✿✿✿✿✿")
                # 等待随机时间
                await async_countdown("发现按钮，开始等待", generate_random_time(10, 20))
                await page.click('button[data-element-supplier-id="28043"]')
                await async_countdown("点击完成，开始等待", generate_random_time(10, 20))
                button_found = True
                print("按钮点击完成。")
                # 调用 update_find_file 函数更新文件
                update_find_file(True, url)
            except TimeoutError:
                print("在指定时间内未找到元素或页面未完全加载。")
                # 调用 update_find_file 函数，表示没有找到按钮
                update_find_file(False, url)
                
            if button_found:  # 只有当button_found为True时才执行             
                try:
                # 在预定页面寻找 nextPage
                # 在新页面上等待特定元素出现
                    # 模拟页面滚动到底部
                    current_url = page.url
                    await async_countdown("到达booking Page", generate_random_time(10, 15))
                    print(f"当前URL : {current_url}")
                    
                    print("开始预定页面滚动")
                    await slow_scroll_to_bottom(page)
                    print("预定页面滚动结束")
                    await page.waitForSelector('button[data-action="nextPage"]', {'timeout': 48000}) #38秒
                    print("✿✿✿✿✿ 发现nextPage, 等待一下 ✿✿✿✿✿")
                    # 等待随机时间（10到20秒之间）
                    wait_time = random.randint(10, 20)
                    print(f"等待时间：{wait_time}秒。")
                    await asyncio.sleep(wait_time)
                except Exception as e:
                    print(f"点击后的页面错误: {e}")
                try:
                    print(f"发现后的等待，等待 {found_button_wait_time} 秒后进行下一次操作。")
                    await asyncio.sleep(found_button_wait_time)
                    print("发现按钮后的等待时间过后步骤")
                except TimeoutError:
                    print("在指定时间内未找到元素或页面未完全加载。")
            else:
                print(f"未发现按钮，等待 {not_found_button_wait_time} 秒后进行下一次操作。")
                await asyncio.sleep(not_found_button_wait_time)
        except Exception as e:
            print(f"未预料到的错误: {e}")
        finally:
            print("visit_and_operate_url 函数运行结束")
            # 结束任务
            end_time = datetime.datetime.now()
            duration = (end_time - start_time).total_seconds()
            print(f"v函数结束时间：{end_time.strftime('%Y-%m-%d %H:%M:%S')}，所需时间：{duration}秒。")
            # await page.close()  关闭page就出错
            print("虚拟关闭页面")

async def main_loop(proxy_host, proxy_port, proxy_user, proxy_pass):
    print("main 函数开始执行")
    #url_1 = "https://www.agoda.com/ja-jp/sunshine-city-prince-hotel-ikebukuro-tokyo/hotel/tokyo-jp.html?"
    #url_1 = "https://www.agoda.com/ja-jp/sunshine-city-prince-hotel-ikebukuro-tokyo/hotel/tokyo-jp.html?"
    #url_1 = "https://www.agoda.com/ko-kr/yufunogo-saigakukan/hotel/yufu-jp.html?"
    # url_1 ="https://www.agoda.com/hotel-oriental-express-fukuoka-nakasu-kawabata/hotel/fukuoka-jp.html?"
    # url_1 = "https://www.agoda.com/ja-jp/hotel-gracery-kyoto-sanjo/hotel/kyoto-jp.html?"
    # url_1 = "https://www.agoda.com/dormy-inn-premium-namba-natural-hot-spring/hotel/osaka-jp.html?"
    url_1 = "https://www.agoda.com/dormy-inn-maebashi-hot-spring/hotel/maebashi-jp.html?"
    
    start_date = "2024-11-02"  # 开始日期
    num_days = 1  # 连续确认天数
    los_num = 1  # 连住天数
    adults_num = 1  # 成人数量  
    while True:  # 无限循环，每次处理完所有URL后暂停一段时间再重新开始
        urls = read_urls_from_file(txt_file_name) or generate_urls(url_1, start_date, num_days, los_num, adults_num)
        for url in urls:
            try:
                start_time = datetime.datetime.now()
                print(f"main try开始时间：{start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print("main try开始执行")
                # 在函数内部选择随机用户代理
                random_pc_user_agent = random.choice(pc_user_agents)
                # 创建临时用户数据目录
                # temp_user_data_dir = tempfile.mkdtemp() # win11 用

                # 在 /tmp 目录下创建临时用户数据目录
                temp_user_data_dir = tempfile.mkdtemp(dir="/tmp") # Linux Debian 用
                print(f"创建的临时用户数据目录: {temp_user_data_dir}")
                # 构造代理地址字符串
                proxy_arg = f'--proxy-server={proxy_host}:{proxy_port}'
                
                browser = await launch(
                    #executablePath=r'C:\Users\gang\AppData\Local\Chromium\Application\chrome.exe', # win11用
                    executablePath=r'/usr/bin/chromium', # Linux用
                    args=[
                        proxy_arg,
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        f'--user-agent={random_pc_user_agent}', '--user-data-dir=' + temp_user_data_dir
                        ],
                        headless=True # 启用无头模式
                )
                
                await visit_and_operate_url(url, proxy_host, proxy_port, proxy_user, proxy_pass, browser)      
                print("main try 结束")
            except PageError as e:
                print(f"main 函数的页面错误: {e}")
                    # 对PageError进行处理
            except NetworkError as e:
                print(f"main 函数的网络错误: {e}")
                    # 对NetworkError进行处理
            except Exception as e:
                print(f"main 函数其他异常: {e}")
                    # 在这里，你可以添加日志记录或其他异常处理逻辑
            finally:         
                if browser:
                    await browser.close()
                    print("关闭浏览器,删除用户目录前25秒等待") 
                 # 删除临时用户数据目录
                try:
                    await asyncio.sleep(25)
                    shutil.rmtree(temp_user_data_dir)
                    print(f"已删除临时用户数据目录（之后25秒等待）: {temp_user_data_dir}")
                    await asyncio.sleep(25)
                except Exception as e:
                    print(f"删除临时目录时出现错误: {e}")
                    
            print("URL处理完成，准备下一轮...休息36秒")
            await asyncio.sleep(36)  # 休息66秒
               
        print("main 函数结束.再36秒后开始新的循环")
        await asyncio.sleep(36)  # 休息36秒
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"main完整结束时间：{end_time.strftime('%Y-%m-%d %H:%M:%S')}，一个循环所需时间：{duration}秒。")
    print("main 函数结束")     
if __name__ == "__main__":
    proxy_host = "brd.superproxy.io"
    proxy_port = "22225"
    proxy_user = "brd-customer-hl_827063fb-zone-scraping_browser"
    proxy_pass = "700xl6vfzhdx"
    asyncio.run(main_loop(proxy_host, proxy_port, proxy_user, proxy_pass))