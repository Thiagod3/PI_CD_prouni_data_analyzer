import pandas as pd
import matplotlib.pyplot as plt
import glob
import re
from matplotlib.ticker import MaxNLocator


# Função para ler os cursos do arquivo .txt
def ler_cursos_stem():
    with open('cursos_stem.txt', 'r', encoding='utf-8') as file:
        cursos_stem = [line.strip().lower() for line in file.readlines()]
    return cursos_stem

def main():
    arquivos = glob.glob("prouni_*.csv")

    dfs = []


    for arquivo in arquivos:
        print(f"Lendo {arquivo}...")

        municipios_desejados = ["SANTOS", "SAO VICENTE", "PRAIA GRANDE", "CUBATAO", "GUARUJA", "santos", "sao vicente", "praia grande", "cubatao", "guaruja"]

        cursos_stem = ler_cursos_stem()
        try:
            df = pd.read_csv(arquivo, sep=",", encoding="utf-8-sig")
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
    totais = homens + mulheres

    # Calcular porcentagens de homens e mulheres
    porcentagens_homens = (homens / totais) * 100
    porcentagens_mulheres = (mulheres / totais) * 100

    # Criar o gráfico de barras lado a lado
    fig, ax = plt.subplots(figsize=(16, 9))

    # Definir a largura das barras
    bar_width = 0.35

    # Posição no eixo X
    anos = bolsas_por_ano_sexo.index
    indices = range(len(anos))

    # Plotar as barras (lado a lado)
    bar1 = ax.bar([i - bar_width / 2 for i in indices], homens, width=bar_width, label='Homens', color='blue')
    bar2 = ax.bar([i + bar_width / 2 for i in indices], mulheres, width=bar_width, label='Mulheres', color='pink')

    # Adicionar as porcentagens nas barras (acima de cada barra)
    for i, year in enumerate(anos):
        ax.text(i - bar_width / 2, homens.iloc[i] + 5, f'{homens.iloc[i]} ({porcentagens_homens.iloc[i]:.1f}%)',
                ha='center', va='bottom', color='black', fontsize=8, rotation=0)

        ax.text(i + bar_width / 2, mulheres.iloc[i] + 5, f'{mulheres.iloc[i]} ({porcentagens_mulheres.iloc[i]:.1f}%)',
                ha='center', va='bottom', color='black', fontsize=8, rotation=0)

        # Total centralizado no meio das barras
        ax.text(i, max(homens.iloc[i], mulheres.iloc[i]) + 40,
                f'Total = {totais.iloc[i]}', ha='center', va='bottom', color='black', fontsize=9, fontweight='bold')

    # Configurações do gráfico
    ax.set_xticks(indices)
    ax.set_xticklabels(anos, rotation=0)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlabel('Ano')
    ax.set_ylabel('Quantidade de Bolsas')
    ax.set_title('Quantidade de Bolsas Masculinas x Femininas por Ano (Cursos STEM)')
    ax.legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
