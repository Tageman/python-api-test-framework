#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import argparse
from datetime import datetime

def ensure_dir(directory):
    """确保目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def run_tests(env=None, markers=None, report_path=None):
    """
    运行测试
    
    Args:
        env: 环境名称，如dev/test/prod
        markers: pytest标记筛选，如smoke/api
        report_path: 报告输出路径
    """
    # 设置环境变量（如果指定）
    if env:
        # 更新config.yaml中的env值
        with open("config/config.yaml", "r", encoding="utf-8") as f:
            config_content = f.read()
        
        # 替换环境配置行
        import re
        new_content = re.sub(r'env:\s+"[^"]+"', f'env: "{env}"', config_content)
        new_content = re.sub(r"env:\s+'[^']+'", f'env: "{env}"', new_content)
        new_content = re.sub(r"env:\s+\w+", f'env: "{env}"', new_content)
        
        with open("config/config.yaml", "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print(f"已设置测试环境为: {env}")
    
    # 确保报告目录存在
    if report_path:
        ensure_dir(report_path)
        allure_results = os.path.join(report_path, "allure-results")
    else:
        ensure_dir("reports")
        allure_results = "reports/allure-results"
    
    ensure_dir(allure_results)
    
    # 构建pytest命令
    cmd = ["pytest"]
    
    # 添加markers过滤
    if markers:
        cmd.append(f"-m {markers}")
    
    # 添加报告输出路径
    cmd.append(f"--alluredir={allure_results}")
    
    # 运行测试
    print("开始运行测试...")
    subprocess.run(" ".join(cmd), shell=True)
    
    # 生成Allure报告
    print("生成Allure报告...")
    allure_report = os.path.join(os.path.dirname(allure_results), "allure-report")
    ensure_dir(allure_report)
    
    try:
        # 尝试使用allure命令生成报告
        allure_cmd = f"allure generate {allure_results} -o {allure_report} --clean"
        result = subprocess.run(allure_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("警告: Allure命令行工具未安装或无法运行，无法生成报告。")
            print("请访问 https://docs.qameta.io/allure/ 了解如何安装Allure命令行工具。")
            print(f"测试结果已保存到 {allure_results}，安装Allure后可手动生成报告。")
        else:
            print(f"Allure报告已生成: {allure_report}")
            # 尝试打开报告
            open_report_cmd = f"allure open {allure_report}"
            try:
                subprocess.Popen(open_report_cmd, shell=True)
                print("已打开Allure报告。")
            except:
                print(f"无法自动打开报告，请手动打开: {allure_report}")
    except Exception as e:
        print(f"生成Allure报告时出错: {str(e)}")
        print(f"测试结果已保存到 {allure_results}，可以手动生成报告。")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="运行API自动化测试")
    parser.add_argument("--env", choices=["dev", "test", "prod"], 
                        help="指定测试环境: dev/test/prod", default=None)
    parser.add_argument("--markers", help="指定测试标记，如'smoke'或'api'", default=None)
    parser.add_argument("--report-path", help="指定报告输出路径", default=None)
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    run_tests(env=args.env, markers=args.markers, report_path=args.report_path) 