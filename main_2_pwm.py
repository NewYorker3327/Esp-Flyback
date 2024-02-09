#Bibliotecas:
from time import sleep, sleep_us
from time import ticks_us as time
from machine import Pin, PWM, UART
#import _thread
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
    from valores import frequencia, potencia, portadora, musica
except:
    print("Erro na leitura da memória para o PWM...")
    with open("valores.py", "w") as arq:
        arq.write("potencia, frequencia, portadora, musica = 20, 432, 10000, 'zelda'")
    sleep(0.1)
    from valores import *
    
from pinos import *
from musica import *

def piscar(led):
    for _ in range(3):
        led.on()
        sleep(0.25)
        led.off()
        sleep(0.25)

def logica_serial(texto, uart, potencia, frequencia, portadora, musica = "zelda"):
    """
    Lógica da serial
    """
    texto = texto.replace("\r", "")

    if texto.find("=") > -1:
        texto = texto.replace(" ", "")
        try:
            uart.write(f"\nComando recebido: {texto}\n")
            globals()["ultimo"] = texto
        except:
            uart.write("[ERRO TEXTO]")
        if not "musica" in texto:
            funcao = f"globals()['{texto[:texto.find('=')]}'] = int({texto[texto.find('=') + 1:]})"
        else:
            funcao = f"globals()['{texto[:texto.find('=')]}'] = '{texto[texto.find('=') + 1:]}'"
        exec(funcao)
        uart.write(f"Salvo {texto[:texto.find('=')]} localmente com o valor {texto[texto.find('=') + 1:]}!\n\n")

    elif texto.find("salvar") > -1:
        with open("valores.py", "w") as arq:
            arq.write(f"potencia, frequencia, portadora, musica = {potencia}, {frequencia}, {portadora}, {musica}")
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
        uart.write(f"Temperatura placa = {(esp32.raw_temperature()-32)/1.8:0.1f}C")

    elif texto.find("musica") > -1:
        uart.write(f"musica = {musica}\n\n")

    elif texto.find("help") > -1:
        ajuda = """\nComandos		|Explicacao
------------------------|---------------------------------------------
geral			|Recebe os valores na memória local
potencia		|Recebe o valor da potencia de 0 a 4096
frequencia		|Recebe o valor da frequencia em hearts
portadora		|Recebe o valor da portadora em micro segundos
salvar			|Salva as variáveis na memória flash
temperatura		|Mostra a temperatura da placa\n\n"""
        uart.write(ajuda)


def logica_principal(uart, pwm, pwm_portadora, led, frequencia, potencia, portadora):
    piscar(led)

    logo = """8b           d8  db						F_1.0         
 8b         d8  d88b        
  8b       d8  d8  8b       
   8b     d8  d8    8b      
    8b   d8  d8YaaaaY8b     
     8b d8  d8========8b    
      888  d8          8b   
       8  d8            8b
\n\n"""
    uart.write(logo)
    ajuda = """\nComandos		|Explicacao
------------------------|---------------------------------------------
geral			|Recebe os valores na memória local
potencia		|Recebe o valor da potencia de 0 a 4096
frequencia		|Recebe o valor da frequencia em hearts
portadora		|Recebe o valor da portadora em micro segundos
salvar			|Salva as variáveis na memória flash
temperatura		|Mostra a temperatura da placa\n\n"""
    uart.write(ajuda)
    uart.write(f"{'='*40}\n\n")
    uart.write("Escreva 'help' para ajuda...\n\n")
    
    frequencia_antiga = frequencia
    potencia_antiga = potencia
    portadora_antiga = portadora

    pwm.freq(frequencia)
    pwm.duty(potencia)
    pwm_portadora.freq(portadora)
    pwm_portadora.duty(128) #50% do duty cicle
    intervalo = 35_000
    iteracao = 1

    #Da interface:
    texto_completo = ""
    uart.write(">>>")

    while True:
        iteracao += 1
        # Lógica do PWM com a portadora sendo pwm:
        #Mudança de parâmetros:
        if frequencia_antiga != frequencia:
            pwm.freq(frequencia)
            frequencia_antiga = frequencia

        elif potencia_antiga != potencia:
            pwm.duty(frequencia)
            potencia_antiga = potencia

        elif portadora_antiga != portadora:
            pwm_portadora.freq(portadora)
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

            if texto_completo.find("§") > -1:
                uart.write(f"\n\n\nReiniciando...\n\n\n\n\n")
                return None
            
            if texto_completo.find("+") > -1:
                frequencia = 432
                potencia = 0
                portadora = 10_000
                uart.write(f"\nReiniciando parâmetros potencia = {potencia}, frequencia = {frequencia}, portadora = {portadora}\n\n")
                texto_completo = ""
                uart.write("\n>>>")

            if texto_completo.find("\r") > -1:
                uart.write(f"\n\n")
                logica_serial(texto_completo, uart, potencia, frequencia, portadora, musica)
                texto_completo = ""
                uart.write("\n>>>")
            
            if iteracao % 30 == 0:
                if (esp32.raw_temperature()-32)/1.8 > 80:
                    uart.write(f"Alta temperatura {(esp32.raw_temperature()-32)/1.8}Cº, diminuindo clock!\n\n")
                    intervalo += 30_000
                    intervalo = min(300_000, intervalo) 
                
                elif (esp32.raw_temperature()-32)/1.8 < 60:
                    intervalo = 35_000
                iteracao = 1
            
        except Exception as error:
            uart.write(f"{texto_completo} -> {str(error)}\n\n>>>")
            texto_completo = ""
            print(error)
            sleep(0.5)
        
        sleep_us(intervalo)

if __name__ == "__main__":
#   ____        __ _       _      /\/|               
#  |  _ \  ___ / _(_)_ __ (_) ___|/\/   ___  ___   _ 
#  | | | |/ _ \ |_| | '_ \| |/ __/ _ \ / _ \/ __| (_)
#  | |_| |  __/  _| | | | | | (_| (_) |  __/\__ \  _ 
#  |____/ \___|_| |_|_| |_|_|\___\___/ \___||___/ (_)
#                             )_)                    
    ###Variável limite duty (1=100%):
    ultimo = ""
    novo = ""
    
    sleep(3)
    led = Pin(2, Pin.OUT)
    piscar(led)

    ###Saídas:
    print(f"Ligando PWM (pino {pino_pwm})...\n")
    pwm = PWM(Pin(pino_pwm))#Canal PWM
    pwm.freq(432)
    pwm.duty(0)

    print(f"Ligando sinal portadora (pino {pino_portadora})...\n")
    pwm_portadora = PWM(Pin(pino_portadora))#Canal PWM
    pwm_portadora.freq(10_000)
    pwm_portadora.duty(500)

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

     #Tocando musíca:
    musicas(musica, pwm)

    while True:
        logica_principal(uart, pwm, pwm_portadora, led, frequencia, potencia, portadora)
