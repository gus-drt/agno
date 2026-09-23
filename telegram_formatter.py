import re
import html

def sanitize_text(text: str) -> str:
    """
    Remove mensagens de erro internas de políticas de ferramentas,
    hooks de segurança e resíduos de terminal que não devem aparecer no chat.
    """
    if not text:
        return ""
    # Remove avisos como: Denied by policy "confirm_run_command". ("denied by pre-tool hook: ...")
    text = re.sub(r'Denied by policy "[^"]*"\.\s*\("denied by pre-tool hook:[^)]*"\)\s*', '', text)
    text = re.sub(r'\(denied by pre-tool hook:[^)]*\)\s*', '', text)
    text = re.sub(r'Denied by policy "[^"]*"\.\s*', '', text)
    return text.strip()

def markdown_to_telegram_html(text: str) -> str:
    """
    Converte Markdown com suporte a cabeçalhos, negrito, itálico, código,
    listas e divisores para o formato HTML aceito pela API do Telegram.
    Fecha tags abertas automaticamente para garantir estabilidade em streaming.
    """
    text = sanitize_text(text)
    if not text:
        return ""
        
    # Fecha marcadores de Markdown abertos no final do streaming
    if text.count("```") % 2 != 0:
        text += "\n```"
    if text.count("`") % 2 != 0:
        text += "`"
    if text.count("**") % 2 != 0:
        text += "**"
    if text.count("__") % 2 != 0:
        text += "__"

    code_blocks = []
    def save_code_block(match):
        lang = match.group(1) or ""
        code = match.group(2)
        escaped_code = html.escape(code.strip())
        tag = f'<pre><code class="language-{lang}">{escaped_code}</code></pre>' if lang else f'<pre><code>{escaped_code}</code></pre>'
        code_blocks.append(tag)
        return f"@@@CODE_BLOCK_{len(code_blocks)-1}@@@"

    # Salva blocos de código pré-formatados ```...```
    text = re.sub(r'```(\w+)?\n?(.*?)```', save_code_block, text, flags=re.DOTALL)
    
    # Salva código inline `...`
    inline_codes = []
    def save_inline_code(match):
        code = match.group(1)
        inline_codes.append(f'<code>{html.escape(code)}</code>')
        return f"@@@INLINE_CODE_{len(inline_codes)-1}@@@"

    text = re.sub(r'`([^`\n]+)`', save_inline_code, text)
    
    # Escapa caracteres especiais HTML no restante do texto
    text = html.escape(text)
    
    # Linhas divisórias (---, ___, ***)
    text = re.sub(r'(?m)^(\s*[-*_]\s*){3,}$', '──────────────', text)
    
    # Cabeçalhos (#, ##, ###, ####) convertidos para negrito destacado
    text = re.sub(r'(?m)^#{1,6}\s*(.+)$', r'<b>\1</b>', text)
    
    # Marcadores de lista (* ou - no início da linha) convertidos para bullet elegante '•'
    text = re.sub(r'(?m)^(\s*)[*\-]\s+(.+)$', r'\1• \2', text)
    
    # Negrito **texto** e __texto__
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    
    # Itálico *texto* e _texto_ (evitando conflito com tags ou palavras compostas)
    text = re.sub(r'(?<!\w)\*([^*]+?)\*(?!\w)', r'<i>\1</i>', text)
    text = re.sub(r'(?<!\w)_([^_]+?)_(?!\w)', r'<i>\1</i>', text)
    
    # Links Markdown [texto](url)
    text = re.sub(r'\[([^\]]+)\]\((https?://[^\s\)]+)\)', r'<a href="\2">\1</a>', text)
    
    # Restaura o código inline e blocos de código
    for i, code_html in enumerate(inline_codes):
        text = text.replace(f"@@@INLINE_CODE_{i}@@@", code_html)
    for i, block_html in enumerate(code_blocks):
        text = text.replace(f"@@@CODE_BLOCK_{i}@@@", block_html)
        
    # Balanceamento e fechamento automático de tags para streaming seguro
    for tag in ["b", "i", "code", "pre", "a"]:
        opens = len(re.findall(rf'<{tag}(?: [^>]*)?>', text))
        closes = len(re.findall(rf'</{tag}>', text))
        if opens > closes:
            text += f"</{tag}>" * (opens - closes)
            
    return text
