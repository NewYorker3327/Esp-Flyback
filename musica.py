from math import log2
from time import sleep

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
