#!/usr/bin/env bash
set -e
GH_USER="${1:-xlDuarte}"
REPO_NAME="${2:-automotive-industrial-lab}"

echo "=================================================================="
echo " Inicializando repositorio Git (Site Portfolio + 110 Projetos + F1-PIP)"
echo "=================================================================="
git init -b main
git add -A
git commit -m "feat: release 3D portfolio website (index.html), 111 projects & F1-PIP" || true

if command -v gh >/dev/null 2>&1; then
    gh repo create "${GH_USER}/${REPO_NAME}" --public --source=. --remote=origin --push || {
        git remote remove origin 2>/dev/null || true
        git remote add origin "https://github.com/${GH_USER}/${REPO_NAME}.git"
        git push -u origin main
    }
else
    git remote remove origin 2>/dev/null || true
    git remote add origin "https://github.com/${GH_USER}/${REPO_NAME}.git"
    git push -u origin main
fi
echo "Envio finalizado. Verifique o repositorio remoto antes de anunciar a publicacao."
