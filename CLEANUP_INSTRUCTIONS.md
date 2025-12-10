# Instruções para Limpeza do Histórico Remoto

## ⚠️ AVISO IMPORTANTE
Reescrever o histórico do Git é **disruptivo**. Todos os colaboradores que tenham clonado ou feito push devem ser informados e precisarão de fazer uma nova clonagem ou fazer `git reset --hard` após o force-push.

## Opção 1: Usar `git filter-repo` (RECOMENDADO)

### Pré-requisitos
1. Instalar `git filter-repo`:
```powershell
pip install git-filter-repo
```

2. Fazer backup do repositório:
```powershell
git clone --mirror https://github.com/<seu_user>/<seu_repo>.git repo-backup.git
```

### Executar Limpeza
```powershell
# Ir para a raiz do repositório
cd C:\Ferramentas\API_GPS

# Remover config.env e cep_distance_cache.csv do histórico
git filter-repo --invert-paths --path config.env --path cep_distance_cache.csv

# Ou, se quiseres remover padrões (ex: *.csv)
# git filter-repo --invert-paths --path-glob '*.csv'
```

### Depois da Limpeza
```powershell
# Force-push para remoto (CUIDADO: isto reescreve o histórico!)
git push --force-all

# Todos os colaboradores precisam fazer:
cd <repo-directory>
git fetch
git reset --hard origin/main
```

## Opção 2: Usar BFG (alternativa)

1. Descarregar BFG: https://rtyley.github.io/bfg-repo-cleaner/

2. Executar:
```powershell
# Clone mirror
git clone --mirror https://github.com/<seu_user>/<seu_repo>.git

# BFG
bfg --delete-files config.env repo.git
bfg --delete-files cep_distance_cache.csv repo.git

# Cleanup
cd repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Push
git push --force-all
```

## O Que Já Foi Feito (Seguro)
✅ `.gitignore` atualizado com `config.env` e `cep_distance_cache.csv`  
✅ `env.sample` criado com placeholder  
✅ Ficheiros removidos do disco local  
✅ Commit local realizado  

## Próximos Passos (Antes de Force-Push)
1. **Coordena com colaboradores** — avisa que o histórico será reescrito
2. **Executa `git filter-repo`** — remove ficheiros do histórico
3. **Testa localmente** — verifica que `git log` não mostra mais os ficheiros
4. **Force-push** — `git push --force-all`
5. **Todos fazem reset** — colaboradores executam `git fetch; git reset --hard origin/main`
6. **Rotaciona chave** — se a chave estava em `config.env`, revoga a antiga e cria nova

## Se Não Quiseres Reescrever o Histórico
Deixar como está: os ficheiros foram removidos do disco e estão no `.gitignore`. Histório remoto fica com as referências antigas (normal em repos "sujos"), mas novos commits não incluem os ficheiros.

---

**Necessita de confirmação do utilizador antes de executar force-push.**
