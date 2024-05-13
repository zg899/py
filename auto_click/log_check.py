import re

# 日志文件路径
log_path = 'nohup.out'

def analyze_log(log_path):
    try:
        with open(log_path, 'r') as file:
            content = file.readlines()
        
        # 初始化数据结构
        start_times = []
        end_times = []
        cycle_times = []
        clicks_found = 0
        clicks_success = 0
        clicks_failed = 0
        not_found_errors = 0
        
        # 正则表达式匹配
        start_pattern = r"main try开始时间: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
        end_pattern = r"main完整结束时: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
        cycle_pattern = r"一个循环所需时间：(\d+\.\d+)秒。"
        found_click_pattern = r"发现 \d+ 即将点击"
        success_click_pattern = r"点击按钮成功！"
        failed_click_pattern = r"点击按钮失败"
        not_found_pattern = r"在指定时间内未找到元素或页面未完全加载。"
        
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
        
        # 输出结果
        print(f"Main try开始次数: {len(start_times)}, 最早 {min(start_times) if start_times else 'N/A'}, 最晚 {max(start_times) if start_times else 'N/A'}")
        print(f"Main完整结束次数: {len(end_times)}, 最早 {min(end_times) if end_times else 'N/A'}, 最晚 {max(end_times) if end_times else 'N/A'}")
        print(f"一个循环所需时间次数: {len(cycle_times)}, 最少 {min(cycle_times) if cycle_times else 'N/A'}, 最大 {max(cycle_times) if cycle_times else 'N/A'}, 平均耗时 {sum(cycle_times)/len(cycle_times) if cycle_times else 'N/A'}")
        print(f"发现即将点击次数: {clicks_found}")
        print(f"点击按钮成功次数: {clicks_success}")
        print(f"点击按钮失败次数: {clicks_failed}")
        print(f"未找到元素或页面未完全加载次数: {not_found_errors}")
    
    except FileNotFoundError:
        print(f"No such file: {log_path}")

# 调用函数
analyze_log(log_path)
