# Frontend - Copa do Mundo Tech Album 🏆💻

Este diretório contém a interface visual interativa do projeto **Alura Album**, construída em HTML, CSS e JavaScript puros (Vanilla). A interface simula um livro físico em 3D com folheamento realista, sintetiza sons procedurais de papel no navegador e conecta-se dinamicamente ao backend para gerenciar a coleção de figurinhas do usuário.

---

## 📁 Estrutura de Arquivos

* **`index.html`**: Estrutura semântica das páginas do álbum, badges das categorias, botões de controle e o modal de autenticação de usuários.
* **`src/css/style.css`**: Identidade visual premium baseada em tons escuros e magenta, efeitos 3D de profundidade (lombada do livro), animações (glitch, esfera rotativa) e suporte completo para o Light Mode.
* **`src/js/app.js`**: Lógica de inicialização do álbum (`PageFlip`), manipulação de toque/arraste, geração de som procedural (`Web Audio API`), consumo das rotas da API (login, cadastro, perfil) e colagem/remoção dinâmica de figurinhas.

---

## ✨ Funcionalidades Principais

1. **Efeito Físico de Livro (3D):** Utiliza a biblioteca `PageFlip.js` para permitir que o usuário arraste e folheie as páginas do álbum com animações realistas tridimensionais.
2. **Som Procedural de Papel:** Synthe de áudio em tempo real usando a `Web Audio API` para gerar o som de papel sendo folheado, modulado por frequência dinâmica de acordo com a dobra.
3. **Autenticação com Modal Premium:** Modal de login e cadastro integrado diretamente com o backend. Suporta salvamento e auto-login após o registro de nova conta.
4. **Coleção Interativa (Colar/Descolar):**
   * Os slots de figurinhas só exibem a imagem se o usuário estiver logado e possuir a figurinha em sua conta.
   * Ao passar o mouse em um slot vazio, a borda tracejada muda para verde neon. Ao clicar, a figurinha correspondente é colada instantaneamente no SQLite e atualizada na tela.
   * Ao clicar em uma figurinha colada, o sistema abre uma confirmação para descolar.

---

## 🚀 Guia de Uso Passo a Passo

Siga o roteiro abaixo para executar e interagir com o álbum completo na sua máquina:

### Passo 1: Inicializar o Backend
Para que os dados dos usuários e as fotos das figurinhas sejam carregados, o servidor backend precisa estar ativo na porta `8000`.
1. Acesse o diretório do backend e ative seu ambiente virtual.
2. Execute o comando:
   ```bash
   uvicorn main:app --reload
   ```
*(O banco de dados SQLite será inicializado automaticamente na primeira execução).*

### Passo 2: Acessar a Interface do Álbum
O backend está configurado para servir a página do frontend diretamente. Acesse o endereço abaixo no seu navegador:
👉 **[http://localhost:8000/](http://localhost:8000/)**

*Nota: Você também pode abrir o arquivo `index.html` diretamente ou servir o diretório frontend separadamente (ex: usando a extensão Live Server ou rodando `npx serve` na pasta frontend), mas rodar pelo endereço do backend é o método recomendado para evitar bloqueios de CORS no navegador.*

### Passo 3: Criar uma Conta ou Logar
1. No canto superior direito da página, clique no **ícone de Usuário** (silhueta/avatar).
2. O modal de autenticação com efeito de vidro (glassmorphism) se abrirá.
3. Você pode se conectar usando o usuário de teste criado automaticamente:
   * **Usuário:** `test_user_pion`
   * **Senha:** `test_password`
4. Ou clique na aba **"Cadastrar"** e crie um novo usuário. Ao clicar em cadastrar, você será autenticado automaticamente.
5. Após o login, o ícone de usuário exibirá uma **bolinha verde** (indicador de conectado).

### Passo 4: Cole e Gerencie suas Figurinhas
1. Com o login feito, folheie as páginas do álbum arrastando os cantos da folha ou clicando nas setas de navegação.
2. Quando passar o cursor sobre um slot vazio, a borda ficará verde brilhante.
3. **Dê um clique no slot.** A imagem correspondente à personalidade da tecnologia será renderizada imediatamente e salva na sua conta!
4. **Para remover uma figurinha**, clique em cima da imagem instalada e confirme a remoção na caixa de diálogo.
