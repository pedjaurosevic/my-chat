"""
UI Helper funkcije
"""


def get_model_avatar(model_name):
    """Vraća specifičan emoji na osnovu imena modela"""
    if not model_name:
        return "🤖"

    name = model_name.lower()

    # 1. Specifična mapiranja po porodicama modela
    if "llama" in name: return "🦙"      # Llama
    if "mistral" in name: return "🌪️"    # Mistral (Storm)
    if "mixtral" in name: return "🌀"    # Mixtral
    if "gemma" in name: return "💎"      # Gemma (Gem)
    if "qwen" in name: return "🐉"       # Qwen (Dragon)
    if "deepseek" in name: return "🐳"   # DeepSeek (Whale/Deep sea)
    if "phi" in name: return "🔮"        # Phi (Golden Ratio/Physics)
    if "vicuna" in name: return "🐪"     # Vicuna
    if "wizard" in name: return "🧙‍♂️"    # Wizard
    if "codellama" in name: return "👾"  # Code Llama
    if "dolphin" in name: return "🐬"    # Dolphin
    if "orca" in name: return "🐋"       # Orca
    if "zephyr" in name: return "🌬️"     # Zephyr (Wind)
    if "falcon" in name: return "🦅"     # Falcon
    if "starling" in name: return "🐦"   # Starling
    if "solar" in name: return "☀️"      # Solar
    if "command" in name: return "⌘"     # Command R
    if "hermes" in name: return "⚚"      # Hermes
    if "aya" in name: return "🌺"        # Aya
    if "yi" in name: return "🏔️"         # Yi (Mountain range implies tough)
    if "claude" in name: return "🎭"     # Claude (Anthropic)
    if "gpt" in name: return "🤖"        # GPT generic

    # 2. Bazen raznolikih avatara za ostale modele (deterministički izbor)
    # Koristimo hash imena da bi isti model uvek dobio isti avatar
    pool = [
        "👾", "👽", "👻", "👺", "👹", "💀", "🤡", "🦾", "👁️", "🧘",
        "🕵️", "🧞", "🧟", "🧛", "🦉", "🐙", "🍄", "🎲", "🧩", "🎹",
        "🎯", "🎰", "🎱", "💿", "💾", "📡", "🛸", "🦠", "🧬", "🧪"
    ]

    hash_val = sum(ord(c) for c in name)
    return pool[hash_val % len(pool)]
