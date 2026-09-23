# 🤖 Agno - Assistente de IA Pessoal via Telegram

**Agno** é um agente de inteligência artificial pessoal que roda diretamente no seu computador e permite que você controle sua máquina, desenvolva projetos, execute comandos e automatize tarefas remotamente pelo aplicativo **Telegram** (no celular ou PC).

---

## ✨ Principais Funcionalidades

- 💬 **Interface no Telegram:** Comunique-se com o assistente em tempo real usando formatação rica e atualizações em stream.
- ⚡ **Dois Modos de Operação:**
  - **Modo CLI:** Executa comandos e tarefas usando o motor de linha de comando com controle total de ferramentas.
  - **Modo SDK:** Integração direta com a SDK Python para interações fluídas e estruturadas.
- 🛡️ **Segurança por Whitelist:** Apenas o seu Telegram User ID (`ALLOWED_USER_ID`) tem permissão para emitir comandos.
- 🚀 **Autostart Invisível no Windows:** Inicia automaticamente em segundo plano ao ligar o PC (sem janelas de terminal abertas).
- 🔌 **Suporte a Wake-on-LAN (WoL):** Ligue seu computador remotamente de qualquer lugar pelo celular (guia incluso).
- 🛠️ **Notificações de Ferramentas:** Acompanhe em tempo real quais ferramentas o agente está acionando no sistema.

---

## 📁 Estrutura do Projeto

```text
Agno/
├── .agents/rules/         # Regras e persona do agente
├── backends/              # Implementações dos backends (CLI e SDK)
│   ├── base.py
│   ├── cli_backend.py
│   └── sdk_backend.py
├── agent_runner.py        # Gerenciador de ciclo de vida e alternância de backends
├── agno.bat               # Script rápido de inicialização via terminal
├── config.py              # Carregamento de variáveis e configurações de estado
├── install_autostart.ps1  # Script PowerShell para instalar inicialização com o Windows
├── main.py                # Ponto de entrada da aplicação
├── memory_manager.py      # Registro de sessões e histórico local
├── requirements.txt       # Dependências Python
├── run_hidden.vbs         # Launcher silencioso em background para Windows
├── telegram_bot.py        # Lógica do bot Telegram e handlers de mensagens
├── telegram_formatter.py  # Formatador e sanitizador de Markdown para Telegram HTML
├── WOL_GUIDE.md           # Guia passo a passo de configuração do Wake-on-LAN
└── .env.example           # Modelo de variáveis de ambiente
```

---

## 🚀 Como Instalar e Rodar

### 1. Pré-requisitos
- Python 3.10 ou superior
- Uma conta no Telegram
- [Opcional] CLI do agente instalado na máquina

### 2. Clonando o Repositório
```bash
git clone https://github.com/gus-drt/agno.git
cd agno
```

### 3. Configurando o Ambiente Virtual
```bash
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Configuração das Variáveis de Ambiente
Copie o arquivo de exemplo `.env.example` para `.env`:
```bash
cp .env.example .env
```
Abra o `.env` e preencha suas informações:
- `TELEGRAM_BOT_TOKEN`: Obtenha com o [@BotFather](https://t.me/BotFather) no Telegram.
- `ALLOWED_USER_ID`: Seu ID numérico no Telegram (obtenha enviando uma mensagem para [@userinfobot](https://t.me/userinfobot)).
- `GEMINI_API_KEY`: Sua chave de API (caso utilize o modo SDK).
- `CLI_COMMAND`: Comando do CLI configurado (padrão: `agy`).

### 5. Execução
Para iniciar o bot no terminal:
```bash
python main.py
```
*(Ou execute o arquivo `agno.bat` no Windows).*

---

## ⚙️ Comandos do Bot no Telegram

| Comando | Descrição |
| :--- | :--- |
| `/start` | Mensagem inicial de boas-vindas e status |
| `/status` | Exibe o backend de IA atualmente ativo (`CLI` ou `SDK`) |
| `/mode cli` | Alterna o motor de inteligência para o modo CLI |
| `/mode sdk` | Alterna o motor de inteligência para o modo SDK |

---

## 💤 Inicialização Automática e Wake-on-LAN

- **Para iniciar com o Windows em segundo plano:**
  Execute o script `install_autostart.ps1` no PowerShell. Um atalho silencioso será criado na pasta `Inicializar` do seu usuário.
- **Para ligar o PC remotamente pelo celular:**
  Consulte o guia detalhado em [`WOL_GUIDE.md`](WOL_GUIDE.md).

---

## 🔒 Segurança

- O arquivo `.env` **nunca** deve ser versionado no Git. Ele já está listado no `.gitignore`.
- O bot valida o `ALLOWED_USER_ID` em todas as requisições para impedir que terceiros executem comandos na sua máquina.
- Antes de publicar commits, certifique-se de não incluir credenciais em código-fonte.

---

## 📄 Licença
Este projeto é distribuído sob a licença MIT.
