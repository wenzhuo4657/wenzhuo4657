from github import Github
from github import Auth
from datetime import datetime, timedelta
import pytz
import os


# getlist(g)  获取需要的仓库列表
def getlist(g):
    all_repos = g.get_user().get_repos()
    # 排除个人简介仓库
    filtered_repos = [repo for repo in all_repos if repo.full_name != "wenzhuo4657/wenzhuo4657"]
    return filtered_repos


# get_commits_count(repo)  获取仓库最近一天的提交数量
def get_commits_count(repo):
    # 获取当前时间
    now = datetime.now(pytz.UTC)
    # 计算昨天的时间
    yesterday = now - timedelta(days=1)
    
    try:
        # 获取最近一天的提交
        commits = repo.get_commits(since=yesterday, until=now)
        return commits.totalCount
    except Exception as e:
        print(f"获取仓库 {repo.full_name} 的提交数量时出错: {e}")
        return 0


# write_to_readme(repos_data)  将提交信息写入README.md
def write_to_readme(repos_data):
    readme_path = "README.md"
    
    # 读取现有README内容
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = ""
    
    # 找到"## 📊 最近活动"部分并替换
    start_marker = "## 📊 最近活动"
    end_marker = "*最后更新:"
    
    # 查找开始位置
    start_pos = content.find(start_marker)
    if start_pos == -1:
        # 如果没有找到标记，在文件末尾添加
        new_section = f"\n\n{start_marker}\n\n"
    else:
        # 找到结束位置
        end_pos = content.find(end_marker, start_pos)
        if end_pos == -1:
            end_pos = len(content)
        # 保留开始标记之前的内容
        content = content[:start_pos]
        new_section = f"{start_marker}\n\n"
    
    # 生成新的内容
    # 强制转换为UTC+8时区
    utc_plus_8 = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(utc_plus_8).strftime("%Y-%m-%d %H:%M:%S")
    
    # 统计信息
    total_repos = len(repos_data)
    active_repos = len([repo for repo in repos_data if repo['commits'] > 0])
    total_commits = sum(repo['commits'] for repo in repos_data)
    
    new_content = f"{content}{new_section}"
    new_content += f"📈 **今日统计**: {total_repos} 个仓库，{active_repos} 个活跃，共 {total_commits} 次提交\n\n"
    
    # 按提交数量排序
    sorted_repos = sorted(repos_data, key=lambda x: x['commits'], reverse=True)
    
    # 添加有提交的仓库
    if active_repos > 0:
        new_content += "### 🔥 今日活跃仓库\n\n"
        for repo in sorted_repos:
            if repo['commits'] > 0:
                commits_emoji = "🚀" if repo['commits'] >= 5 else "✨" if repo['commits'] >= 2 else "📝"
                new_content += f"- {commits_emoji} **[{repo['name']}](https://github.com/{repo['full_name']})**: {repo['commits']} 次提交\n"
        new_content += "\n"
    

    
    new_content += f"\n*最后更新: {current_time}*\n"
    
    # 写入文件
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ README.md 已更新，包含 {total_repos} 个仓库的提交信息")



if __name__ == "__main__":    # 程序入口，只有直接执行当前文件时才会执行
    print("Building README.md")
    TOKEN = os.environ.get("GT_TOKEN", "")

    if not TOKEN:
        print("错误: 未找到 GT_TOKEN 环境变量，请设置有效的 GitHub token")
        exit(1)

    auth = Auth.Token(TOKEN)
    g = Github(auth=auth)
    repos = getlist(g)
    
    print(f"📊 正在分析 {len(repos)} 个仓库的提交情况...")
    
    # 收集所有仓库的提交数据
    repos_data = []
    for repo in repos:
        commits_count = get_commits_count(repo)
        repos_data.append({
            'name': repo.name,
            'full_name': repo.full_name,
            'commits': commits_count
        })
        print(f"  ✓ {repo.full_name}: {commits_count} 个提交")
    
    # 写入README.md
    write_to_readme(repos_data)
    
