param(
    [string]$GitHubUser = "xlDuarte",
    [string]$RepoName = "automotive-industrial-lab"
)
$ErrorActionPreference = "Stop"
git init -b main
git add -A
git commit -m "feat: release 3D portfolio website (index.html), 111 projects & F1-PIP"
if (Get-Command gh -ErrorAction SilentlyContinue) {
    gh repo create "$GitHubUser/$RepoName" --public --source=. --remote=origin --push
} else {
    git remote remove origin 2>$null
    git remote add origin "https://github.com/$GitHubUser/$RepoName.git"
    git push -u origin main
}
Write-Host "Upload concluido! Site e 110 projetos publicados." -ForegroundColor Green
