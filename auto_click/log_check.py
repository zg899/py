import argparse
import re

def analyze_log(log_path):
    try:
        # 尝试使用不同的编码读取文件
        try:
            with open(log_path, 'r', encoding='utf-8') as file:
                content = file.readlines()
        except UnicodeDecodeError:
            with open(log_path, 'r', encoding='latin-1') as file:
                content = file.readlines()
        
        # 初始化数据结构
        start_times = []
        end_times = []
        cycle_times = []
        clicks_found = 0
        clicks_success = 0
        clicks_failed = 0
        not_found_errors = 0
        consecutive_not_found = 0
        max_chromium_processes = 0
        last_chromium_processes = 0
        max_current_chromium = 0
        last_current_chromium = 0
        
        # 正则表达式匹配
        start_pattern = r"main try开始时间: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
        end_pattern = r"main完整结束时: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
        cycle_pattern = r"一个循环所需时间：(\d+\.\d+)秒。"
        found_click_pattern = r"发现 \d+ 即将点击"
        success_click_pattern = r"点击按钮成功！"
        failed_click_pattern = r"点击按钮失败"
        not_found_pattern = r"在指定时间内未找到元素或页面未完全加载。"
        chromium_processes_pattern = r"Found (\d+) Chromium processes running."
        current_chromium_pattern = r"当前运行chromium: (\d+)"
        
        for line in content:
            if re.search(start_pattern, line):
                start_times.append(re.search(start_pattern, line).group(1))
            if re.search(end_pattern, line):
                end_times.append(re.search(end_pattern, line).group(1))
            if re.search(cycle_pattern, line):
                cycle = float(re.search(cycle_pattern, line).group(1))
                cycle_times.append(cycle)
            if re.search(found_click_pattern, line):
                clicks_found += 1
            if re.search(success_click_pattern, line):
                clicks_success += 1
            if re.search(failed_click_pattern, line):
                clicks_failed += 1
            if re.search(not_found_pattern, line):
                not_found_errors += 1
                consecutive_not_found += 1
                if consecutive_not_found == 3:
                    print("警告！警告！连续三次未找到元素或页面未完全加载。")
            else:
                consecutive_not_found = 0
            if match := re.search(chromium_processes_pattern, line):
                chromium_processes = int(match.group(1))
                max_chromium_processes = max(max_chromium_processes, chromium_processes)
                last_chromium_processes = chromium_processes
            if match := re.search(current_chromium_pattern, line):
                current_chromium = int(match.group(1))
                max_current_chromium = max(max_current_chromium, current_chromium)
                last_current_chromium = current_chromium
        
        # 输出结果
        print(f"Main try开始次数: {len(start_times)}, 最早 {min(start_times) if start_times else 'N/A'}, 最晚 {max(start_times) if start_times else 'N/A'}")
        print(f"Main完整结束次数: {len(end_times)}, 最早 {min(end_times) if end_times else 'N/A'}, 最晚 {max(end_times) if end_times else 'N/A'}")
        print(f"一个循环所需时间次数: {len(cycle_times)}, 最少 {min(cycle_times) if cycle_times else 'N/A'}, 最大 {max(cycle_times) if cycle_times else 'N/A'}, 平均耗时 {sum(cycle_times)/len(cycle_times) if cycle_times else 'N/A'}")
        print(f"发现即将点击次数: {clicks_found}")
        print(f"点击按钮成功次数: {clicks_success}")
        print(f"点击按钮失败次数: {clicks_failed}")
        print(f"未找到元素或页面未完全加载次数: {not_found_errors}")
        print(f"Found Chromium processes running: 最大次数 {max_chromium_processes}, 最后一次记录的次数 {last_chromium_processes}")
        print(f"当前运行chromium: 最大次数 {max_current_chromium}, 最后一次记录的次数 {last_current_chromium}")
    
    except FileNotFoundError:
        print(f"No such file: {log_path}")

def main():
    # 创建ArgumentParser对象
    parser = argparse.ArgumentParser(description='Analyze log file')
    
    # 添加命令行参数
    parser.add_argument('logfile', type=str, help='Path to the log file')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 调用日志分析函数
    analyze_log(args.logfile)

if __name__ == '__main__':
    main()
