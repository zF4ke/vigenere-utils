import os
import requests
import unicodedata
import re

# --- Configurações ---
URL_PT_FULL      = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2016/pt/pt_full.txt"
WORDLIST_CACHE   = 'pt_full_cache.txt'          # cache para pt_full.txt
CIPHERTEXT       = "lmdxr fm iei qvnum se xzvgwoiwa"  # seu ciphertext completo (frase)
MIN_KEY_LEN      = 4                             # tamanho mínimo da chave a considerar
MAX_KEY_LEN      = 12                            # tamanho máximo da chave a considerar
TOP_N            = 20                            # quantas chaves "top" queremos
TOP_KEYS_FILE    = "top_chaves_genericas.txt"

# --- Carregamento de dicionário de frequência ---
def remove_acentos(s: str) -> str:
    nkfd = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in nkfd if not unicodedata.combining(c))


def load_word_freq(url: str) -> dict:
    """
    Baixa (se necessário) pt_full e retorna dict: palavra->frequência.
    Todas em lowercase sem acentos.
    """
    cache = WORDLIST_CACHE
    if not os.path.exists(cache):
        print(f"Cache de frequência não encontrado. Baixando de {url}...")
        resp = requests.get(url)
        resp.raise_for_status()
        with open(cache, 'w', encoding='utf-8') as f:
            f.write(resp.text)
        print(f"Cache salvo em '{cache}'.")

    word_freq = {}
    with open(cache, 'r', encoding='utf-8') as f:
        next(f)  # pula cabeçalho
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                w, freq = parts[0], parts[1]
                w = remove_acentos(w.lower())
                try:
                    word_freq[w] = int(freq)
                except ValueError:
                    continue
    return word_freq

# --- Vigenère Utils ---

def to_num(c: str) -> int:
    return ord(c) - ord('a')

def to_char(n: int) -> str:
    return chr((n % 26) + ord('a'))


def decrypt_vigenere(cipher: str, key: str) -> str:
    """Descriptografa todo `ciphertext` usando a key (repetida)."""
    plain = []
    ki = 0
    for c in cipher:
        if c.isalpha():
            k = key[ki % len(key)]
            plain.append(to_char((to_num(c.lower()) - to_num(k)) % 26))
            ki += 1
        else:
            plain.append(c)
    return ''.join(plain)

# --- Fitness baseada em contagem de palavras + frequência para desempate ---

def fitness_sentence(decrypted: str, word_freq: dict) -> tuple:
    """
    Retorna tupla (num_palavras_validas, soma_freq_palavras) para desempate.
    """
    tokens = re.findall(r"[a-zA-Z]+", decrypted.lower())
    valid_count = 0
    freq_sum = 0
    for t in tokens:
        t_clean = remove_acentos(t)
        freq = word_freq.get(t_clean, 0)
        if freq > 0:
            valid_count += 1
            freq_sum += freq
    return valid_count, freq_sum

# --- Main Pipeline ---

def main():
    # 1) carrega dicionário com frequência
    print("Carregando dicionário de frequência...")
    word_freq = load_word_freq(URL_PT_FULL)

    # 2) gera candidatos de chave (apenas palavras entre min e max)
    candidates = [w for w, f in word_freq.items() if MIN_KEY_LEN <= len(w) <= MAX_KEY_LEN]

    # 3) testa cada candidato e pontua
    scored = []
    for key in candidates:
        decrypted = decrypt_vigenere(CIPHERTEXT, key)
        valid_count, freq_sum = fitness_sentence(decrypted, word_freq)
        scored.append((key, valid_count, freq_sum, decrypted))

    # 4) extrai top N, ordenando por valid_count, depois freq_sum
    top = sorted(
        scored,
        key=lambda x: (x[1], x[2]),
        reverse=True
    )[:TOP_N]

    # 5) grava e exibe resultados
    with open(TOP_KEYS_FILE, 'w', encoding='utf-8') as ft:
        for key, valid_count, freq_sum, _ in top:
            ft.write(f"{key}  # words={valid_count}, freq_sum={freq_sum}\n")

    print(f"\n=== Top {TOP_N} chaves para a frase ===")
    for i, (key, valid_count, freq_sum, dec) in enumerate(top, 1):
        print(f"{i:2d}. key='{key}' words={valid_count}, freq_sum={freq_sum} -> {dec}")
    print(f"\nArquivo top salvo em: {TOP_KEYS_FILE}")

if __name__ == "__main__":
    main()
