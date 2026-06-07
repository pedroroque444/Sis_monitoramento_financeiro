import csv
import sqlite3
from banco_dados import conectar

def importar_gastos_csv(caminho_arquivo):
    """Lê planilhas bancárias externas e popula automaticamente o banco local."""
    conn = conectar()
    cursor = conn.cursor()
    
    with open(caminho_arquivo, mode='r', encoding='utf-8') as arquivo:
        leitor = csv.DictReader(arquivo) 
        for linha in leitor:
            try:
                desc = linha['Descricao']
                valor_banco = float(linha['Valor'].replace(',', '.'))
                
                # Identifica registros de gastos (saídas de dinheiro representadas por números negativos)
                if valor_banco < 0:
                    valor_positivo = abs(valor_banco)
                    cursor.execute("""
                        INSERT INTO transacoes (descricao, valor, categoria) 
                        VALUES (?, ?, 'Importado')
                    """, (desc, valor_positivo))
            except (KeyError, ValueError):
                continue
                
    conn.commit()
    conn.close()

def exportar_gastos_csv(caminho_salvamento):
    """Extrai os dados locais e exporta um relatório financeiro estruturado compatível com Excel."""
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("SELECT descricao, valor, categoria, data FROM transacoes ORDER BY id ASC")
    todos_gastos = cursor.fetchall()
    
    with open(caminho_salvamento, mode='w', newline='', encoding='utf-8') as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(['Descricao', 'Valor', 'Categoria', 'Data_Registro'])
        
        for gasto in todos_gastos:
            escritor.writerow(gasto)
            
    conn.close()