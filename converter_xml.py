import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import os
from openpyxl import load_workbook

# Configurações
arquivo_xml = 'eSocial_xxx.xml'
arquivo_excel = 'XML_Convertido.xlsx'
namespace = {'ns': 'http://www.esocial.gov.br/xxxx'}

# Lista dos códigos de receita para criar as colunas
codigos_receita = [
    "1082-01", "1099-01", "1138-01", "1138-04", "1141-01", 
    "1170-01", "1176-01", "1176-02", "1181-01", "1184-01", 
    "1191-01", "1196-01", "1200-01", "1213-03", "1646-01"
]

# PARTE 1: Processamento do XML
print(f"Iniciando processamento do arquivo: {arquivo_xml}")

try:
    tree = ET.parse(arquivo_xml)
    root = tree.getroot()
except FileNotFoundError:
    print("Erro: Arquivo XML não encontrado.")
    exit()
except ET.ParseError:
    print("Erro: O XML está malformado.")
    exit()

# Lista para armazenar os dados
data = []

# Navegando pelo XML com o namespace e extraindo as informações necessárias
for ideEstab in root.findall('.//ns:ideEstab', namespace):
    cnpj = ideEstab.find('ns:nrInsc', namespace).text  # Extrai o CNPJ
    
    # Aplica o formato XX.XXX.XXX/XXXX-XX ao CNPJ
    cnpj_formatado = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

    # Encontra a tag infoEstab dentro de ideEstab
    infoEstab = ideEstab.find('ns:infoEstab', namespace)

    if infoEstab is not None:
        aliq_rat_element = infoEstab.find('ns:aliqRat', namespace)
        fap_element = infoEstab.find('ns:fap', namespace)
        aliq_rat_ajust_element = infoEstab.find('ns:aliqRatAjust', namespace)

        aliq_rat = float(aliq_rat_element.text) if aliq_rat_element is not None else 0
        fap = float(fap_element.text) if fap_element is not None else 0
        aliq_rat_ajust = float(aliq_rat_ajust_element.text) if aliq_rat_ajust_element is not None else 0
    else:
        aliq_rat, fap, aliq_rat_ajust = 0, 0, 0  # Caso infoEstab não exista

    # Para cada tpCR, vrCR e vrSuspCR em infoCREstab
    for infoCREstab in ideEstab.findall('ns:infoCREstab', namespace):
        codigo_receita = infoCREstab.find('ns:tpCR', namespace).text  # Código de Receita
        
        # Aplica o formato XXXX-XX ao Código de Receita
        codigo_receita_formatado = f"{codigo_receita[:4]}-{codigo_receita[4:]}"

        # Extrai valores, garantindo que existam
        valor_cr_element = infoCREstab.find('ns:vrCR', namespace)
        valor_cr = float(valor_cr_element.text) if valor_cr_element is not None else 0

        valor_suspenso_cr_element = infoCREstab.find('ns:vrSuspCR', namespace)
        valor_suspenso_cr = float(valor_suspenso_cr_element.text) if valor_suspenso_cr_element is not None else 0

        # Cálculo da diferença
        diferenca = valor_cr - valor_suspenso_cr

        # Adiciona as informações na lista de dados
        data.append([cnpj_formatado, codigo_receita_formatado, valor_cr, valor_suspenso_cr, diferenca, 
                     aliq_rat, fap, aliq_rat_ajust])

# Confere se dados foram extraídos
if not data:
    print("Nenhum dado encontrado no XML.")
    exit()

# Cria o DataFrame a partir da lista de dados
df_xml = pd.DataFrame(data, columns=['CNPJ', 'Código de Receita', 'Valor correspondente ao Código de Receita - CR apurado', 
                                 'Valor suspenso correspondente ao Código de Receita - CR apurado', 'Diferença',
                                 'Aliquota RAT', 'FAP', 'Aliquota RAT Ajustada'])

print("Dados extraídos do XML com sucesso.")

# PARTE 2: Processamento do DataFrame e criação do segundo DataFrame
print("Iniciando processamento dos dados...")

# Filtrar os dados apenas para os códigos de receita relevantes
df_filtered = df_xml[df_xml['Código de Receita'].isin(codigos_receita)]

# Criar um DataFrame pivotado com as diferenças
df_pivot = df_filtered.pivot_table(
    index='CNPJ', 
    columns='Código de Receita', 
    values='Diferença', 
    aggfunc='sum', 
    fill_value=0
)

# Renomear as colunas
df_pivot.columns = [f"{col}_Diferença" for col in df_pivot.columns]
df_pivot.reset_index(inplace=True)

# Calcular o total de "Valor correspondente...", "Valor suspenso..." e "Diferença" por filial
df_totals = df_xml.groupby("CNPJ")[[
    "Valor correspondente ao Código de Receita - CR apurado", 
    "Valor suspenso correspondente ao Código de Receita - CR apurado", 
    "Diferença"
]].sum().reset_index()

# Combinar os totais com o dataframe pivotado
df_result = df_totals.merge(df_pivot, on="CNPJ", how="left")

# Preencher valores NaN com zeros para evitar erros nos cálculos
colunas_diferenca = [col for col in df_result.columns if "_Diferença" in col]
for col in colunas_diferenca:
    if col not in df_result.columns:
        df_result[col] = 0
    else:
        df_result[col].fillna(0, inplace=True)

# Adicionar novas colunas calculadas
df_result['Empresa'] = df_result.get('1082-01_Diferença', 0) + df_result.get('1138-01_Diferença', 0)
df_result['Terceiros'] = (
    df_result.get('1170-01_Diferença', 0) + 
    df_result.get('1176-01_Diferença', 0) + 
    df_result.get('1176-02_Diferença', 0) + 
    df_result.get('1181-01_Diferença', 0) + 
    df_result.get('1184-01_Diferença', 0) + 
    df_result.get('1191-01_Diferença', 0) + 
    df_result.get('1196-01_Diferença', 0) + 
    df_result.get('1200-01_Diferença', 0) + 
    df_result.get('1213-03_Diferença', 0)
)
df_result['RAT'] = df_result.get('1141-01_Diferença', 0) + df_result.get('1646-01_Diferença', 0)

print("Processamento dos dados concluído.")

# PARTE 3: Salvar os dois DataFrames em abas diferentes no mesmo arquivo Excel
print(f"Salvando dados no arquivo: {arquivo_excel}")

# Salvar com o ExcelWriter para controlar os nomes das abas
with pd.ExcelWriter(arquivo_excel, engine='openpyxl') as writer:
    df_xml.to_excel(writer, sheet_name='XML', index=False)
    df_result.to_excel(writer, sheet_name='Base por Código e Filial', index=False)

print(f"Arquivo salvo com sucesso! O arquivo contém duas abas:")
print("1. 'XML' - Dados brutos extraídos do XML")
print("2. 'Base por Código e Filial' - Dados processados com pivotamento e cálculos")
print("Processamento concluído com sucesso!")