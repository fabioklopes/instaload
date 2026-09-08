# Downloader de posts do Instagram

Baixa todas as mídias de uma publicação pública — fotos, vídeos e todos os itens de um carrossel — usando Python.

Os arquivos são organizados assim:

```text
downloads/
  nome_do_perfil/
    YYYY-MM-DD-Assunto/
      2026-09-05_12-30-00_CODIGO.jpg
```

Apenas essa raiz `downloads` é usada. Ao baixar outro post do mesmo perfil/canal, ele é colocado na subpasta correspondente a `YYYY-MM-DD-Assunto`. A pasta é reutilizada quando já existe: os arquivos incluem o shortcode da publicação, e uma nova execução do mesmo link não cria pastas duplicadas nem baixa novamente os arquivos existentes.

Enquanto a mídia é baixada, o terminal mostra uma animação `Baixando...`. Ao finalizar, o programa informa se novos arquivos foram baixados (ou se já estavam na pasta) e exibe o caminho de destino.

## Instalação

No PowerShell, dentro desta pasta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edite o arquivo `.env` conforme necessário. Para posts públicos, normalmente é possível deixar usuário e senha vazios. Se o Instagram limitar acessos anônimos, preencha `INSTAGRAM_USERNAME` e `INSTAGRAM_PASSWORD`.

Se a conta usa autenticação em duas etapas (2FA), no primeiro login — ou quando a sessão expirar — o programa solicitará o código de verificação no terminal. Após o acesso, a sessão fica no arquivo definido em `SESSION_FILE`, portanto não é necessário informar o código a cada execução enquanto ela permanecer válida. O código não é armazenado.

## Uso

```powershell
python download_post.py
```

O programa pedirá que você cole o link da publicação. Se preferir, o link também pode ser passado diretamente:

```powershell
python download_post.py "https://www.instagram.com/p/CODIGO_DO_POST/"
```

Para definir manualmente o assunto da subpasta:

```powershell
python download_post.py "https://www.instagram.com/p/CODIGO_DO_POST/" --assunto "Festa de aniversário"
```

## Observações

- São aceitos posts de uma foto, carrosséis, vídeos, reels e sequências de vídeos; links com `/p/`, `/reel/`, `/reels/` ou `/tv/` são reconhecidos e todas as mídias disponíveis são baixadas.
- Use apenas conteúdo público que você tenha permissão para baixar e respeite os termos do Instagram e direitos autorais.
- O Instagram pode exigir autenticação, limitar requisições ou solicitar verificações. O script não tenta contornar esses controles.
