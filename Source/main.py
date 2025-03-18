import pandas as pd
import matplotlib.pyplot as plt
import glob
import re


# Função para ler os cursos do arquivo .txt
def ler_cursos_stem():
    with open('cursos_stem.txt', 'r', encoding='utf-8') as file:
        cursos_stem = [line.strip().lower() for line in file.readlines()]
    return cursos_stem

def main():
    arquivos = glob.glob("pda-prouni-*.csv")

    dfs = []


    for arquivo in arquivos:
        print(f"Lendo {arquivo}...")

        municipios_desejados = ["SANTOS", "SAO VICENTE", "PRAIA GRANDE", "CUBATAO", "GUARUJA"]

        cursos_stem = ler_cursos_stem()
        try:
            df = pd.read_csv(arquivo, sep=";", encoding="utf-8-sig")
        except UnicodeDecodeError:
            df = pd.read_csv(arquivo, sep=";", encoding="latin1")

        df.columns = df.columns.str.strip()
        print(f"\n Colunas de {arquivo}", df.columns.tolist(), "\n")
        if "UF_BENEFICIARIO" in df.columns:
            df.rename(columns={"UF_BENEFICIARIO": "SIGLA_UF_BENEFICIARIO_BOLSA"}, inplace=True)
        if "SEXO_BENEFICIARIO" in df.columns:
            df.rename(columns={"SEXO_BENEFICIARIO": "SEXO_BENEFICIARIO_BOLSA"}, inplace=True)
        if "MUNICIPIO_BENEFICIARIO" in df.columns:
            df.rename(columns={"MUNICIPIO_BENEFICIARIO": "MUNICIPIO_BENEFICIARIO_BOLSA"}, inplace=True)

        df = df[df["SIGLA_UF_BENEFICIARIO_BOLSA"] == "SP"]
        df = df[df["MUNICIPIO_BENEFICIARIO_BOLSA"].isin(municipios_desejados)]
        # Escapando os caracteres especiais de cada termo na lista
        cursos_stem_escapados = [re.escape(curso) for curso in cursos_stem]

        # Agora criando o filtro
        df = df[df["NOME_CURSO_BOLSA"].str.contains('|'.join(cursos_stem_escapados), case=False, na=False)]


        dfs.append(df)


    df_total = pd.concat(dfs)
    # Agrupando por ano e sexo
    bolsas_por_ano_sexo = df_total.groupby(
        ["ANO_CONCESSAO_BOLSA", "SEXO_BENEFICIARIO_BOLSA"]).size()

    # Calculando a porcentagem dentro de cada ano
    bolsas_por_ano_sexo_percent = bolsas_por_ano_sexo.groupby(level=0).apply(lambda x: 100 * x / float(x.sum()))

    # Reorganizando os dados para plotar
    bolsas_por_ano_sexo = bolsas_por_ano_sexo.unstack(fill_value=0)
    bolsas_por_ano_sexo_percent = bolsas_por_ano_sexo_percent.unstack(fill_value=0)

    # Preparando os dados de homens e mulheres para o gráfico
    homens = bolsas_por_ano_sexo['M']
    mulheres = bolsas_por_ano_sexo['F']

    # Calcular os totais de bolsas para cada ano
    totais = homens + mulheres

    # Calcular porcentagens de homens e mulheres
    porcentagens_homens = (homens / totais) * 100
    porcentagens_mulheres = (mulheres / totais) * 100

    # Criar o gráfico de barras empilhadas
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plotar as barras empilhadas (Homens e Mulheres)
    ax.bar(bolsas_por_ano_sexo.index, homens, label='Homens', color='blue')
    ax.bar(bolsas_por_ano_sexo.index, mulheres, bottom=homens, label='Mulheres', color='pink')

    # Adicionar as porcentagens nas barras
    for i, year in enumerate(bolsas_por_ano_sexo.index):
        ax.text(year, homens.iloc[i] + 5, f'{porcentagens_homens.iloc[i]:.1f}% H', ha='center', va='bottom', color='black')
        ax.text(year, homens.iloc[i] + mulheres.iloc[i] + 5, f'{porcentagens_mulheres.iloc[i]:.1f}% F', ha='center', va='bottom', color='black')

    # Configurações do gráfico
    ax.set_ylabel('Quantidade de Bolsas')
    ax.set_title('Quantidade de Bolsas por Sexo por Ano')
    ax.legend()

    # Mostrar o gráfico
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
