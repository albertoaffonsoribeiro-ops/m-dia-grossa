# 📰 MÍDIA GROSSA — Newsletter Automática

Newsletter gerada automaticamente todo dia com Claude AI + RSS Feeds brasileiros.

---

## O que você precisa (tudo gratuito exceto a API)

- Conta no **GitHub** → [github.com](https://github.com) (gratuito)
- Conta na **Anthropic** → [console.anthropic.com](https://console.anthropic.com) (paga, ~R$ 0,10–0,50 por edição)

---

## Passo a passo completo

### PASSO 1 — Criar o repositório no GitHub

1. Entre em [github.com](https://github.com) e faça login
2. Clique no **"+"** no canto superior direito → **"New repository"**
3. Dê o nome: `midia-grossa`
4. Deixe como **Public** (necessário para o GitHub Pages)
5. Clique em **"Create repository"**

---

### PASSO 2 — Subir os arquivos

Na página do repositório recém-criado, clique em **"uploading an existing file"** e suba:

```
gerar_newsletter.py
requirements.txt
.github/workflows/newsletter.yml   ← crie as pastas manualmente no upload
```

> 💡 **Dica para o arquivo .yml:** Ao fazer upload, você pode criar pastas digitando o caminho completo no campo de nome do arquivo. Digite `.github/workflows/newsletter.yml` e o GitHub cria as pastas automaticamente.

---

### PASSO 3 — Pegar sua chave da API do Claude

1. Acesse [console.anthropic.com](https://console.anthropic.com)
2. Vá em **"API Keys"** no menu lateral
3. Clique em **"Create Key"**
4. Dê um nome (ex: `newsletter`) e copie a chave — ela começa com `sk-ant-...`

> ⚠️ **Guarde essa chave** — você só a vê uma vez!

---

### PASSO 4 — Adicionar a chave como Secret no GitHub

1. No seu repositório, clique em **Settings** (aba superior)
2. No menu lateral, clique em **"Secrets and variables"** → **"Actions"**
3. Clique em **"New repository secret"**
4. **Name:** `ANTHROPIC_API_KEY`
5. **Value:** cole a chave que você copiou (`sk-ant-...`)
6. Clique em **"Add secret"**

---

### PASSO 5 — Ativar o GitHub Pages

1. No repositório, clique em **Settings**
2. Role até **"Pages"** no menu lateral
3. Em **"Source"**, selecione **"Deploy from a branch"**
4. Em **"Branch"**, selecione **"main"** e a pasta **"/ (root)"**
5. Clique em **Save**

Após alguns minutos, sua newsletter estará disponível em:
```
https://SEU_USUARIO.github.io/midia-grossa/
```

---

### PASSO 6 — Testar agora (sem esperar as 7h)

1. No repositório, clique na aba **"Actions"**
2. Clique no workflow **"📰 Gerar Newsletter Diária"** no menu lateral
3. Clique em **"Run workflow"** → **"Run workflow"**
4. Aguarde ~2 minutos
5. Acesse sua URL — a newsletter aparecerá!

---

## O que acontece todo dia

```
07:00h (horário de Brasília)
    ↓
GitHub Actions acorda automaticamente
    ↓
Instala Python e as dependências
    ↓
Roda gerar_newsletter.py:
    → Lê os RSS feeds (G1, GE, InfoMoney, Agência Brasil)
    → Envia as notícias para Claude API
    → Claude escreve e formata o HTML completo
    ↓
Salva index.html no repositório
    ↓
GitHub Pages publica automaticamente
    ↓
Sua newsletter está no ar! ✅
```

---

## Personalizar os feeds

Edite o dicionário `FEEDS` no arquivo `gerar_newsletter.py`:

```python
FEEDS = {
    "politica": [
        "https://g1.globo.com/rss/g1/politica/",
        # Adicione ou troque por outros feeds aqui
    ],
    "esportes": [
        "https://ge.globo.com/rss/ge/",
        # Ex: feed do Vasco, Fla, etc.
    ],
    ...
}
```

Qualquer site que tenha RSS (a maioria dos jornais brasileiros tem) pode ser adicionado.

---

## Histórico de edições

Toda edição é salva na pasta `edicoes/` com o nome `YYYY-MM-DD.html`.
Exemplo: `edicoes/2026-02-19.html`

---

## Custo estimado

| Item | Custo |
|---|---|
| GitHub (repositório + Actions + Pages) | **Gratuito** |
| Claude API (por edição gerada) | **~R$ 0,15–0,50** |
| Claude API (por mês, 30 edições) | **~R$ 5–15** |

---

## Problemas comuns

**"The workflow is not running"**
→ Verifique se o arquivo `.github/workflows/newsletter.yml` está no caminho certo.

**"Error: ANTHROPIC_API_KEY not found"**
→ Confira o Passo 4 — o nome do secret deve ser exatamente `ANTHROPIC_API_KEY`.

**"Page not found" na URL do GitHub Pages**
→ Aguarde 5-10 minutos após ativar o Pages. Se não resolver, rode o workflow manualmente (Passo 6).

**Newsletter em branco ou com erro de HTML**
→ Veja o log completo em Actions → clique no workflow com ❌ → clique em "gerar" para ver o erro.
