import tkinter as tk
import pandas as pd
import math
import cmath
import csv

with open('cabos.csv', 'r') as arquivo_csv:
    # Crie um objeto leitor do CSV
    leitor_csv = csv.reader(arquivo_csv)
    linhas_csv = list(leitor_csv)

# Crie um DataFrame a partir das linhas do CSV
df_info = pd.DataFrame(linhas_csv[1:], columns=linhas_csv[0])

df_entrada = pd.DataFrame(
    columns=[
        "potencia_ativa",
        "fator_potencia",
        "comprimento_linha",
        "previsao_futura",
        "frequencia",
        "percentual_carga_leve",
        "T_aux",
        "perda_corona_max",
        "regulacao_maxima",
        "rendimento_minimo",
        "pressao_atm",
        "temperatura_ambiente",
    ]
)

df_final = pd.DataFrame()

df_resultados = pd.DataFrame()
valor_df = 0
regulacao_anterior = None
regulacao_recente = None
perda_corona_anterior = None
perda_corona_recente = None
rendimento_anterior = None
rendimento_recente = None
corrente_recente = math.inf
dif_corrente_recente = None
nome_cabo_recente = None
quant_subcondutores_recente = None

def resultado_modelagem(tensao_otima, corrente_rect, corrente_polar):
    # Passar lendo todos os resultados do dataframe e buscar a melhor combinaçao de resultados
    global df_resultados
    global df_entrada
    global regulacao_recente
    global regulacao_anterior
    global perda_corona_recente
    global perda_corona_anterior
    global rendimento_recente
    global rendimento_anterior
    global corrente_recente
    global dif_corrente_recente
    global nome_cabo_recente
    global quant_subcondutores_recente
    global df_final
    
    perda_corona_max = float(df_entrada.iloc[0]["perda_corona_max"])
    regulacao_maxima = float(df_entrada.iloc[0]["regulacao_maxima"])
    rendimento_minimo = float(df_entrada.iloc[0]["rendimento_minimo"])
    tamanho = len(df_resultados)
    #for index, row in reversed(list(df_resultados.iterrows())):
    for index, row in df_resultados.iterrows():
        nome_cabo_atual = row["cabo"]
        regulacao = row["regulacao"]
        perda_corona = row["perda_corona"]
        rendimento = row["rendimento"]
        max_corrente = row["max_corrente"]
        quant_subcondutores = row["quantidade_subcondutores"]
        distancia_subcondutores = row["distancia_subcondutores"]
        disposicao_condutores = row["disposicao_condutores"]
        distancia_entre_fases = row["distancia_entre_fases"]
        
        corrente_necessaria_por_cabo = ((corrente_polar[0] * 1000) / quant_subcondutores)
         
        #dif_corrente = float(max_corrente) - corrente_necessaria_por_cabo
        #if dif_corrente_recente is None or dif_corrente < dif_corrente_recente:      
        if (corrente_necessaria_por_cabo) < float(max_corrente):
            #Verificar os requisitos do projeto
            if regulacao < regulacao_maxima:
                if perda_corona < perda_corona_max:
                    if rendimento > rendimento_minimo:
                        #if nome_cabo_atual == "Redwing":
                            #Verificar o melhor resultado possivel
                        nome_cabo_recente = nome_cabo_atual
                        regulacao_recente = regulacao
                        perda_corona_recente = perda_corona
                        rendimento_recente = rendimento
                        corrente_recente = max_corrente
                        quant_subcondutores_recente = quant_subcondutores
                        corrente_necessaria_recente = corrente_necessaria_por_cabo
                        disposicao_recente = disposicao_condutores
                        distancia_fases_recente = distancia_entre_fases
                        distancia_subcondutores_recente = distancia_subcondutores
                        

    df_resultados.to_excel('E:\Trabalho TED/resultados.xlsx', index=False)
  
    
    resposta_texto = "Tensao otima: " + str(tensao_otima) + " kV" + "\n"
    resposta_texto += (
        "Disposiçao dos condutores: " + str(disposicao_recente) + "\n"
    )
    resposta_texto += (
        "Distancia entre fases: " + str(round(distancia_fases_recente, 2)) + " m" + "\n"
    )
    resposta_texto += (
        "Condutor: " + str(nome_cabo_recente) + "\n"
    )
    resposta_texto += (
        "Condutores por fase: " + str(quant_subcondutores_recente) + "\n"
    )
    resposta_texto += (
        "Distancia entre subcondutores: " + str(round(distancia_subcondutores_recente, 2 )) + " cm" + "\n"
    )
    resposta_texto += "Regulacao de tensao: " + str(round(regulacao_recente, 2)) + " %" + "\n"
    resposta_texto += "Perda corona obtida: " + str(round(perda_corona_recente, 2)) + " kW/km" + "\n"
    resposta_texto += "Rendimento obtido: " + str(round(rendimento_recente, 2)) + " %"
        
    resposta_label.config(text=resposta_texto)
    return
        

def calculo_modelagem(
    nome_cabo, bitola, corrente_max, quant_subcondutores, dist_subcondutores, quant_circuitos, tensao_otima, corrente_polar, potencia_corrigida, index
):
    global df_info
    global df_resultados
    global df_entrada
    global valor_df
    global regulacao_anterior
    global perda_corona_anterior
    global rendimento_anterior
    condicao = 0

    dist_subcondutores = dist_subcondutores * (10 ** (-2))

    percentual_carga_leve = float(df_entrada.iloc[0]["percentual_carga_leve"]) / 100
    T_aux = float(df_entrada.iloc[0]["T_aux"])
    perda_corona_max = float(df_entrada.iloc[0]["perda_corona_max"])
    regulacao_maxima = float(df_entrada.iloc[0]["regulacao_maxima"]) / 100
    rendimento_minimo = float(df_entrada.iloc[0]["rendimento_minimo"]) / 100
    pressao_atm = float(df_entrada.iloc[0]["pressao_atm"])
    temperatura_ambiente = float(df_entrada.iloc[0]["temperatura_ambiente"])
    frequencia = float(df_entrada.iloc[0]["frequencia"])
    comprimento_linha = float(df_entrada.iloc[0]["comprimento_linha"])
    regulacao_maxima = regulacao_maxima * 100
    rendimento_minimo = rendimento_minimo *100

    temp = 228
    E_0 = 8.854187817 * (10 ** (-12))
    w = 2 * math.pi * frequencia
    resistencia = 0
    indutancia = 0
    capacitancia = 0
    distancia_entre_fases = 0
    disposicao_condutores=""

    linha_atual = df_info.loc[df_info["nome"] == nome_cabo]
    diametro_ext = float(linha_atual.loc[index, "diametro_condutor"])
    raio_medio_geo = float(linha_atual.loc[index, "raio_medio"])

    if tensao_otima >= 230:
        # Calculo da distancia horizontal - de acordo com a norma ABNT 5422
        distancia_horizontal_min = 0.22 + 0.01 * tensao_otima
        distancia_horizontal_max = 0.37 * math.sqrt(frequencia) + 0.0076 * tensao_otima
        if distancia_horizontal_min > distancia_horizontal_max:
            distancia_entre_fases = distancia_horizontal_min
        else:
            distancia_entre_fases = distancia_horizontal_max
        disposicao_condutores = "Horizontal"
        
    elif tensao_otima >= 69:
        # Calculo da distancia vertical - de acordo com a norma ABNT 5422
        distancia_vertical_min = 1
        distancia_vertical_max = 0.5 + 0.01 * tensao_otima
        if distancia_vertical_min > distancia_vertical_max:
            distancia_entre_fases = distancia_vertical_min
        else:
            distancia_entre_fases = distancia_vertical_max
        df_resultados.loc[valor_df, 6] = distancia_entre_fases
        disposicao_condutores = "Vertical"

    else:
        # Calculo da distancia triangular
        distancia_triangular_min = 1
        distancia_triangular_max = 0.5 + 0.01 * tensao_otima
        if distancia_triangular_min > distancia_triangular_max:
            distancia_entre_fases = distancia_triangular_min
        else:
            distancia_entre_fases = distancia_triangular_max
        df_resultados.loc[valor_df, 6] = distancia_entre_fases
        disposicao_condutores = "Triangular"

    dmg = (
            distancia_entre_fases * distancia_entre_fases * 2 * distancia_entre_fases
        ) ** (1 / 3)

    raio = (float(diametro_ext) * (10 ** (-3))) / 2    #metros

    # Calculo da Resistencia Serie (Rs)
    if T_aux > 37.5:
        T_2 = T_aux
        T_1 = 50
        resistencia_cabos = linha_atual.loc[index, "res5060"]
        resistencia = ((temp + T_2) * float(resistencia_cabos)) / (temp + T_1)

    elif T_aux <= 37.5:
        T_2 = T_aux
        T_1 = 25
        resistencia_cabos = linha_atual.loc[index, "res2560"]
        resistencia = ((temp + T_1) * float(resistencia_cabos)) / (temp + T_2)

    rmg = raio
    # Calculo da Indutancia
    if quant_subcondutores == 1:
        indutancia = 2 * pow(10, -7) * math.log(dmg / raio_medio_geo)
        capacitancia = (2 * math.pi * E_0) / (math.log(dmg / rmg))
    elif quant_subcondutores == 2:
        ds_L = math.sqrt(raio_medio_geo * dist_subcondutores)
        indutancia = (2 * (10 ** (-7)) * math.log(dmg / ds_L)) * (10 ** 3)
        ds_C = math.sqrt(rmg * dist_subcondutores)
        capacitancia = (2 * math.pi * E_0) / (math.log(dmg / ds_C)) * (10 ** 3)
    elif quant_subcondutores == 3:
        ds_L = pow(raio_medio_geo * pow(dist_subcondutores, 2), 1 / 3)
        indutancia = 2 * pow(10, -7) * math.log(dmg / ds_L) * (10 ** 3)
        ds_C = pow(rmg * pow(dist_subcondutores, 2), 1 / 3)
        capacitancia = (2 * math.pi * E_0) / (math.log(dmg / ds_C)) * (10 ** 3)
    elif quant_subcondutores == 4:
        ds_L = 1.09 * pow(raio_medio_geo * pow(dist_subcondutores, 3), 1 / 4)
        indutancia = 2 * pow(10, -7) * math.log(dmg / ds_L) * (10 ** 3)
        ds_C = 1.09 * pow(rmg * pow(dist_subcondutores, 3), 1 / 4)
        capacitancia = (2 * math.pi * E_0) / (math.log(dmg / ds_C)) * (10 ** 3)

    # Calculo dos parametros ABCD
    zs = resistencia + (1j * w * indutancia)
    ysh = 1j * w * capacitancia
    zc = cmath.sqrt(zs / ysh)
    gama = cmath.sqrt(zs * ysh)

    A = cmath.cosh(gama * comprimento_linha)
    B = zc * (cmath.sinh(gama * comprimento_linha))
    C = (1 / zc) * cmath.sinh(gama * comprimento_linha)
    D = A

    if comprimento_linha < 80 or tensao_otima < 69:
        # Linha Curta
        ir = corrente_polar[0] / math.sqrt(3)
        vr = tensao_otima * pow(10, 3) / math.sqrt(3)
        vs = tensao_otima * pow(10, 3) + ir * zs  # Fase - neutro
        i_s = ir
    elif comprimento_linha >= 80 and comprimento_linha <= 240:
        # Linha Media
        ir = corrente_polar[0] / math.sqrt(3)
        vr = tensao_otima * pow(10, 3) / math.sqrt(3)
        vs = tensao_otima * pow(10, 3) + ir * zs  # Fase - neutro
        i_s = ir
    else:
        # Linha Longa
        ir_p = cmath.rect(corrente_polar[0], corrente_polar[1])
        ir = (ir_p * (10**3)) / cmath.sqrt(3)
        vr = (tensao_otima * (10**3)) / cmath.sqrt(3)

    vs_cp = A * vr + B * ir
    is_cp = C * vr + D * ir
    vs_cl = A * vr + B * ir * percentual_carga_leve
    is_cl = C * vr + D * ir * percentual_carga_leve

    regulacao = abs((abs(vs_cl) - abs(vs_cp)) / abs(vs_cp)) * 100

    # Calculo da perda por corona ( Gradiente de potencial)
    # Calculo tensao critica disruptiva
    e0 = 21.1 * (10**3)
    densidade_relativa = (3.9211 * pressao_atm) / (273 + temperatura_ambiente)
    for fator_irregularidade_condutor in range(80, 87, 2):
        #Calculo da resistencia equivalente para 2, 3 ou 4 subcondutores
        if quant_subcondutores != 1: 
            a = 0.01  # valor mínimo inicial de x
            b = 10.0  # valor máximo inicial de x
            precision = 0.0001  # precisão desejada
            def f(x):
                return dmg / x - ((dmg / ds_C) ** ((quant_subcondutores * raio) / x))
            while abs(b - a) > precision:
                c = (a + b) / 2
                
                if f(c) == 0:
                    break
                elif f(a) * f(c) < 0:
                    b = c
                else:
                    a = c
            x = (a + b) / 2
            req = x * 100 #cm
        else:
            req = raio * 100 #cm
        
        mc = fator_irregularidade_condutor / 100
        vo = e0 * densidade_relativa * req * mc * math.log((dmg * 100) / req)
        
            
        if disposicao_condutores == "Horizontal":
            v0cc = vo * 0.96
            v0cl = vo * 1.06
            if frequencia >= 25 and frequencia <= 120 and req > 0.25 and (tensao_otima/vo) > 1.8:
                perda_corona = (241 / densidade_relativa) * (frequencia + 25) * math.sqrt(req / distancia_entre_fases) * ((tensao_otima - vo) ** 2) * (10 ** 5)
            else:
                if ((tensao_otima * 1000) / v0cl) <= 0.6:
                    fator_corona_cl = 0.012
                elif ((tensao_otima * 1000) / v0cl) > 0.6 and ((tensao_otima * 1000) / v0cl) <= 0.8:
                    fator_corona_cl = 0.018
                elif ((tensao_otima * 1000) / v0cl) > 0.8 and ((tensao_otima * 1000) / v0cl) <= 1.0:
                    fator_corona_cl = 0.05
                elif ((tensao_otima * 1000) / v0cl) > 1.0 and ((tensao_otima * 1000) / v0cl) <= 1.2:
                    fator_corona_cl = 0.08
                elif ((tensao_otima * 1000) / v0cl) > 1.2 and ((tensao_otima * 1000) / v0cl) <= 1.4:
                    fator_corona_cl = 0.3
                elif ((tensao_otima * 1000) / v0cl) > 1.4 and ((tensao_otima * 1000) / v0cl) <= 1.5:
                    fator_corona_cl = 1.0
                elif ((tensao_otima * 1000) / v0cl) > 1.5 and ((tensao_otima * 1000) / v0cl) <= 1.8:
                    fator_corona_cl = 3.5
                elif ((tensao_otima * 1000) / v0cl) > 1.8 and ((tensao_otima * 1000) / v0cl) <= 2.0:
                    fator_corona_cl = 6.0
                else:
                    fator_corona_cl = 8.0

                if ((tensao_otima * 1000) / v0cc) <= 0.6:
                    fator_corona_cc = 0.012
                elif ((tensao_otima * 1000) / v0cc) > 0.6 and ((tensao_otima * 1000) / v0cc) <= 0.8:
                    fator_corona_cc = 0.018
                elif ((tensao_otima * 1000) / v0cc) > 0.8 and ((tensao_otima * 1000) / v0cc) <= 1.0:
                    fator_corona_cc = 0.05
                elif ((tensao_otima * 1000) / v0cc) > 1.0 and ((tensao_otima * 1000) / v0cc) <= 1.2:
                    fator_corona_cc = 0.08
                elif ((tensao_otima * 1000) / v0cc) > 1.2 and ((tensao_otima * 1000) / v0cc) <= 1.4:
                    fator_corona_cc = 0.3
                elif ((tensao_otima * 1000) / v0cc) > 1.4 and ((tensao_otima * 1000) / v0cc) <= 1.5:
                    fator_corona_cc = 1.0
                elif ((tensao_otima * 1000) / v0cc) > 1.5 and ((tensao_otima * 1000) / v0cc) <= 1.8:
                    fator_corona_cc = 3.5
                elif ((tensao_otima * 1000) / v0cc) > 1.8 and ((tensao_otima * 1000) / v0cc) <= 2.0:
                    fator_corona_cc = 6.0
                else:
                    fator_corona_cc = 8.0
                
                fccl = fator_corona_cl
                fccc = fator_corona_cc
                
                perda_corona_cl = ((1.11066 * (10 ** (-4)))/((math.log((distancia_entre_fases * 100)/ req)) ** (2))) * frequencia * (((tensao_otima)/math.sqrt(3)) ** 2) * fccl
                perda_corona_cc = ((1.11066 * (10 ** (-4)))/((math.log((distancia_entre_fases * 100)/ req)) ** (2))) * frequencia * (((tensao_otima)/math.sqrt(3)) ** 2) * fccc
                perda_corona = 3 * (perda_corona_cl + perda_corona_cc)
                
        # Calculo Rendimento
        potencia_emissor = 3 * (vs_cp * is_cp)
        potencia_emissor_polar = cmath.polar(potencia_emissor)
        perda_corona_total = (perda_corona * comprimento_linha) * (10 ** 3)
        perda_joule = resistencia * comprimento_linha * ((corrente_polar[0]) ** 2) * (10 ** 6)
        rendimento = (((potencia_emissor_polar[0]) / (perda_corona_total + potencia_emissor_polar[0] + perda_joule ))) * 100
        
        df_resultados.loc[valor_df, "tensao"] = tensao_otima
        df_resultados.loc[valor_df, "cabo"] = nome_cabo
        df_resultados.loc[valor_df, "bitola"] = bitola
        df_resultados.loc[valor_df, "quantidade_subcondutores"] = quant_subcondutores
        df_resultados.loc[valor_df, "numero_circuitos"] = quant_circuitos            # Numero de circuito é igual a 1
        df_resultados.loc[valor_df, "distancia_subcondutores"] = dist_subcondutores
        df_resultados.loc[valor_df, "disposicao_condutores"] = "Horizontal"
        df_resultados.loc[valor_df, "disposicao_condutores"] = disposicao_condutores
        df_resultados.loc[valor_df, "distancia_entre_fases"] = distancia_entre_fases
        df_resultados.loc[valor_df, "regulacao"] = regulacao
        df_resultados.loc[valor_df, "perda_corona"] = perda_corona
        df_resultados.loc[valor_df, "rendimento"] = rendimento
        df_resultados.loc[valor_df, "max_corrente"] = corrente_max
        
        valor_df += 1
        #if regulacao < regulacao_maxima and perda_corona < perda_corona_max and rendimento > rendimento_minimo:
                
            
       

    return


def verificar_campos():
    global df_info
    global df_resultados
    global df_entrada
    global regulacao_recente
    global perda_corona_recente
    global rendimento_recente

    tensoes_padroes = [
        6,
        11.4,
        13.8,
        34.5,
        69,
        88,
        138,
        230,
        345,
        440,
        500,
        600,
        750,
        1100,
    ]  # kV
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
        temperatura_ambiente_entry.get(),
    ]
    df_entrada.loc[0] = valores

    potencia_ativa = float(df_entrada.iloc[0]["potencia_ativa"])
    fator_potencia = float(df_entrada.iloc[0]["fator_potencia"])
    comprimento_linha = float(df_entrada.iloc[0]["comprimento_linha"])
    previsao_futura = float(df_entrada.iloc[0]["previsao_futura"]) / 100
    frequencia = float(df_entrada.iloc[0]["frequencia"])

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
        potencia_corrigida = potencia_ativa * (1 + previsao_futura)  #kW
        tensao_otima = 5.5 * math.sqrt(
            (0.62 * comprimento_linha) + (potencia_corrigida / 100) #kV
        )
        # Escolher a tensao otima padrao
        tensao_otima = min(tensoes_padroes, key=lambda x: abs(x - tensao_otima)) #kV

        # Calculo da corrente
        corrente_rect = (
            (potencia_corrigida / 1000)
            / (math.sqrt(3) * tensao_otima * fator_potencia)
            * cmath.exp(-1j * math.acos(fator_potencia))
        )
        corrente_polar = cmath.polar(corrente_rect) #kA
        corrente_modulo = abs(corrente_rect)
        corrente_angle = math.degrees(cmath.phase(corrente_rect))

        # Escolha da bitola do condutor e buscando informaçoes do cabo
        for index, row in df_info.iterrows():
            if condicao == False:
                corrente_max = row.iloc[11]
                nome_cabo = row.iloc[0]
                # bitola do condutor
                bitola = row.iloc[2]
                # Linhas acima de 230 kV utilizam condutores geminados
                #if tensao_otima >= 230:
                    # Quantidade de subcondutores
                for quant_subcondutores in range(1, 5):
                    # Verificar se a corrente sera suportada
                    if (int(corrente_polar[0]) * 1000 / quant_subcondutores) <= float(
                        corrente_max
                    ):
                        # Distancia de segurança entre subcondutores(Varia 10 a 30 x o diametro)
                        # 2, 3 ou 4 subcondutores por fase
                        if (
                            quant_subcondutores == 2
                            or quant_subcondutores == 3
                            or quant_subcondutores == 4
                        ):
                            for dist in range(10, 31, 5):
                                numero_circuitos = "1"
                                dist_subcondutores = dist
                                
                                calculo_modelagem(
                                    nome_cabo,
                                    bitola,
                                    corrente_max,
                                    quant_subcondutores,
                                    dist_subcondutores,
                                    numero_circuitos,
                                    tensao_otima,
                                    corrente_polar,
                                    potencia_corrigida,
                                    index
                                )
                        else:  #Para apenas 1 subcondutor acima de 230 kV
                            dist_subcondutores = 0
                            numero_circuitos = "1"

                            calculo_modelagem(
                                    nome_cabo,
                                    bitola,
                                    corrente_max,
                                    quant_subcondutores,
                                    dist_subcondutores,
                                    numero_circuitos,
                                    tensao_otima,
                                    corrente_polar,
                                    potencia_corrigida,
                                    index
                                )

        resultado_modelagem(tensao_otima, corrente_rect, corrente_polar)

# Criando a segunda janela
janela = tk.Tk()

# Criando os componentes da interface
potencia_ativa_label = tk.Label(janela, text="Potencia ativa da carga (kW):")
potencia_ativa_label.grid(row=0, column=0, sticky="w")
valor_entry = tk.StringVar(value="220000")
potencia_ativa_entry = tk.Entry(janela, textvariable=valor_entry)
potencia_ativa_entry.grid(row=1, column=0)

fator_potencia_label = tk.Label(janela, text="Fator de potencia da carga:")
fator_potencia_label.grid(row=2, column=0, sticky="w")
valor_entry = tk.StringVar(value="0.95")
fator_potencia_entry = tk.Entry(janela, textvariable=valor_entry)
fator_potencia_entry.grid(row=3, column=0)

comprimento_label = tk.Label(janela, text="Comprimento da linha (km):")
comprimento_label.grid(row=4, column=0, sticky="w")
valor_entry = tk.StringVar(value="300")
comprimento_entry = tk.Entry(janela, textvariable=valor_entry)
comprimento_entry.grid(row=5, column=0)

frequencia_label = tk.Label(janela, text="Frequencia de operação (Hz):")
frequencia_label.grid(row=6, column=0, sticky="w")
valor_entry = tk.StringVar(value="60")
frequencia_entry = tk.Entry(janela, textvariable=valor_entry)
frequencia_entry.grid(row=7, column=0)

temperatura_operacao_label = tk.Label(janela, text="Temperatura de operação (°C):")
temperatura_operacao_label.grid(row=8, column=0, sticky="w")
valor_entry = tk.StringVar(value="46")
temperatura_operacao_entry = tk.Entry(janela, textvariable=valor_entry)
temperatura_operacao_entry.grid(row=9, column=0)

temperatura_ambiente_label = tk.Label(janela, text="Temperatura ambiente (°C):")
temperatura_ambiente_label.grid(row=10, column=0, sticky="w")
valor_entry = tk.StringVar(value="25")
temperatura_ambiente_entry = tk.Entry(janela, textvariable=valor_entry)
temperatura_ambiente_entry.grid(row=11, column=0)

pressao_atm_label = tk.Label(janela, text="Pressao atmosferica (cmHg):")
pressao_atm_label.grid(row=12, column=0, sticky="w")
valor_entry = tk.StringVar(value="76")
pressao_atm_entry = tk.Entry(janela, textvariable=valor_entry)
pressao_atm_entry.grid(row=13, column=0)

percentual_carga_leve_label = tk.Label(janela, text="Percentual de carga leve:")
percentual_carga_leve_label.grid(row=0, column=1, sticky="w")
valor_entry = tk.StringVar(value="10")
percentual_carga_leve_entry = tk.Entry(janela, textvariable=valor_entry)
percentual_carga_leve_entry.grid(row=1, column=1)

regulacao_maxima_label = tk.Label(janela, text="Regulação de tensao máxima (%):")
regulacao_maxima_label.grid(row=2, column=1, sticky="w")
valor_entry = tk.StringVar(value="10")
regulacao_maxima_entry = tk.Entry(janela, textvariable=valor_entry)
regulacao_maxima_entry.grid(row=3, column=1)

perda_efeito_corona_label = tk.Label(janela, text="Perda por efeito corona máxima (kW/km):")
perda_efeito_corona_label.grid(row=4, column=1, sticky="w")
valor_entry = tk.StringVar(value="10")
perda_efeito_corona_entry = tk.Entry(janela, textvariable=valor_entry)
perda_efeito_corona_entry.grid(row=5, column=1)

rendimento_minimo_label = tk.Label(janela, text="Rendimento mínimo (%):")
rendimento_minimo_label.grid(row=6, column=1, sticky="w")
valor_entry = tk.StringVar(value="93")
rendimento_minimo_entry = tk.Entry(janela, textvariable=valor_entry)
rendimento_minimo_entry.grid(row=7, column=1)

previsao_aumento_carga_label = tk.Label(janela, text="Previsão aumento de carga (%):")
previsao_aumento_carga_label.grid(row=8, column=1, sticky="w")
valor_entry = tk.StringVar(value="20")
previsao_aumento_carga_entry = tk.Entry(janela, textvariable=valor_entry)
previsao_aumento_carga_entry.grid(row=9, column=1)

verificar_button = tk.Button(janela, text="Verificar", command=verificar_campos)
verificar_button.grid(row=17, column=0, columnspan=2)

resposta_label = tk.Label(janela, text="")
resposta_label.grid(row=18, column=0, columnspan=2)

# Iniciando o loop principal da janela
janela.mainloop()
