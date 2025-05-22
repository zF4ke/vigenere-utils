import requests
import unicodedata
import math

# URL opcional para baixar o pt_full (caso não tenha wordlist local)
URL = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2016/pt/pt_full.txt"

# Frequência de monogramas em pt-BR (em %)
PORTUGUESE_FREQ = {
    'a': 12.57, 'b': 1.01,  'c': 3.88,  'd': 4.99,  'e': 14.63,
    'f': 1.02,  'g': 1.30,  'h': 1.28,  'i': 6.18,  'j': 0.40,
    'k': 0.02,  'l': 2.78,  'm': 4.74,  'n': 5.05,  'o': 10.73,
    'p': 2.52,  'q': 1.20,  'r': 6.53,  's': 6.81,  't': 4.34,
    'u': 3.01,  'v': 1.67,  'w': 0.01,  'x': 0.21,  'y': 0.01,
    'z': 0.47
}

def remove_acentos(s: str) -> str:
    nkfd = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in nkfd if not unicodedata.combining(c))

def baixar_linhas(url: str) -> list:
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text.splitlines()

def to_num(c: str) -> int:
    return ord(c) - ord('a')

def to_char(n: int) -> str:
    return chr((n % 26) + ord('a'))

def reverse_vigenere_key(plain: str, cipher: str) -> str:
    return ''.join(
        to_char((to_num(c) - to_num(p)) % 26)
        for p, c in zip(plain, cipher)
    )

def load_wordlist(path: str, length: int) -> list:
    with open(path, 'r', encoding='utf-8') as f:
        return [w.strip() for w in f if len(w.strip()) == length]

def fitness_portugues(key: str, wordset: set) -> float:
    """
    Score = 100 + soma dos logs das frequências se key for palavra real;
    caso contrário, apenas a soma dos logs (menor score).
    """
    mono_score = sum(math.log(PORTUGUESE_FREQ.get(c, 0.01)) for c in key)
    return (100.0 + mono_score) if key in wordset else mono_score

def main():
    # Configurações
    ciphertext     = "zwccmb"         # ajuste para seu ciphertext de 6 letras
    WORDLIST_6     = "palavras6letras.txt"
    ALL_KEYS_FILE  = "all_keys6.txt"
    TOP_KEYS_FILE  = "top_chaves6_vigenere.txt"
    TARGET_LEN     = 6
    TOP_N          = 50

    # Se não tiver ainda o wordlist de 6 letras, descomente para gerar:
    # linhas = baixar_linhas(URL)[1:]
    # with open(WORDLIST_6, 'w', encoding='utf-8') as fw:
    #     for linha in linhas:
    #         pal = linha.split()[0]
    #         pal_sem = remove_acentos(pal).lower()
    #         if len(pal_sem) == TARGET_LEN:
    #             fw.write(pal_sem + "\n")

    # Carrega o wordlist e monta um set para lookup
    print(f"Carregando '{WORDLIST_6}'…")
    words6 = load_wordlist(WORDLIST_6, TARGET_LEN)
    wordset = set(words6)

    # Gera e salva todas as chaves
    print(f"Gerando {len(words6):,} chaves e salvando em '{ALL_KEYS_FILE}'…")
    all_keys = []
    with open(ALL_KEYS_FILE, 'w', encoding='utf-8') as fa:
        for w in words6:
            k = reverse_vigenere_key(w, ciphertext)
            all_keys.append(k)
            fa.write(f"{k} -> {w}\n")

    # Calcula fitness e ordena
    print("Calculando fitness e ordenando as chaves…")
    scored = [(k, fitness_portugues(k, wordset)) for k in all_keys]
    top = sorted(scored, key=lambda x: x[1], reverse=True)[:TOP_N]

    # Grava as TOP_N chaves
    with open(TOP_KEYS_FILE, 'w', encoding='utf-8') as ft:
        for k, _ in top:
            ft.write(k + "\n")

    # Exibe no console
    print(f"\n=== Top {TOP_N} chaves Vigenère para '{ciphertext}' ===")
    for i, (k, sc) in enumerate(top, 1):
        mark = "✓" if k in wordset else "𐄂"
        print(f"{i:3d}. {k}  (score={sc:.2f}) {mark}")

    print(f"\nArquivos gerados:\n"
          f" - todas as chaves:    {ALL_KEYS_FILE}\n"
          f" - top {TOP_N} chaves:  {TOP_KEYS_FILE}")

if __name__ == "__main__":
    main()
