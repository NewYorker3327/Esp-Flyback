# Esp-Flyback
Arquivos relacionados ao projeto do gerador digital de alta tensão de frequência e potência ajustáveis.

## Conexões

### Direita

gpio_5 -> rx

gpio_18 -> tx

### Esquerda

gpio_12 -> pwm

gpio_12 -> portadora

						 
## MAIN

### main_1_pwm

Programa que tem um pwm e a portadora funciona por meio de um sleep. Caso a diferênça em microsegundos da portadora seja pequena demais a esp piscará.

### main_2_pwm

Programa que tem dois pwm's, o segundo pwm funciona como a portadora da segunda.

## Serial

* Instale o putty;
* Configure o baudrate do putty como 115200;
* Mande comandos para a esp.

### Comandos seriais

geral -> Recebe os valores na memória local

potencia -> Recebe o valor da potencia de 0 a 4096

frequencia -> Recebe o valor da frequencia em hearts

portadora -> Recebe o valor da portadora em micro segundos

salvar -> Salva as variáveis na memória flash

temperatura ->	Mostra a temperatura da placa
