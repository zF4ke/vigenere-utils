import os
import requests
import unicodedata
import math

# --- Configurações ---
URL_PT_FULL      = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2016/pt/pt_full.txt"
WORDLIST         = "palavras_tx.txt"        # lista de palavras em pt-BR (uma por linha)
CIPHERTEXT       = "kmrvrfwg"               # seu ciphertext genérico
MIN_KEY_LEN      = 4                        # tamanho mínimo da chave a considerar
MAX_KEY_LEN      = 9                        # tamanho máximo da chave a considerar
TOP_N            = 100                      # quantas chaves "top" queremos
ALL_KEYS_FILE    = "all_keys_all_periods.txt"
TOP_KEYS_FILE    = "top_chaves_genericas.txt"

# Frequências de monogramas em pt-BR (em %)
PORT_FREQ = {
    'a':12.57,'b':1.01,'c':3.88,'d':4.99,'e':14.63,
    'f':1.02, 'g':1.30,'h':1.28,'i':6.18,'j':0.40,
    'k':0.02,'l':2.78,'m':4.74,'n':5.05,'o':10.73,
    'p':2.52,'q':1.20,'r':6.53,'s':6.81,'t':4.34,
    'u':3.01,'v':1.67,'w':0.01,'x':0.21,'y':0.01,
    'z':0.47
}

def remove_acentos(s: str) -> str:
    nkfd = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in nkfd if not unicodedata.combining(c))

def to_num(c: str) -> int:
    return ord(c) - ord('a')

def to_char(n: int) -> str:
    return chr((n % 26) + ord('a'))

def reverse_vigenere_key_segment(plain: str, cipher: str) -> str:
    """Retorna o key-stream (mesmo tamanho do texto) que faria plain -> cipher."""
    return ''.join(
        to_char((to_num(c) - to_num(p)) % 26)
        for p, c in zip(plain, cipher)
    )

def minimal_period(s: str, min_len: int, max_len: int) -> int:
    """
    Retorna o menor p entre min_len e max_len tal que
    repetir s[:p] (e truncar) reconstrói s. Se nenhum válido, retorna max_len.
    """
    L = len(s)
    upper = min(max_len, L)
    for p in range(min_len, upper+1):
        if (s[:p] * ((L//p)+1))[:L] == s:
            return p
    return upper

def fitness(key: str, wordset: set) -> float:
    """
    Score = 100 + soma(log-freq) se key for palavra real; senão apenas soma(log-freq).
    """
    mono = sum(math.log(PORT_FREQ.get(c, 0.01)) for c in key)
    return (100.0 + mono) if key in wordset else mono

def load_wordlist(path: str, length: int=None) -> list:
    """
    Lê e retorna palavras sem acentos.
    Se length for setado, filtra só palavras com esse tamanho.
    """
    # Baixa o wordlist se não existir
    if not os.path.exists(path):
        print(f"Wordlist '{path}' não encontrado. Baixando...")
        resp = requests.get(URL_PT_FULL)
        resp.raise_for_status()
        with open(path, 'w', encoding='utf-8') as fw:
            for line in resp.text.splitlines()[1:]:
                word = remove_acentos(line.split()[0]).lower()
                fw.write(word + "\n")
        print(f"Wordlist '{path}' baixado e salvo.")

    lst = []
    with open(path, 'r', encoding='utf-8') as f:
        for ln in f:
            w = remove_acentos(ln.strip().lower())
            if length is None or len(w) == length:
                lst.append(w)
    return lst

def main():
    L = len(CIPHERTEXT)

    # 1) carrega candidatos de plaintext do tamanho do ciphertext
    plains = load_wordlist(WORDLIST, length=L)
    # para fitness, wordset de palavras entre min e max len
    wordset = set(load_wordlist(WORDLIST))
    
    # 2) gerar ALL_KEYS_FILE com key-stream, período e prefixo
    with open(ALL_KEYS_FILE, 'w', encoding='utf-8') as fa:
        for p in plains:
            ks     = reverse_vigenere_key_segment(p, CIPHERTEXT)
            period = minimal_period(ks, MIN_KEY_LEN, MAX_KEY_LEN)
            prefix = ks[:period]
            fa.write(f"{ks} | period={period} | key='{prefix}'\n")

    # 3) pontuar cada prefix
    scored = {}
    for p in plains:
        ks     = reverse_vigenere_key_segment(p, CIPHERTEXT)
        period = minimal_period(ks, MIN_KEY_LEN, MAX_KEY_LEN)
        prefix = ks[:period]
        sc     = fitness(prefix, wordset)
        # manter o maior score por prefix único
        if prefix not in scored or sc > scored[prefix]:
            scored[prefix] = sc

    # 4) extrair TOP_N únicos
    top = sorted(scored.items(), key=lambda x: x[1], reverse=True)[:TOP_N]

    # 5) salvar e printar top
    with open(TOP_KEYS_FILE, 'w', encoding='utf-8') as ft:
        for k, _ in top:
            ft.write(k + "\n")

    print(f"\n=== Top {TOP_N} chaves candidatas para '{CIPHERTEXT}' ===")
    for i, (k, sc) in enumerate(top, 1):
        mark = "✓" if k in wordset else "𐄂"
        print(f"{i:3d}. {k:<{MAX_KEY_LEN}} (score={sc:.2f}) {mark}")

    print(f"\nArquivos gerados:\n"
          f" - Todos os key-streams: {ALL_KEYS_FILE}\n"
          f" - Top {TOP_N} chaves:    {TOP_KEYS_FILE}")

if __name__ == "__main__":
    main()
