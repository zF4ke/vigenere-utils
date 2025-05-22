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

def load_wordlist(path: str) -> list:
    with open(path, 'r', encoding='utf-8') as f:
        return [w.strip() for w in f if len(w.strip()) == len(w.strip())]

def fitness_portugues(key: str, wordset: set) -> float:
    """
    Score = bonus se key for palavra real + soma dos logs das frequências.
    Palavras reais ganham um offset grande para sempre ficarem no topo.
    """
    # soma dos logs das frequências monograma
    mono_score = sum(math.log(PORTUGUESE_FREQ.get(c, 0.01)) for c in key)
    if key in wordset:
        # bônus: 100 pontos (bem acima de qualquer variação de mono_score)
        return 100.0 + mono_score
    else:
        # penaliza chaves não-palavra
        return mono_score

def main():
    # Configurações
    ciphertext = "ztwccmb"
    WORDLIST = "palavras7letras.txt"
    ALL_KEYS_FILE = "all_keys7.txt"
    TOP_KEYS_FILE = "top_chaves7_vigenere.txt"
    TOP_N = 50
    TARGET_LEN = 7

    # linhas = baixar_linhas(URL)[1:]
    # with open(WORDLIST, 'w', encoding='utf-8') as fw:
    #     for linha in linhas:
    #         pal = linha.split()[0]
    #         pal_sem = remove_acentos(pal).lower()
    #         if len(pal_sem) == TARGET_LEN:
    #             fw.write(pal_sem + "\n")

    # Carrega as palavras de 7 letras e monta um set para lookup rápido
    print("Carregando wordlist local…")
    words = load_wordlist(WORDLIST)
    wordset = set(words)

    # Gera todas as chaves e grava em ALL_KEYS_FILE
    print(f"Gerando {len(words):,} chaves e salvando em '{ALL_KEYS_FILE}'…")
    all_keys = []
    with open(ALL_KEYS_FILE, 'w', encoding='utf-8') as fa:
        for w in words:
            key = reverse_vigenere_key(w, ciphertext)
            all_keys.append(key)
            fa.write(f"{key}\n")

    # Calcula fitness e ordena
    print("Calculando fitness e ordenando as chaves…")
    scored = [(k, fitness_portugues(k, wordset)) for k in all_keys]
    top = sorted(scored, key=lambda x: x[1], reverse=True)[:TOP_N]

    # Grava as TOP_N chaves
    with open(TOP_KEYS_FILE, 'w', encoding='utf-8') as ft:
        for k, _ in top:
            ft.write(k + "\n")

    # Print no console
    print(f"\n=== Top {TOP_N} chaves Vigenère para '{ciphertext}' ===")
    for rank, (k, sc) in enumerate(top, start=1):
        marker = "✓" if k in wordset else "𐄂"
        print(f"{rank:3d}. {k}  (score = {sc:.2f}) {marker}")

    print(f"\nArquivos gerados:\n - Todas as chaves: {ALL_KEYS_FILE}\n - Top {TOP_N}: {TOP_KEYS_FILE}")

if __name__ == "__main__":
    main()
