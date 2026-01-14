import requests
import os
from tkinter import *
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def previsao_tempo():
    API_KEY = os.getenv("OWM_API_KEY")
    
    if not API_KEY:
        texto_previsao['text'] = "Erro: OWM_API_KEY não configurada no .env"
        return
    
    cidade = campo_texto.get()
    if not cidade:
        texto_previsao['text'] = "Por favor, insira uma cidade"
        return
    
    try:
        link = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={API_KEY}&units=metric&lang=pt_br"
        requisicao = requests.get(link, timeout=10)
        
        if requisicao.status_code != 200:
            texto_previsao['text'] = f"Erro: Cidade não encontrada ou erro na API"
            return
        
        requisicao_dic = requisicao.json()
        descricao = requisicao_dic['weather'][0]['description']
        temperatura = requisicao_dic['main']['temp']
        sensacao = requisicao_dic['main']['feels_like']
        umidade = requisicao_dic['main']['humidity']
        
        informacoes = f'''Cidade: {requisicao_dic['name']}
Tempo: {descricao.capitalize()}
Temperatura: {temperatura:.1f}°C
Sensação: {sensacao:.1f}°C
Umidade: {umidade}%'''
        
        texto_previsao['text'] = informacoes
        
    except requests.exceptions.Timeout:
        texto_previsao['text'] = "Erro: Timeout na conexão"
    except requests.exceptions.RequestException:
        texto_previsao['text'] = "Erro: Falha na conexão com a API"
    except Exception as e:
        texto_previsao['text'] = f"Erro: {str(e)}"


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