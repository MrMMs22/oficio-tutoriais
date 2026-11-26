# Ofício

90 tutoriais curtos e grátis de casa, jardim e eletrônicos — passo a passo, material e alertas de segurança.

**Site:** https://mrmms22.github.io/oficio-tutoriais/

## Como funciona

- Site estático, sem dependências, publicado pelo GitHub Pages direto da branch `main` (pasta raiz).
- O conteúdo fica em `data/tutoriais.json`. Cada tutorial tem `id`, `tema` (`casa`, `jardim` ou `eletronicos`), `titulo`, `resumo`, `minutos`, `material`, `passos`, `dica` e `aviso`.
- `tools/build.py` gera a página inicial, uma página por tutorial em `t/<id>/`, a página 404, o `sitemap.xml` e o redirecionamento das URLs antigas.

## Editar um tutorial

1. Edite `data/tutoriais.json`.
2. Rode `python3 tools/build.py` (Python 3, nada para instalar).
3. Faça commit de tudo (inclusive os arquivos gerados). O Pages atualiza em 1–2 minutos.

## Recursos

Busca sem acento, filtros por categoria e por tempo, ordenação, tema claro/escuro, checklist de material e de passos com progresso salvo no aparelho, sumário, anterior/próximo, compartilhar, versão para impressão, dados estruturados (HowTo) para o Google e links antigos (`index.html#/t/<id>`, `tutoriais/tutorial.html`) redirecionando para as páginas novas.
