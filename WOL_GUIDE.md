# Guia de Configuração Wake-on-LAN (WoL) para Windows 11

Para que o bot funcione remotamente (ligar o PC pelo celular), precisamos configurar o Wake-on-LAN. Siga as instruções abaixo:

## Passo 1: Habilitar WoL na BIOS/UEFI
1. Reinicie o computador.
2. Acesse a BIOS (pressionando F2, DEL ou F12 durante a inicialização, dependendo da sua placa-mãe).
3. Procure por configurações de energia ("Power Management", "APM Configuration", "Advanced").
4. Habilite opções como:
   - "Power On By PCI-E/PCI"
   - "Wake on LAN"
   - "Resume by PME"
   - "ErP Ready" (Se existir, deixe **Desabilitado**, pois o ErP desliga a energia da placa de rede).
5. Salve e saia da BIOS.

## Passo 2: Configurar Adaptador de Rede no Windows 11
1. Clique com o botão direito no botão Iniciar e selecione **Gerenciador de Dispositivos**.
2. Expanda a seção **Adaptadores de rede**.
3. Clique com o botão direito na sua placa de rede (Ethernet/Realtek/Intel) e selecione **Propriedades**.
4. Na aba **Avançado**, procure por:
   - "Wake on Magic Packet" (Habilitado)
   - "Shutdown Wake-On-Lan" (Habilitado)
5. Na aba **Gerenciamento de Energia**, marque TODAS as caixas:
   - [x] O computador pode desligar o dispositivo para economizar energia
   - [x] Permitir que este dispositivo acorde o computador
   - [x] Permitir que apenas um "Magic Packet" acorde o computador
6. Clique em **OK**.

## Passo 3: Desabilitar a Inicialização Rápida (Recomendado)
A inicialização rápida do Windows pode impedir que a placa de rede fique "escutando" o pacote mágico quando o PC é desligado.
1. Abra o **Painel de Controle** (pesquise no Iniciar).
2. Vá em **Hardware e Sons** > **Opções de Energia**.
3. No menu esquerdo, clique em "Escolher a função dos botões de energia".
4. Clique em "Alterar configurações não disponíveis no momento" (requer admin).
5. Desmarque a opção **Ligar inicialização rápida (recomendado)**.
6. Salve as alterações.

## Passo 4: Como ligar pelo Celular
1. Conecte o PC à rede e anote o Endereço MAC (Abra o CMD e digite `ipconfig /all`, procure por "Endereço Físico" na sua placa de rede principal).
2. Anote também o IP local se for usar na mesma rede (geralmente começa com 192.168...).
3. No seu celular, baixe um app como o **Fing** ou o **Wake On LAN** (tem um ícone de um computador ligando).
4. Adicione um novo dispositivo no app colocando o MAC Address que você anotou.
5. Quando seu PC estiver desligado (mas ligado na tomada), basta abrir o app e clicar em "Wake" para ligá-lo remotamente.

Quando o PC ligar, o script de Autostart (que configuraremos neste projeto) irá iniciar o Bot do Telegram automaticamente em background!
