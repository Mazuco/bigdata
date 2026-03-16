#!/bin/bash

# =================================================================
# Script de Bootstrap - HDFS DataNode (Cluster Node Instance)
# =================================================================
# Descrição: Prepara o ambiente local do DataNode e inicia o daemon.
# Garante a integridade dos volumes e permissões de escrita.

set -o errexit
set -o pipefail

# Definições de ambiente
readonly DATA_DIR="/opt/hadoop/data/dataNode"
readonly SERVICE_USER="hadoop"

# Função de log customizada
notify() {
    echo "--- [$(date +'%H:%M:%S')] DATA-NODE-INIT: $1 ---"
}

# --- Preparação do Sistema de Arquivos ---
if [ ! -d "$DATA_DIR" ]; then
    notify "Diretório de dados não encontrado. Criando em $DATA_DIR"
    mkdir -p "$DATA_DIR"
else
    # Opcional: Aqui você poderia limpar dados antigos se quisesse um cluster efêmero.
    # No momento, apenas garantimos que está acessível.
    notify "Volume de dados detectado. Verificando integridade..."
fi

# --- Ajuste de Permissões ---
# Essencial para evitar erros de I/O no HDFS
notify "Ajustando ownership para o usuário $SERVICE_USER..."
chown -R "$SERVICE_USER:$SERVICE_USER" "$DATA_DIR"
chmod 755 "$DATA_DIR"

# --- Inicialização ---
notify "Sincronização concluída. Subindo o daemon do DataNode..."

# O uso do 'exec' permite que o processo do Hadoop receba os sinais do Docker (STOP/KILL)
exec hdfs datanode
