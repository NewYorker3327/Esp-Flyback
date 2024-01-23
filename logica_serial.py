def logica_serial(texto, uart, potencia, frequencia, portadora, musica = None):
    """
    Lógica da serial
    """
    texto = texto.replace("\r", "")
    
    if texto.find("=") > -1:
        texto = texto.replace(" ", "")
        if not "musica" in texto:
            funcao = f"globals()['{texto[:texto.find('=')]}'] = int({texto[texto.find('=') + 1:]})"
        else:
            funcao = f"globals()['{texto[:texto.find('=')]}'] = '{texto[texto.find('=') + 1:]}'"
        exec(funcao)
        uart.write(f"Salvo {texto[:texto.find('=')]} localmente com o valor {{texto[texto.find('=') + 1:])}!\n\n")
        
    elif texto.find("salvar") > -1:
        with open("variaveis.py", "w") as arq:
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
        uart.write("Temperatura placa = {(esp32.raw_temperature()-32)/1.8:0.1f}C")

    elif texto.find("musica") > -1:
        uart.write(f"musica = {musica}\n\n")
        
    elif texto.find("help") > -1:
        ajuda = """\nComandos		Explicacao
geral			Recebe os valores na memória local
potencia		Recebe o valor da potencia de 0 a 4096
frequencia		Recebe o valor da frequencia em hearts
portadora		Recebe o valor da portadora em micro segundos
salvar			Salva as variáveis na memória flash
temperatura		Mostra a temperatura da placa\n\n"""
        uart.write(ajuda)
