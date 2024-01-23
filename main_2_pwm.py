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
        arq.write("potencia, frequencia, portadora, musica = 20, 480, 100_000, 'zelda'")
    sleep(0.1)
    from valores import *
    
from pinos import *
from musica import *
from logica_serial import *

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
    musicas(musica, pwm)

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
                logica_serial(texto_completo, uart, potencia, frequencia, portadora, musica)
                texto_completo = ""
                uart.write("\n>>>")
        
        except Exception as error:
            uart.write(str(error))
            print(error)
            sleep(0.5)

        sleep_us(50000)
