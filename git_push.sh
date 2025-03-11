#!/bin/bash

# 检查是否传入了 commit 信息作为参数
if [ $# -eq 0 ]; then
    echo "请提供 commit 信息作为参数，例如：./git_push.sh '更新代码'"
    exit 1
fi

# 获取 commit 信息
commit_message="$1"

# 执行 git 操作
git add .
git commit -m "$commit_message"
git push

# 检查 git push 是否成功
if [ $? -eq 0 ]; then
    echo "代码推送成功！"
else
    echo "代码推送失败，请检查网络或仓库状态。"
fi