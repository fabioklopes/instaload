# Downloader de posts do Instagram

Baixa todas as mídias de uma publicação pública — fotos, vídeos e todos os itens de um carrossel — usando Python.

Os arquivos são organizados assim:

```text
📂 downloads/
|--- 📂 nome_do_perfil/
|------ 📂 YYYY-MM-DD-Assunto/
|---------- 📸 2026-09-05_12-30-00_CODIGO.jpg
```

Apenas essa raiz `downloads` é usada. Ao baixar outro post do mesmo perfil/canal, ele é colocado na subpasta correspondente a `YYYY-MM-DD-Assunto`. A pasta é reutilizada quando já existe: os arquivos incluem o shortcode da publicação, e uma nova execução do mesmo link não cria pastas duplicadas nem baixa novamente os arquivos existentes.

Enquanto a mídia é baixada, o terminal mostra uma animação `Baixando...`. Ao finalizar, o programa informa se novos arquivos foram baixados (ou se já estavam na pasta) e exibe o caminho de destino.

## Instalação

⚠️ **ATENÇÃO: É necessário ter o Python instalado no seu computador.**

1. No PowerShell, dentro desta pasta:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

2. Crie um arquivo chamado `.env` na raíz da aplicação. Em seguida, edite o arquivo `.env` conforme o quadro abaixo. Para posts públicos, normalmente é possível deixar usuário e senha vazios. Se o Instagram limitar acessos anônimos, preencha `INSTAGRAM_USERNAME` e `INSTAGRAM_PASSWORD`.

**Arquivo .env**
```# Credenciais opcionais para posts públicos.
INSTAGRAM_USERNAME=seu_usuario
INSTAGRAM_PASSWORD=sua_senha
DOWNLOAD_DIR=downloads
SESSION_FILE=.instagram-session
```

Se a sua conta usa o 2FA (2º Fator de Autenticação), apenas no 1º login a aplicação solicitará que você digite esse código. Quando a seção expirar, será necessária a digitação de um novo código. Após o acesso, a sessão fica no arquivo definido em `SESSION_FILE`, portanto não é necessário informar o código a cada execução enquanto ela permanecer válida. O código não é armazenado.

## Uso
```powershell
iniciar.bat
```

De forma automática, a aplicação vai inicializar o ambiente virtual da aplicação e executar o arquivo `download_post.py`. 

Se tudo der certo, a aplicação vai pedir que você cole o link da postagem desejada. Caso tenha preferência, você também pode executar a aplicação diretamente com o link desejado desta maneira:

```powershell
python download_post.py "https://www.instagram.com/p/CODIGO_DO_POST/"
```

Para definir manualmente o assunto da subpasta (exemplo):

```powershell
python download_post.py "https://www.instagram.com/p/CODIGO_DO_POST/" --assunto "Festa de aniversário"
```

## Observações

- São aceitos posts de uma foto, carrosséis, vídeos, reels e sequências de vídeos; links que possuam `/p/`, `/reel/`, `/reels/` ou `/tv/` na sua composição de URL. Todas as mídias disponíveis são baixadas.
- Use apenas conteúdo público que você tenha permissão para baixar e respeite os termos do Instagram e direitos autorais.
- O Instagram pode exigir autenticação, limitar requisições ou solicitar verificações. O script não tenta contornar esses controles.
