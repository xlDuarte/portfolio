#!/usr/bin/env bash
# Requires local gh CLI authenticated as a repository administrator.
set -euo pipefail
repo="${1:-xlDuarte/portfolio}"
description="Portfólio com 111 projetos de Data Analytics, ML, SQL, BI, engenharia industrial e motorsport. Código, testes e demonstrações sintéticas."
homepage="https://xlduarte.github.io/portfolio/"
command -v gh >/dev/null || { echo "Instale GitHub CLI: https://cli.github.com/"; exit 1; }
gh auth status
echo "Editando About em: ${repo}"
gh api --method PATCH "repos/${repo}" -f description="$description" -f homepage="$homepage" --jq '{description,homepage,visibility}'
printf '%s\n' '{"names":["data-analytics","data-science","machine-learning","python","sql","industrial-analytics","business-intelligence","motorsport","formula-1","mlops","computer-vision","fastapi","streamlit","power-bi","portfolio"]}' |
 gh api --method PUT "repos/${repo}/topics" --input - --jq '.names'
echo "About atualizado: https://github.com/${repo}"
