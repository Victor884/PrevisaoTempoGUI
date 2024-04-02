import requests
from tkinter import *

def  previsao_tempo():
    API_KEY = "4e58652643262559157672350a860d75"
    cidade = campo_texto.get()
    link = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={API_KEY}&lang=pt_br"

    requisicao = requests.get(link)
    requisicao_dic = requisicao.json()
    descricao = requisicao_dic['weather'][0]['description']
    temperatura_celsius = requisicao_dic['main']['temp'] - 273.15

    informacoes = f'''
    Tempo: {descricao}
    Temperatura: {temperatura_celsius:.1f}ºC'''

    texto_previsao['text'] =  informacoes


janela = Tk()
janela.title('Previsao Do Tempo')
texto_orient =  Label(janela, text="Insira a Cidade que deseja verificar o clima:")
texto_orient.grid(row=0, column=0, padx=10, pady=10)

campo_texto = Entry(janela)
campo_texto.grid(row=1, column=0)

texto_previsao = Label(janela, text='')
texto_previsao.grid(row=2,column=0)

botao = Button(janela, text="Buscar clima", command=previsao_tempo)
botao.grid(column=0,row=3, padx=10, pady=10)

janela.mainloop()