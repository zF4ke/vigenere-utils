# 🗝️ Vigenère Key Recovery Tools (Português)

Ferramentas Python para criptoanálise e recuperação de chaves da cifra de Vigenère em **português**. 

> **Objetivo:**  
> Testar diversas chaves possíveis e encontrar aquela que, ao decifrar o texto, produz o maior número de palavras reais e coerentes.

**Premissas:**
- O texto cifrado é em português.
- A chave é uma palavra ou expressão do idioma.

---

## 🛠️ Scripts Principais

### `vig_nletras_frases.py` — Análise de frases completas

- **O que faz:**  
  Analisa frases cifradas e testa todas as palavras conhecidas do idioma como chave (entre `MIN_KEY_LEN` e `MAX_KEY_LEN`).
- **Critérios de escolha da melhor chave:**
  - Número de palavras válidas geradas.
  - Soma da frequência das palavras (critério de desempate).

#### Como usar

1. Edite o valor de `CIPHERTEXT` com sua frase cifrada.
2. Ajuste `MIN_KEY_LEN` e `MAX_KEY_LEN` se necessário.
3. Execute:

    ```bash
    cd nletras_frases
    python vig_nletras_frases.py
    ```

#### Saída

- `top_chaves_genericas.txt`: lista com as melhores chaves encontradas.
- Console: exibe as top chaves, número de palavras válidas e a frase decifrada.

---

## 🧩 Scripts para comprimentos isolados

| Script             | Descrição                                 | Wordlist usada           |
|--------------------|-------------------------------------------|--------------------------|
| `vig_6letras.py`   | Analisa palavras cifradas de 6 letras     | `palavras6letras.txt`    |
| `vig_7letras.py`   | Versão para palavras de 7 letras          | `palavras7letras.txt`    |

---

### `vig_nletras.py` — Versão Intermediária

Analisa palavras cifradas de tamanho variável (entre `MIN_KEY_LEN` e `MAX_KEY_LEN`) porém só funciona para ciphertexts com uma única palavra.

---

## 📚 Dicionários Utilizados

- `pt_full_cache.txt`: wordlist com frequência real do idioma (HermitDave). https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2016/pt/pt_full.txt
- `palavras_tx.txt`: lista local de palavras (sem acentos), usada como base.

---

## ⚙️ Requisitos

- Python **3.7+**
- Bibliotecas:
  - `requests`
  - `unicodedata`
  - `re`

---

## 💡 Recomendações

Para recuperar a chave de uma frase cifrada em português, utilize:

```bash
cd nletras_frases
python vig_nletras_frases.py
```

> É o método mais flexível, completo e eficaz.

---

## 👤 Autor

Ferramenta desenvolvida por Pedro Silva, para fins educacionais de criptoanálise da cifra de Vigenère em português.