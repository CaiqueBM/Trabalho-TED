import tkinter as tk
import pandas as pd
import math
import cmath

df_info = pd.read_csv("cabos.csv")
df_entrada = pd.DataFrame(columns=['potencia_ativa',
                                   'fator_potencia',
                                   'comprimento_linha',
                                   'previsao_futura',
                                   'frequencia',
                                   'percentual_carga_leve',
                                   'T_aux',
                                   'perda_corona_max',
                                   'regulacao_maxima',
                                   'rendimento_minimo',
                                   'pressao_atm',
                                   'temperatura_ambiente'])
df_resultados = pd.DataFrame(columns=['cabo', 'bitola', 'numero_circuitos', 'quantidade_subcondutores', 'distancia_subcondutores', 'disposicao_condutores'])
valor_df = 0

def resultado_modelagem():
    # Passar lendo todos os resultados do dataframe e buscar a melhor combinaçao de resultados 
    global df_resultados
    for row in df_resultados:
        print()


def calculo_modelagem(nome_cabo, tensao_otima, corrente_polar, quant_subcondutores, dist_subcondutores):
    global df_info
    global df_resultados
    global df_entrada
    global valor_df

    percentual_carga_leve = float(df_entrada.iloc[0]['percentual_carga_leve'])/100
    T_aux = float(df_entrada.iloc[0]['T_aux'])
    perda_corona_max = float(df_entrada.iloc[0]['perda_corona_max'])
    regulacao_maxima = float(df_entrada.iloc[0]['regulacao_maxima'])/100
    rendimento_minimo = float(df_entrada.iloc[0]['rendimento_minimo'])/100
    pressao_atm = float(df_entrada.iloc[0]['pressao_atm'])
    temperatura_ambiente = float(df_entrada.iloc[0]['temperatura_ambiente'])
    frequencia = float(df_entrada.iloc[0]['frequencia'])
    temp = 228
    E_0 = 8.854187817 * pow(10, -12)
    w = 2 * math.pi * frequencia

    linha_atual = df_info.loc[df_info['Nome'] == nome_cabo]
    diametro_ext = linha_atual.iloc['diametro_condutor']
    raio_medio_geo = linha_atual.iloc['raio_medio']

    if tensao_otima >= 230:
        # Calculo da distancia horizontal - de acordo com a norma ABNT 5422
        distancia_horizontal_min = 0.22 + 0.01 * tensao_otima
        distancia_horizontal_max = (
            0.37 * math.sqrt(frequencia) + 0.0076 * tensao_otima
        )
        if distancia_horizontal_min > distancia_horizontal_max:
            distancia_horizontal = distancia_horizontal_min
        else:
            distancia_horizontal = distancia_horizontal_max
        df_resultados.loc[valor_df, 6] = distancia_horizontal
    elif tensao_otima >= 69:
        # Calculo da distancia vertical - de acordo com a norma ABNT 5422
        distancia_vertical_min = 1
        distancia_vertical_max = (
            0.5 + 0.01 * tensao_otima
        )
        if distancia_vertical_min > distancia_vertical_max:
            distancia_vertical = distancia_vertical_min
        else:
            distancia_vertical = distancia_vertical_max
        df_resultados.loc[valor_df, 6] = distancia_vertical
    else:
        # Calculo da distancia triangular
        distancia_triangular_min = 1
        distancia_triangular_max = (
            0.5 + 0.01 * tensao_otima
        )
        if distancia_vertical_min > distancia_triangular_max:
            distancia_triangular = distancia_triangular_min
        else:
            distancia_triangular = distancia_triangular_max
        df_resultados.loc[valor_df, 6] = distancia_triangular
    
    dmg = (
        distancia_horizontal
        * distancia_horizontal
        * 2
        * distancia_horizontal
    ) ** (1/3)

    
    raio = diametro_ext / 2
    #rmg = raio

    # Calculo da Resistencia Serie (Rs)
    if T_aux > 37.5:
        T_2 = T_aux
        T_1 = 50
        resistencia_cabos = linha_atual[' res50_60']
        resistencia = ((temp + T_2) * resistencia_cabos) / (
        temp + T_1
        )

    elif T_aux <= 37.5:
        T_2 = T_aux
        T_1 = 25
        resistencia_cabos = linha_atual[' res25_60']
        resistencia = ((temp + T_1) * resistencia_cabos) / (
        temp + T_2
        )
    df_resultados.loc[valor_df, 7] = resistencia

    if quant_subcondutores == 1:
        indutancia = 2 * pow(10,-7) * math.ln(dmg/raio_medio_geo)
    elif quant_subcondutores == 2:
        ds = math.sqrt(raio_medio_geo * dist_subcondutores)
        indutancia = 2 * pow(10,-7) * math.log1p(dmg/ds)
    elif quant_subcondutores == 3:
        ds = pow(raio_medio_geo * pow(dist_subcondutores,2),3)
        indutancia = 2 * pow(10,-7) * math.log1p(dmg/ds)
    elif quant_subcondutores == 4:
        ds = math.sqrt(raio_medio_geo * dist_subcondutores)
        indutancia = 2 * pow(10,-7) * math.log1p(dmg/ds)

    return



def verificar_campos():
    global df_info
    global df_resultados
    global df_entrada    
    tensoes_padroes = [6, 11.4, 13.8, 34.5, 69, 88, 138, 230, 345, 440, 500, 600, 750, 1100] #kV
    condicao = False
    valor_df = 0
    valores = [
            potencia_ativa_entry.get(),
            fator_potencia_entry.get(),
            comprimento_entry.get(),
            previsao_aumento_carga_entry.get(),
            frequencia_entry.get(),
            percentual_carga_leve_entry.get(),
            temperatura_operacao_entry.get(),
            perda_efeito_corona_entry.get(),
            regulacao_maxima_entry.get(),
            rendimento_minimo_entry.get(),
            pressao_atm_entry.get(),
            temperatura_ambiente_entry.get()
        ]
    df_entrada.loc[0] = valores

    potencia_ativa = float(df_entrada.iloc[0]['potencia_ativa'])
    fator_potencia = float(df_entrada.iloc[0]['fator_potencia'])
    comprimento_linha = float(df_entrada.iloc[0]['comprimento_linha'])
    previsao_futura = float(df_entrada.iloc[0]['previsao_futura'])/100
    frequencia = float(df_entrada.iloc[0]['frequencia'])

    # Neste exemplo, vamos verificar se o campo "nome" e o campo "idade" estão preenchidos
    if (
        potencia_ativa_entry.get() != ""
        and fator_potencia_entry.get() != ""
        and comprimento_entry.get() != ""
        and frequencia_entry.get() != ""
        and temperatura_operacao_entry.get() != ""
        and temperatura_ambiente_entry.get() != ""
        and pressao_atm_entry.get() != ""
        and percentual_carga_leve_entry.get() != ""
        and regulacao_maxima_entry.get() != ""
        and perda_efeito_corona_entry.get() != ""
        and rendimento_minimo_entry.get() != ""
        and previsao_aumento_carga_entry.get() != ""
    ):
        # Calculo da tensao otima
        potencia_corrigida = potencia_ativa * (1 + previsao_futura)
        tensao_otima = 5.5 * math.sqrt(
            (0.62 * comprimento_linha) + (potencia_corrigida / 100)
        )
        # Escolher a tensao otima padrao
        tensao_otima = min(tensoes_padroes, key=lambda x: abs(x - tensao_otima))

        # Calculo da corrente
        corrente_rect = (
            (potencia_corrigida / 1000)
            / (math.sqrt(3) * tensao_otima * fator_potencia)
            * cmath.exp(-1j * math.acos(fator_potencia))
        )
        corrente_polar = cmath.polar(corrente_rect)

        # Escolha da bitola do condutor e buscando informaçoes do cabo
        for index, row in df_info.iterrows():
            if condicao == False:
                corrente_max = row.iloc[11]
                nome_cabo = row.iloc[0]
                # bitola do condutor
                bitola = row.iloc[2]

                # Linhas acima de 230 kV utilizam condutores geminados
                if tensao_otima >= 230:
                    #Quantidade de subcondutores
                    for quant_subcondutores in range(1, 5):
                        # Verificar se a corrente sera suportada
                        if (int(corrente_polar[0]) / quant_subcondutores) <= corrente_max: 
                            
                            
                            #Distancia de segurança entre subcondutores(Varia 10 a 30 x o diametro)
                            #2, 3 ou 4 subcondutores por fase
                            if (
                                quant_subcondutores == 2
                            and quant_subcondutores == 3
                            and quant_subcondutores == 4
                            ):
                                for dist in range(10,31):
                                    df_resultados.loc[valor_df, 'cabo'] = nome_cabo
                                    df_resultados.loc[valor_df, 'bitola'] = bitola
                                    df_resultados.loc[valor_df, 'quantidade_subcondutores'] = quant_subcondutores
                                    #Numero de circuito é igual a 1
                                    df_resultados.loc[valor_df, 'numero_circuitos'] = "1"
                                    dist_subcondutores = dist
                                    df_resultados.loc[valor_df, 'distancia_subcondutores'] = dist_subcondutores
                                    df_resultados.loc[valor_df, 'disposicao_condutores'] = "Disposiçao horizontal"
                                    calculo_modelagem(nome_cabo, quant_subcondutores, dist_subcondutores, tensao_otima, corrente_polar)

                #Tensao otima abaixo de 230 kV, apenas 1 condutor por fase
                else:
                    df_resultados.loc[valor_df, 'cabo'] = nome_cabo
                    df_resultados.loc[valor_df, 'bitola'] = bitola
                    #Numero de circuito é igual a 1
                    df_resultados.loc[valor_df, 'numero_circuitos'] = "1"
                    #Quantidade de subcondutores igual a 1
                    df_resultados.loc[valor_df, 'quantidade_subcondutores'] = "1"
                    #Distancia de segurança igual a 0
                    df_resultados.loc[valor_df, 'distancia_subcondutores'] = "0"
                    if tensao_otima < 69:
                        df_resultados.loc[valor_df, 'disposicao_condutores'] = "Disposiçao em triangulo"
                    else:
                        df_resultados.loc[valor_df, 'disposicao_condutores'] = "Disposiçao vertical"
                    calculo_modelagem(1, 0, tensao_otima, corrente_polar)


                

            """resposta_texto = "Tensao otima: " + str(tensao_otima) + " kV" + "\n"
            resposta_texto += (
                "Corrente: "
                + str(corrente_polar[0])
                + " <"
                + str(math.degrees(corrente_polar[1]))
                + " kA"
                + "\n"
            )
            resposta_texto += (
                "Distancia horizontal entre fases: " + str(distancia_horizontal) + "\n"
            )
            resposta_texto += (
                "Distancia vertical entre fases: " + str(distancia_vertical) + "\n"
            )
            resposta_texto += "Condutor: " + str(nome_cabo) + "\n"
            resposta_texto += (
                "Distancia horizontal entre fases: " + str(distancia_horizontal) + "\n"
            )
            resposta_texto += (
                "Condutores por fase: " + str(quantidade_condutores_fase)
            ) + "\n"
            resposta_texto += (
                "Distancia entre subcondutores na mesma fase: "
                + str(distancia_condutores_fase)
                + "\n"
            )
            resposta_texto += "Regulacao de tensao: " + str(regulacao_tensao) + "\n"
            resposta_texto += "Perda corona obtida: " + str(perda_corona) + "\n"
            resposta_texto += "Rendimento obtido: " + str(rendimento) + "\n"
            resposta_texto += "Resistencia: " + str(resistencia) + "\n"

            resposta_label.config(text=resposta_texto)
            """
        print()

# Criando a segunda janela
janela = tk.Tk()

# Criando os componentes da interface
potencia_ativa_label = tk.Label(janela, text="Potencia ativa da carga (kW):")
potencia_ativa_label.grid(row=0, column=0, sticky="w")
potencia_ativa_entry = tk.Entry(janela)
potencia_ativa_entry.grid(row=1, column=0)

fator_potencia_label = tk.Label(janela, text="Fator de potencia da carga:")
fator_potencia_label.grid(row=2, column=0, sticky="w")
fator_potencia_entry = tk.Entry(janela)
fator_potencia_entry.grid(row=3, column=0)

comprimento_label = tk.Label(janela, text="Comprimento da linha:")
comprimento_label.grid(row=4, column=0, sticky="w")
comprimento_entry = tk.Entry(janela)
comprimento_entry.grid(row=5, column=0)

frequencia_label = tk.Label(janela, text="Frequencia de operaçao:")
frequencia_label.grid(row=6, column=0, sticky="w")
frequencia_entry = tk.Entry(janela)
frequencia_entry.grid(row=7, column=0)

temperatura_operacao_label = tk.Label(janela, text="Temperatura de operaçao:")
temperatura_operacao_label.grid(row=8, column=0, sticky="w")
temperatura_operacao_entry = tk.Entry(janela)
temperatura_operacao_entry.grid(row=9, column=0)

temperatura_ambiente_label = tk.Label(janela, text="Temperatura ambiente:")
temperatura_ambiente_label.grid(row=10, column=0, sticky="w")
temperatura_ambiente_entry = tk.Entry(janela)
temperatura_ambiente_entry.grid(row=11, column=0)

pressao_atm_label = tk.Label(janela, text="Pressao atmosferica:")
pressao_atm_label.grid(row=12, column=0, sticky="w")
pressao_atm_entry = tk.Entry(janela)
pressao_atm_entry.grid(row=13, column=0)

percentual_carga_leve_label = tk.Label(janela, text="Percentual de carga leve:")
percentual_carga_leve_label.grid(row=0, column=1, sticky="w")
percentual_carga_leve_entry = tk.Entry(janela)
percentual_carga_leve_entry.grid(row=1, column=1)

regulacao_maxima_label = tk.Label(janela, text="Regulaçao de tensao maxima:")
regulacao_maxima_label.grid(row=2, column=1, sticky="w")
regulacao_maxima_entry = tk.Entry(janela)
regulacao_maxima_entry.grid(row=3, column=1)

perda_efeito_corona_label = tk.Label(janela, text="Perda por efeito corona maxima:")
perda_efeito_corona_label.grid(row=4, column=1, sticky="w")
perda_efeito_corona_entry = tk.Entry(janela)
perda_efeito_corona_entry.grid(row=5, column=1)

rendimento_minimo_label = tk.Label(janela, text="Rendimento minimo:")
rendimento_minimo_label.grid(row=6, column=1, sticky="w")
rendimento_minimo_entry = tk.Entry(janela)
rendimento_minimo_entry.grid(row=7, column=1)

previsao_aumento_carga_label = tk.Label(janela, text="Previsao aumento de carga:")
previsao_aumento_carga_label.grid(row=8, column=1, sticky="w")
previsao_aumento_carga_entry = tk.Entry(janela)
previsao_aumento_carga_entry.grid(row=9, column=1)

verificar_button = tk.Button(janela, text="Verificar", command=verificar_campos)
verificar_button.grid(row=17, column=0, columnspan=2)

resposta_label = tk.Label(janela, text="")
resposta_label.grid(row=18, column=0, columnspan=2)


# Iniciando o loop principal da janela
janela.mainloop()
