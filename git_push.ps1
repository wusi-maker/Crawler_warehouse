# 检查是否传入了 commit 信息作为参数
if ($args.Count -eq 0) {
    Write-Host "请提供 commit 信息作为参数，例如：.\git_push.ps1 '更新代码'"
    return
}

# 获取 commit 信息
$commitMessage = $args[0]

# 执行 git 操作
git add .
git commit -m $commitMessage
git push

