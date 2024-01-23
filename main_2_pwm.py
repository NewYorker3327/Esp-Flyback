#Bibliotecas:
from time import sleep, sleep_us
from time import ticks_us as time
from machine import Pin, PWM, UART
#import _thread
from math import log2
import os

#Para sensores de temperatura:
#from ds18x20 import DS18X20
#from onewire import OneWire

#Temperatuda da propria esp:
import esp32
#esp32.raw_temperature()

#Medir memória e limpar:
#from gc import mem_free, collect

#Valores pré-definidos:
try:
    from valores import *
except:
    print("Erro na leitura da memória para o PWM...")
    with open("valores.py", "w") as arq:
        arq.write("potencia, frequencia, portadora = 20, 480, 100_000")
    sleep(0.1)
    from valores import *
    
from pinos import *

def musicas(mus:str, obj):
    """
    Para tocar música
    """
    def voltar(k, log2 = log2, limite_inf = 440):
        return int(12*log2(k/limite_inf))

    def passar_nota(n):
        return int(220 * 2 ** (n/12))
    
    if mus == "intro":
        temp = 8
        mus = [[392, 200, 2], [392, 400, 3], [523, 200, 2], [523, 400, 3],
               [588, 200, 2], [588, 400, 3], [660, 200, 2], [660, 400, 3], [392, 200, 2],[392, 400, 23], [392,0, .8],
               [392, 400, 5], [523, 400, 5], [523, 400, 3], [588, 400, 5],
               [588, 400, 5], [660, 400, 5], [588, 400, 5], [660, 400, 5], [700, 400, 3], [660, 400, 3], [700, 400, 5],
               [660, 400, 3], [588, 400, 3], [523, 400, 25], [392, 10, 3]]

    if mus == "exit":
        temp = 8
        mus = [[1568+784, 440, 2], [1175+587, 440, 2], [784+523, 440, 2], [587+294, 440, 2],
               [523+392, 440, 2]]

    if mus == "zelda":
        v = 300
        temp = 16
        mus = [[12, v, 6], [0, v, 10], [2, v, 2], [3, v, 2], [5, v, 2], [7, v, 16],
               [8, v, 2], [10, v, 2], [12, v, 16], [10, v, 2], [8, v, 2], [10, v, 4],
               [8, v, 2], [7, v, 16], [5, v, 4], [7, v, 2], [8, v, 16], [7, v, 2], [5, v, 2], [3, v, 4],
               [5, v, 2], [7, v, 16], [5, v, 2], [3, v, 2], [2, v, 2], [3, v, 2], [5, v, 2], [8, v, 6], [7, v, 12]]

    if mus == "fef":
        v = 300
        temp = 16
        mus = [[1, v, 2], [8, v, 2], [15, v, 2], [16, v, 6], [1, v, 2], [8, v, 2], [15, v, 2], [16, v, 6], [1, v, 2], [8, v, 2], [15, v, 2], [16, v, 6],
               [[1,8], v, 2], [8, v, 2], [[15, 8], v, 2], [[16, 8], v, 2], [16, v, 4],
               [[-1,8], v, 2], [8, v, 2], [[15, 8], v, 2], [[16, 8], v, 2], [16, v, 4],
               [[-3,8], v, 2], [8, v, 2], [[15, 8], v, 2], [[16, 8], v, 2], [16, v, 4],
               [[3,6], v, 4], [[1, 4], v, 4], [[-1, 2], v, 4],
               [1, v, 8], [-1, v, 2], [6, v, 2], [1, v, 8], [-1, v, 2], [8, v, 2],
               [4, v, 8], [8, v, 2], [6, v, 2], [8, v, 8]]

    for nota in mus:
        if type(nota[0]) == list:
            resp = 0
            for n_individual in nota[0]:
                resp += passar_nota(n_individual)
            obj.freq(resp)
            obj.duty(nota[1])
            sleep(nota[2]/temp)
        elif nota[0] < 30:
            obj.freq(passar_nota(nota[0]))
            obj.duty(nota[1])
            sleep(nota[2]/temp)
        else:
            obj.freq(nota[0])
            obj.duty(nota[1])
            sleep(nota[2]/temp)

    obj.freq(432)
    obj.duty(0)

def logica_serial(texto, uart, potencia, frequencia, portadora):
    """
    Lógica da serial
    """
    texto = texto.replace("\r", "")
    
    if texto.find("=") > -1:
        texto = texto.replace(" ", "")
        funcao = f"globals()['{texto[:texto.find('=')]}'] = int({texto[texto.find('=') + 1:]})"
        exec(funcao)
        uart.write(f"Salvo {texto[:texto.find('=')]} localmente com o valor {{texto[texto.find('=') + 1:])}!\n\n")
        
    elif texto.find("salvar") > -1:
        with open("variaveis.py", "w") as arq:
            arq.write(f"potencia, frequencia, portadora = {potencia}, {frequencia}, {portadora}")
        uart.write("Salvo na memória flash!\n\n")
    
    elif texto.find("geral") > -1:
        uart.write(f"potencia = {potencia}\nfrequencia = {frequencia}\nportadora = {portadora}\n\n")
    
    elif texto.find("potencia") > -1:
        uart.write(f"potencia = {potencia}\n\n")
    
    elif texto.find("frequencia") > -1:
        uart.write(f"frequencia = {frequencia}\n\n")
    
    elif texto.find("portadora") > -1:
        uart.write(f"portadora = {portadora}\n\n")

    elif texto.find("temperatura") > -1:
        uart.write("Temperatura placa = {(esp32.raw_temperature()-32)/1.8:0.1f}C")
        
    elif texto.find("help") > -1:
        ajuda = """\nComandos		Explicacao
geral			Recebe os valores na memória local
potencia		Recebe o valor da potencia de 0 a 4096
frequencia		Recebe o valor da frequencia em hearts
portadora		Recebe o valor da portadora em micro segundos
salvar			Salva as variáveis na memória flash
temperatura		Mostra a temperatura da placa\n\n"""
        uart.write(ajuda)

if __name__ == "__main__":
#   ____        __ _       _      /\/|               
#  |  _ \  ___ / _(_)_ __ (_) ___|/\/   ___  ___   _ 
#  | | | |/ _ \ |_| | '_ \| |/ __/ _ \ / _ \/ __| (_)
#  | |_| |  __/  _| | | | | | (_| (_) |  __/\__ \  _ 
#  |____/ \___|_| |_|_| |_|_|\___\___/ \___||___/ (_)
#                             )_)                    
    ###Variável limite duty (1=100%):
    limite = 0.50
    
    sleep(3)
    led = Pin(2, Pin.OUT)
    for _ in range(3):
        led.on()
        sleep(0.25)
        led.off()
        sleep(0.25)

    ###Saídas:
    print(f"Ligando PWM (pino {pino_pwm})...\n")
    pwm = PWM(Pin(pino_pwm))#Canal PWM
    pwm.freq(432)
    pwm.duty(0)

    print(f"Ligando sinal portadora (pino {pino_portadora})...\n")
    pwm_portadora = PWM(Pin(pino_portadora))#Canal PWM
    pwm_portadora.freq(432)
    pwm_portadora.duty(0)

    #uart
    print(f"Ligando comunicação serial (pinos: tx = {pino_uart['tx']}, rx = {pino_uart['rx']})...\n")
    uart = UART(2, 115200, tx = pino_uart["tx"], rx = pino_uart["rx"])
    uart.init(115200, bits = 8, parity = None, stop = 1)
    sleep(0.1)
    
#   _____                     _                  _           
#  | ____|_  _____  ___ _   _| |_ __ _ _ __   __| | ___    _ 
#  |  _| \ \/ / _ \/ __| | | | __/ _` | '_ \ / _` |/ _ \  (_)
#  | |___ >  <  __/ (__| |_| | || (_| | | | | (_| | (_) |  _ 
#  |_____/_/\_\___|\___|\__,_|\__\__,_|_| |_|\__,_|\___/  (_)
#                                                            

    logo = """8b           d8   db         
`8b         d8'  d88b        
 `8b       d8'  d8'`8b       
  `8b     d8'  d8'  `8b      
   `8b   d8'  d8YaaaaY8b     
    `8b d8'  d8""""""""8b    
     `888'  d8'        `8b   
      `8'  d8'          `8b
    """
    uart.write(logo)
    uart.write(f"{'='*40}")
    uart.write("Escreva 'help' para ajuda...")

    #Tocando musíca:
    musicas("zelda", pwm)

    frequencia_antiga = frequencia
    potencia_antiga = potencia
    portadora_antiga = portadora

    pwm.freq(frequencia)
    pwm.duty(potencia)
    pwm_portadora.freq(portadora)
    pwm_portadora.duty(128) #50% do duty cicle

    #Da interface:
    texto_completo = ""
    uart.write(">>>")

    demora_media = 0

    while True:
        # Lógica do PWM com a portadora sendo pwm:
        #Mudança de parâmetros:
        if frequencia_antiga != frequencia:
            pwm.freq(frequencia)
            frequencia_antiga = frequencia

        elif potencia_antiga != potencia:
            pwm.duty(frequencia)
            potencia_antiga = potencia

        elif portadora_antiga != portadora:
            pwm_portadora.freq(portadora):
                portadora_antiga = portadora

        #Lógica da UART
        try:
            linha = uart.readline()
            if linha != None:
                novo = linha.decode('utf-8')
                if novo == "\b" and len(texto_completo) > 0:
                    texto_completo = texto_completo[:-1]
                texto_completo = f"{texto_completo}{novo}"
                uart.write(linha.decode('utf-8'))
                
            if texto_completo.find("\r") > -1:
                uart.write(f"\n\n")
                logica_serial(texto_completo, uart, potencia, frequencia, portadora)
                texto_completo = ""
                uart.write("\n>>>")
        
        except Exception as error:
            uart.write(str(error))
            print(error)
            sleep(0.5)

        sleep_us(50000)
