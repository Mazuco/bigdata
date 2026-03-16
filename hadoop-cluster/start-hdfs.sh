#!/bin/bash

# =================================================================
# Script de Inicialização - HDFS NameNode
# =================================================================
# Objetivo: Garantir que o NameNode seja formatado apenas na primeira
# execução e subir o daemon do HDFS.

set -o errexit

# Configurações de diretórios
readonly DATA_PATH="/opt/hadoop/data/nameNode"
readonly VERSION_FILE="$DATA_PATH/current/VERSION"

# Função simples para mensagens no terminal
log_msg() {
    echo -e "\n[$(date +'%Y-%m-%d %H:%M:%S')] >>> $1"
}

# Verificação de metadados existentes
if [[ ! -f "$VERSION_FILE" ]]; then
    log_msg "Iniciando a primeira configuração: Formatando o NameNode..."
    
    # Executa a formatação de forma silenciosa e forçada
    if hdfs namenode -format -force -nonInteractive; then
        log_msg "Estrutura de diretórios criada com sucesso!"
    else
        log_msg "ERRO: Falha crítica ao formatar o NameNode."
        exit 1
    fi
else
    log_msg "Metadados detectados em $DATA_PATH. Pulando etapa de formatação."
fi

# Inicialização do serviço principal
log_msg "Ativando o serviço HDFS NameNode..."
exec hdfs namenode
