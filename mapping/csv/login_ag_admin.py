
# 使用之前提供的用户名和密码替换这些占位符
# your_email = "l.yin@zhiyuanxing.com"
# your_password = "qwer@1234"

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import tempfile
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests

# 代理服务器地址
proxy = "http://127.0.0.1:24004"

# 创建临时用户数据目录
temp_user_data_dir = tempfile.mkdtemp()
    
# 配置Chrome选项
chrome_options = Options()
chrome_options.add_argument('--proxy-server={}'.format(proxy))
chrome_options.add_argument(f'--user-data-dir={temp_user_data_dir}')  # 使用临时用户数据目录
chrome_options.add_argument("--lang=en-US")
chrome_options.add_argument("--start-minimized")
    
# 创建WebDriver实例
with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) as driver:
   
# 获取当前IP地址
# 获取当前IP地址和请求头
    try:
        ip_response = requests.get('http://httpbin.org/ip', proxies={"http": proxy, "https": proxy})
        headers_response = requests.get('http://httpbin.org/headers', proxies={"http": proxy, "https": proxy})
            
        # 打印当前IP
        print(f"当前IP: {ip_response.json()['origin']}")

        # 打印请求头
        print("请求头：")
        headers = headers_response.json()['headers']
        for header, value in headers.items():
            print(f"{header}: {value}")

    except requests.RequestException as e:
        print(f"请求失败: {e}")

# 设置隐式等待时间
driver.implicitly_wait(10)  # 设置全局隐式等待10秒

try:
    # 打开Agoda供应商登录页面
    driver.get("https://supplypartners.agoda.com/login")

    # 使用显式等待来确保元素加载完成
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, "email")))
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, "password")))

    # 使用之前提供的用户名和密码替换这些占位符
    your_email = "l.yin@zhiyuanxing.com"
    your_password = "qwer@1234"

    # 找到邮箱和密码输入框，并输入登录信息
    driver.find_element(By.NAME, "email").send_keys(your_email)
    driver.find_element(By.NAME, "password").send_keys(your_password)

    # 点击登录按钮
    WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-cy="signin-button"]'))).click()

    # 根据需要进行后续操作...

except TimeoutException:
    # 出现超时异常，捕获当前页面截图
    driver.get_screenshot_as_file("timeout_exception.png")
    print("页面加载时间过长，或未能找到元素，已保存当前页面截图。")

finally:
    # 最后，关闭WebDriver
    driver.quit()


