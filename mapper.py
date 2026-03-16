#!/usr/bin/env python3
import sys
import re

# Input: Linhas de texto
# Output: Pares (palavra, 1) já limpos e em minúsculas

for line in sys.stdin:
    # Remove espaços em branco nas pontas e converte tudo para minúsculo
    line = line.strip().lower()
    
    # Extrai apenas palavras (ignorando vírgulas, pontos, aspas, etc)
    words = re.findall(r'\b\w+\b', line)
    
    for word in words:
        print(f"{word}\t1")
