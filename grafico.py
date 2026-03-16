import sys

# Códigos de cores para o terminal
AZUL = '\033[94m'
VERDE = '\033[92m'
AMARELO = '\033[93m'
RESET = '\033[0m'

print(f"\r{AMARELO}\n--- TOP 15 WORDS IN SHAKESPEARE ---{RESET}")

for line in sys.stdin:
    try:
        # Pega a linha, limpa espaços e quebras de linha invisíveis
        partes = line.strip().split()
        if len(partes) != 2:
            continue
            
        word, count = partes
        count = int(count)
        
        # Cria uma barra visual: cada bloco '█' representa aproximadamente 250 ocorrências
        bar = '█' * (count // 250) 
        
        # Imprime alinhado, voltando ao começo da linha (\r) e com cores
        print(f"\r{AZUL}{word.ljust(12)}{RESET} | {VERDE}{bar}{RESET} ({count})")
        
    except ValueError:
        continue

print(f"\r{AMARELO}--------------------------------------{RESET}\n")
