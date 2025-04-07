import unicodedata
import win32print
import ast
from collections import defaultdict
import tkinter as tk
from tkinter import messagebox, END

impressora_arquivo = open('impressora.txt','r')  #ler um arquivo impressora.txt >> nome da impressora
impressora_nome = str(impressora_arquivo.read())




'''---------------------------FUNÇÕES CENTRALIZAR JANELA -----------------------------------------------'''
 

def centralizar_janela(tela, largura, altura,top=0):
        x, y = largura, altura
        tela.geometry("{}x{}+{}+{}".format(x, y,
                                           int((tela.winfo_screenwidth() / 2) - (x / 2)),
                                           int((tela.winfo_screenheight() / 2) - (y / 2) - top)))
        

    

'''---------------------------FUNCAO IMPRIMIR/ENVIAR MAQUININHA -----------------------------------------------'''
def enviar_texto_para_impressora_especifica(data_maquininha,janela_root,nome_impressora_padrao=impressora_nome):
            
    try:
        # Normaliza o texto para garantir a compatibilidade
        texto_para_imprimir = unicodedata.normalize("NFKD", data_maquininha).encode(encoding="windows-1252", errors="ignore")

        # Enumera todas as impressoras disponíveis
        impressoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        lista_impressoras = [imp[2] for imp in impressoras]

        # Verifica se a impressora desejada está na lista de impressoras
        if nome_impressora_padrao in lista_impressoras:
            nome_impressora = nome_impressora_padrao
        else:
            # Se a impressora padrão não for encontrada, utiliza a impressora padrão do sistema
            nome_impressora = win32print.GetDefaultPrinter()

        # Abre a impressora selecionada
        handle = win32print.OpenPrinter(nome_impressora)
        
        try:
            # Inicia um trabalho de impressão
            job = win32print.StartDocPrinter(handle, 1, ("Print Job", None, "RAW"))
            win32print.StartPagePrinter(handle)
            win32print.WritePrinter(handle, texto_para_imprimir)
            win32print.EndPagePrinter(handle)
            win32print.EndDocPrinter(handle)
            if janela_root.destroy():
                janela_root.destroy()
        finally:
            win32print.ClosePrinter(handle)

            
    except Exception as e:
        print(f"Erro ao enviar dados para a impressora: {e}\nVerifique se a impressora está conectada e configurada corretamente.")



'''---------------------------FUNCAO EXIBI O RELATORIO DOS PRODUTOS DINAMICO -----------------------------------------------'''
def aprensentar_dicionario_desempenho(lista):
        '''Tem o proposito de calcular e exibir o relatorio dos produtos dinamico'''

        # Agrupa todos os relatórios e converte em tupla - usando ast.literal_eval para segurança
        # retorno = [eval(tupla_bd[0]) for tupla_bd in lista_retorno] ou
        retorno = [ast.literal_eval(tupla_bd[0]) for tupla_bd in lista]
        
        
        # Usando defaultdict para inicializar automaticamente listas vazias
        dicionario_agrupa = defaultdict(list)

        for dicionario in retorno:
            for tupla in dicionario:
                chave,valor = tupla # umpack
                for tupla in list(sublista for sublista in valor):
                    
                    dicionario_agrupa[chave].append(tupla)
                    dicionario_agrupa.update({f'{chave}' : dicionario_agrupa[chave]})
        
        dicionario_desempenho = dict(dicionario_agrupa)
        agrupar_relatorio = [(chave,sum([uni[0] for uni in dicionario_desempenho[chave]]),sum([uni[1] for uni in dicionario_desempenho[chave]])) for chave in dicionario_desempenho]

        return agrupar_relatorio    
    

'''---------------------------FUNÇÕES QUE ADAPTA O ENTRY PARA FORMATO DE MOEDA -----------------------------------------------'''
# Bloco Formata Moeda 
def formata_moeda(entry_variavel,entry):
    '''Função que formata o valor digitado no entry como uma moeda (ex: 1234 -> 12,34)'''
    
    valor = entry_variavel.get().replace(",", "").replace(".", "")
    
    if valor.isdigit():
        valor = int(valor)
        formato_val = f"{valor // 100},{valor % 100:02d}"
        entry_variavel.set(formato_val)
       
        
    elif not valor:
        
        entry_variavel.set(entry.get())  # Mantém o campo vazio
        

def limpar_click(event, entry_variavel):
    if entry_variavel.get() == "0,00":
        entry_variavel.set("")

def voltar_padrao(event, entry_variavel):
   if not entry_variavel.get():
        entry_variavel.set("0,00")

def iniciar_no_final(event):
    '''Garante que a digitação ocorra sempre no final do texto e lida com exclusões'''
    entry = event.widget
    
    # Verifica se a tecla pressionada é Backspace ou Delete
    if event.keysym in ("BackSpace", "Delete"):
       # Posiciona o cursor sempre no final do texto
       entry.icursor(tk.END)
       # Permite que o comportamento padrão ocorra para estas teclas
       return
    else:
        # Insere o caractere no final
        entry.insert(tk.END, event.char)
    
    # Posiciona o cursor sempre no final do texto
    entry.icursor(tk.END)

    return "break"

def configurar_entry(entry):
    
    '''Configura o widget Entry com a formatação de moeda e os eventos necessários'''
    # Cria uma StringVar para o Entry e define o valor inicial
  
    entry_variavel = tk.StringVar(value='0,00')
    
    # Vincula a StringVar ao Entry
    
    entry.config(textvariable=entry_variavel)

    # Configura os bindings para os eventos
    entry.bind("<FocusIn>", lambda event: limpar_click(event, entry_variavel))
    entry.bind("<FocusOut>", lambda event: voltar_padrao(event, entry_variavel))
    entry.bind("<Key>", iniciar_no_final)

    # Adiciona um trace à variável para formatar o valor como moeda
    entry_variavel.trace_add("write", lambda *args: formata_moeda(entry_variavel,entry))




'''---------------------------FUNCAO POSICIONA ENTRY E BOTOES NA TELA -----------------------------------------------'''
# Posiciona Entry e Botoes da tela
def posicionar_OBJ_tela(valor_x,valor_y,w,h,padding=None):
    '''Configura a posicao da entrada de texto de entry e posicionamento dos botoes'''
    if padding:# Se for entry
        text_x = valor_x + padding
        text_y = valor_y + padding
        text_largura = w - 2 * padding
        text_altura = h - 2 * padding
        
    else:# Se for button
        text_x = valor_x 
        text_y = valor_y
        text_largura = w
        text_altura = h

    return (text_x,text_y,text_largura,text_altura)


'''---------------------------FUNÇÕES COM PROPOSITOS EXPECIFICOS -----------------------------------------------'''



def limparTreeview(treeview):
    for i in treeview.get_children():        
        treeview.delete(i)


def recuperar_texto(texto):
    """
    Converte uma string em uma única linha contendo '\n' para uma string multi-linha com quebras de linha reais.
    """
    return texto.replace("\\n", "\n")

def fechar_frame_dinamico(frame_topcos):
        if frame_topcos.winfo_ismapped():
            frame_topcos.grid_forget()


'''---------------------------FUNÇÕES PARA -----------------------------------------------'''
