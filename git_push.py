import sys
import subprocess
import platform

def execute_git_commands(commit_message):
    try:
        # 新增代理配置
        subprocess.run(['git', 'config', '--global', 'http.proxy', 'http://127.0.0.1:7890'], check=True)
        subprocess.run(['git', 'config', '--global', 'https.proxy', 'http://127.0.0.1:7890'], check=True)
        
        # 执行 git add . 命令
        subprocess.run(['git', 'add', '.'], check=True)
        # 执行 git commit -m "commit_message" 命令
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        # 执行 git push 命令
        subprocess.run(['git', 'push'], check=True)
        print("代码推送成功！")
    except subprocess.CalledProcessError as e:
        print(f"代码推送失败: {e}，请检查网络或仓库状态。")

if __name__ == "__main__":
    # 检查是否提供了 commit 信息
    if len(sys.argv) < 2:
        print("请提供 commit 信息作为参数，例如: python script.py '更新代码'")
        sys.exit(1)

    # 获取 commit 信息
    commit_message = sys.argv[1]

    # 判断当前操作系统
    current_platform = platform.system()
    if current_platform in ['Windows', 'Linux', 'Darwin']:
        execute_git_commands(commit_message)
    else:
        print(f"不支持的操作系统: {current_platform}")