import tkinter as tk
from tkinter import *
from tkinter import Tk, Canvas, PhotoImage, Text, ttk
from PIL import ImageTk, Image
import pyodbc
from tkcalendar import Calendar
from datetime import datetime
from tkinter import messagebox, END
import pandas as pd
import logging
# import re
# import random
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
import string
from tkinter import PhotoImage
from sistema_funcoes_axi import *

conexao = pyodbc.connect("Driver={SQLite3 ODBC Driver};Server=localhost;Database=bdAcai.db")
cursor = conexao.cursor()

# Definindo cores
cores = {'Branca':'#ffffff',
         'Preta':'#000000',
         'Roxo Escuro':'#280D2B',
         'Linha_tre':'#ECECEC',
         'fundo_cinza':'#C5BCBC',
         'fundo_cinzaEscuro':'#C1BAC1',
         'Frame dinamico':'#280D2B',
         'Botao selecao':'#D78ADD',
         'vermelho_bt' :'#b60e0e',
         'Verde_bt' :'#178f1c',
         'text_botao_claro': '#ECECEC',
         }




'''---------------------------CAMPO ROOT (TELA PRINCIPAL) -----------------------------------------------'''
root = tk.Tk()
root.title("Interface de Vendas")
root.config(background=cores['Preta'])
root.attributes("-fullscreen", True)  # definir minha tela-cheia


# Adapta a pagina root com base na resolução da tela
valores_para_tela_root = {'largura_dinamica':root.winfo_screenwidth(),
                'altura_dinamica':root.winfo_screenheight()}
x_dinamica = ((valores_para_tela_root['largura_dinamica'] - 1280))
y_dinamico = ((valores_para_tela_root['altura_dinamica'] - 768))



frame_root = tk.Frame(root, bg='#000000')
frame_root.pack(side="left", fill='both', expand=True)

canvas = Canvas(
    frame_root,
    bg = cores['Preta'],
    height = valores_para_tela_root['altura_dinamica'],
    width = valores_para_tela_root['largura_dinamica'],
    bd = 0,
    highlightthickness = 0,
    relief = "ridge")
canvas.place(x = 0, y = 0)

segundoImagem = ImageTk.PhotoImage(Image.open(r"img_inicio\fundo_historico{}.png".format(valores_para_tela_root['largura_dinamica'])))
background = canvas.create_image(valores_para_tela_root['largura_dinamica']/2, valores_para_tela_root['altura_dinamica']/2, image=segundoImagem)


'''---------------------------CAMPO FILTRO -----------------------------------------------'''
#Eventos de cada sequencia de letras filtra minha lista de profutos na Treeview

def filtro_pedidos(entry_filtro_pedido):
    global colunasDinamicas_pedidos
    global entry_data
    #if - se
    #Verifica se os campos estão vazio
    if not entry_filtro_pedido.get():

        #Se o campo filtro estiver vazio lista todos os valores
        listar_historico_pedido()       
        return
    
    sql = f"SELECT * FROM Pedidos"
    
    params = []
    
    # Verifica se ao codigo esta correto
    comando = f'SELECT * FROM Pedidos WHERE {colunasDinamicas_pedidos[0]} LIKE ? AND Data = ?'
    cursor.execute(comando,(entry_filtro_pedido.get() + '%',entry_data.get()))
    codigo = cursor.fetchall()
    
    if codigo:

        sql += f" WHERE {colunasDinamicas_pedidos[0]} LIKE ?"         
        params.append('%' + entry_filtro_pedido.get() + '%')

    else:
        # Verifica se a categoria esta correto
        digitando_maiusculo = str(entry_filtro_pedido.get()).upper()
        comando = f'SELECT * FROM Pedidos WHERE {colunasDinamicas_pedidos[1]} LIKE ? AND Data = ?'
        cursor.execute(comando,('%' + digitando_maiusculo + '%',entry_data.get()))
        categoria = cursor.fetchall()

        if categoria:
        
            sql += f" WHERE {colunasDinamicas_pedidos[1]} LIKE ?" 
            params.append('%' + digitando_maiusculo + '%')

        
        else:
            # Verifica se a descricao esta correto
            comando = f'SELECT * FROM Pedidos WHERE {colunasDinamicas_pedidos[2]} LIKE ? AND Data = ?'
            cursor.execute(comando,('%' + entry_filtro_pedido.get() + '%',entry_data.get()))
            descricao = cursor.fetchall()

            if descricao:
                sql += f" WHERE {colunasDinamicas_pedidos[2]} LIKE ?" 
                params.append('%' + entry_filtro_pedido.get() + '%')
            else:
                sql += f" WHERE {colunasDinamicas_pedidos[3]} LIKE ?" 
                params.append('%' + entry_filtro_pedido.get() + '%')

    
    #Limpa os dados da treeview
    limparTreeview(treeview_pedidos)

    # Retorna valores so da mesma data
    params.append(entry_data.get())
    cursor.execute(sql + " AND Data = ?", tuple(params))
    produtos = cursor.fetchall()
    
        
    #Preenche treeview com os dados filtrados
    for index,valor in enumerate(produtos):

        if index % 2 == 0:# ocorrencia de repeticao 2 em 2 ou 3 em 3 para colorir uma linha 
            treeview_pedidos.insert('', 0, values=(valor[0], valor[1], valor[3], valor[6]), tags=('evenrow',))
        else:
            treeview_pedidos.insert('', 0, values=(valor[0], valor[1], valor[3], valor[6]), tags=('oddrow',))
    

x,y,w,h = posicionar_OBJ_tela(valor_x=233, 
                              valor_y=148+9,
                              w=401,
                              h=32,
                              padding=5)

entry_filtro_pedido = Entry(
    bd=0,
    bg="#ffffff",
    highlightthickness=0,
    font='Arial 12',
    relief='flat')

filtro_pedido = canvas.create_window(x, y,anchor="nw",width=w, 
                     height=h, window=entry_filtro_pedido)

entry_filtro_pedido.bind("<KeyRelease>",lambda e: filtro_pedidos(entry_filtro_pedido))


'''---------------------------CAMPO DATA -----------------------------------------------'''

x,y,w,h = posicionar_OBJ_tela(valor_x=646+3,
                              valor_y=148+9,
                              w=213,
                              h=32,
                              padding=5)

def open_calendar(entry, data):
    '''Retorna um calendário com ação no entry'''
    def select_date(event):
        '''Filtra os pedidos com base na data passada no entry'''
        try:
            selected_date = cal.selection_get()
            entry.delete(0, tk.END)
            entry.insert(0, selected_date.strftime('%d/%m/%Y'))
            calendarioTela.destroy()
            listar_historico_pedido()
        except Exception as e:
            messagebox.showerror('Erro',f"Erro ao selecionar data: {e}")

    try:
        calendarioTela = tk.Toplevel(root)
        calendarioTela.title("Calendário")
        calendarioTela.grab_set()
        centralizar_janela(calendarioTela, 251, 185,top=115)
        calendarioTela.resizable(False, False)
        
        # Verificar se o `locale` é suportado
        cal = Calendar(calendarioTela, selectmode='day', locale='pt_br', date_pattern='dd/mm/yyyy', year=data.year, month=data.month, day=data.day)
        cal.pack()
        cal.bind("<<CalendarSelected>>", select_date)        
    except Exception as e:
        messagebox.showerror('Erro',f"Erro ao criar o calendário: {e}")


try:
    dataAtual = datetime.now()
    entry_data = Entry(bd=0, bg="#ffffff", highlightthickness=0, relief='flat', font='Arial 12')
    data_criar = canvas.create_window(x, y, width=w, height=h, anchor="nw", window=entry_data)
    entry_data.insert(0, dataAtual.strftime('%d/%m/%Y'))
    entry_data.bind("<Button-1>", lambda event: open_calendar(entry_data, dataAtual))

except Exception as e:
    messagebox.showerror('Erro',f"Erro ao configurar o Entry: {e}")


'''---------------------------BOTAO SAIR SO SISTEMA -----------------------------------------------'''

sair_sistema_img = PhotoImage(file=r"img_inicio\bt_sair_fechar.png")

x,y,w,h = posicionar_OBJ_tela(valor_x=1124 + x_dinamica/2,
                              valor_y=142,
                              w=132+2,
                              h=42+2)

bt_sair_sistema = Button(image=sair_sistema_img, borderwidth=0,background=cores['Roxo Escuro'],
                      activebackground=cores['Roxo Escuro'], highlightthickness=0, 
                      relief="ridge",command=root.destroy)

sair_cancelar_criar = canvas.create_window(x, y, width=w, anchor="nw", height=h, window=bt_sair_sistema)


'''---------------------------CAMPO EXIBIR PEDIDOS -----------------------------------------------'''

colunasDinamicas_pedidos = ['Numero','Tipo','Pedido','Hora']
conta_pedidos_atual_tre = None

x,y,w,h = posicionar_OBJ_tela(valor_x=230.61,
                              valor_y=216+9,                              
                              w=777.77+ x_dinamica,
                              h=514 + y_dinamico)


# Inicializar um Treeview
treeview_pedidos = ttk.Treeview(canvas)
exibir_estoque = canvas.create_window(x, y, anchor=tk.NW, width=w,
                                       height=h, window=treeview_pedidos)

# Adicionar barras de rolagem
scrollbar_y = tk.Scrollbar(treeview_pedidos, orient=tk.VERTICAL)

# Criar o Treeview e configurá-lo com barras de rolagem
treeview_pedidos = ttk.Treeview(treeview_pedidos, yscrollcommand=scrollbar_y.set)
scrollbar_y.config(command=treeview_pedidos.yview)
scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
treeview_pedidos.pack(fill=tk.BOTH, expand=True)




def listar_historico_pedido():
    global entry_data,colunasDinamicas_pedidos,conta_pedidos_atual_tre,entry_filtro_pedido,style

    #Limpa os valores da treeview_estoque
    limparTreeview(treeview_pedidos)

    # Adicionando itens a treeview de exibir -----------------------------------------------
    style = ttk.Style()
    # style.layout("Custom.Treeview", [("Treeview.field", {'sticky': 'nswe'})])
    style.configure("Custom.Treeview", font=("Arial", 12),
                    background='white',foreground="black",fieldbackground="red")
    style.configure("Treeview.Heading", font = "Arial 10 bold")

    treeview_pedidos.config(style='Custom.Treeview')

    #Executa um comando SQL para selecionar só a data selecionada no entry data
    cursor.execute("Select * From Pedidos WHERE Data = ?",(entry_data.get()))

    #Armazena os valores retornados pelo comando SQL em uma variável
    valores = cursor.fetchall()


    # modificar o cabeçario dinamico
    largura_colunas_treeview_pedido = [100,100,350,90]
    treeview_pedidos.config(columns=(colunasDinamicas_pedidos),show="headings")

    # cor linhas treeview
    treeview_pedidos.tag_configure('oddrow', background=cores['Branca'])
    treeview_pedidos.tag_configure('evenrow', background=cores['Linha_tre'])

    for i,coluna in enumerate(colunasDinamicas_pedidos):
        treeview_pedidos.heading(coluna, text=f'  {coluna}  ')
        treeview_pedidos.column(coluna,width=largura_colunas_treeview_pedido[i],anchor= CENTER)

    # Adiciona cor as linhas do Treeview
    for index,valor in enumerate(valores):

        if index % 2 == 0:# ocorrencia de repeticao 2 em 2 ou 3 em 3

            # Inserir valores sempre no inicio do treeview
            treeview_pedidos.insert('', 0,values=(valor[0], valor[1], valor[3], valor[6]), tags=('evenrow',))
        else:
            treeview_pedidos.insert('', 0,values=(valor[0], valor[1], valor[3], valor[6]), tags=('oddrow',))
    
    
    entry_filtro_pedido.delete(0, tk.END)

listar_historico_pedido()

# Busca pedidos feitos ---------------------------------------------------------------------



try:
    def ler_Historico_pedido(event):
        # 1 . Quando der dois click sobre meu treview abre uma tela 
        # com meu text e o pedido do mesmo jeito quando foi finalizado caso queira visualizar
        global entry_data, enviar_texto_para_impressora_especifica

        # retorna a posicao da linha selecionada
        posicao_selecionado = treeview_pedidos.selection()[0]
        
        #Obtém os valores do item selecionado passando a posicao da linha - Numero
        numero_selecionados = treeview_pedidos.item(posicao_selecionado)['values'][0]

        cursor.execute("SELECT * FROM Pedidos WHERE Numero == ? AND Data == ?", 
                       (numero_selecionados,entry_data.get()))
        
        pedido_salvo = cursor.fetchall()[0][2]# Pegando o pedido

        # Substituir as quebras de linha literais '\\n'pela quebra de linha real '\n'
        pedido_recuperado = recuperar_texto(pedido_salvo)
        
        alturaFundo = 545
        larguraFundo = 352
        

        # Janela que exibi o pedido salvo
        janela = Toplevel(root)
        janela.title('Histórico desse Pedido')
        janela.grab_set()# precisa ser chamado apos a criacao
        janela.transient(root)  # Manter janela no topo
        janela.focus_force()  # Força o foco na janela

        janela.rowconfigure(0,weight=1)
        janela.columnconfigure(0,weight=1)
        centralizar_janela(janela,larguraFundo,alturaFundo)
        janela.resizable(False,False)
        
        canvas = tk.Canvas(
            janela,
            bg = cores['Roxo Escuro'],
            height = alturaFundo,
            width = larguraFundo,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge")
        canvas.place(x = 0, y = 0)


        img_exibir_top = PhotoImage(file = r"img_inicio\text-exibir-pedido_topvalue.png")
        exibir_fundo = canvas.create_image(larguraFundo/2, alturaFundo/2, image=img_exibir_top)
        
        def bloquear_texto(event):
            return 'break'
        

        padding = 20

        x,y,w,h = posicionar_OBJ_tela(valor_x=17,
                              valor_y=19,
                              w=318,
                              h=444,
                              padding=padding)
        
        text_exibir_pedido = Text(canvas,bd = 0, bg = "#ffffff",wrap=tk.WORD,highlightthickness = 0,
                                    padx=padding,pady=padding-15, font='Arial 13')


        # Para colocar o scroll preciso dizer onde ele irar acoplar primeiro se e na tela ou em um objeto
        scrollbar = tk.Scrollbar(canvas, orient=tk.VERTICAL, command=text_exibir_pedido.yview)
        canvas.create_window(311, 28, anchor="nw", height=426, window=scrollbar)
        text_exibir_pedido.config(yscrollcommand=scrollbar.set)
       
        exibir_janela = canvas.create_window(x, y, anchor="nw", width=w - 14, 
                                                height=h , window=text_exibir_pedido)
        text_exibir_pedido.delete("1.0", tk.END)
        text_exibir_pedido.insert(tk.END, pedido_recuperado)
        texto_historico = text_exibir_pedido.get('1.0',tk.END)
          

        # Imprimir pedidos feitos
        imprime_img = PhotoImage(file = r"img_inicio\bt-confirma-pagamento.png")
       
        x,y,w,h = posicionar_OBJ_tela(valor_x=176,
                              valor_y=477,
                              w=157 + 3,
                              h=50 + 7)

        imprime_pedido = Button(canvas,image = imprime_img, borderwidth = 0,activebackground=cores['fundo_cinza'], highlightthickness = 0, 
                    command = lambda : enviar_texto_para_impressora_especifica(texto_historico,janela),relief = "ridge")
        imprime_pedido.image = imprime_img
        imprime_pedido.place(x=x, y=y, width=w, height=h)

        # Cancelar pedidos
        cancelar_pedido_img = PhotoImage(file = r"img_inicio\bt-cancelar-pagamento.png")
        
        x,y,w,h = posicionar_OBJ_tela(valor_x=19,
                              valor_y=477,
                              w=143 + 3,
                              h=50 + 7)

        def cancelar_peidos_feitos():
            if messagebox.askyesno('Cuidado!!!','Deseja deletar pra sempre esse pedido?'):
                janela.destroy()
                root.after(2000,deletar_pedido)
                
        def deletar_pedido():
            # try:
            if str(dataAtual.strftime('%d/%m/%Y')) == entry_data.get():

                # Com a linha já selecionada usa essa referencia para deletar os valores da 
                # tabela relatorio com 4 PASSOS
                cursor.execute("SELECT Relatorio FROM Pedidos WHERE Numero == ? AND Data == ?", 
                            (numero_selecionados,entry_data.get()))
                


                # 1° Recuperar todos os valores da linha
                pedidos_pendentes = aprensentar_dicionario_desempenho(cursor.fetchall())
                cursor.execute(f"SELECT Codigo,Descrição,Quantidade,Preço FROM Estoque WHERE Descrição IN ({', '.join(['?'] * len(pedidos_pendentes))})",([pedido[0] for pedido in pedidos_pendentes]))
                pedidos_pendentes_bd = cursor.fetchall()
                


                # 2° Crio um dicionario e lista de lançamentos de referencia para retira do estoque
                dci = {n : (cd,e,p) for cd,n,e,p in pedidos_pendentes_bd if p != 0}
                lista_lancamento = []

                for nome,uni,fat in pedidos_pendentes:
                    
                    # se os produtos for ml por aqui
                    if nome in ['Açai','Sorvete','Milk - Shake']:
                        atualizar_estoque = int((fat/dci[nome][2])*1000)#preco
                        atualizar_estoque = int(dci[nome][1] + atualizar_estoque)#adicionar do estoque
                        lista_lancamento.append((dci[nome][0],atualizar_estoque))# codigo , novo estoque
                    else:
                        atualizar_estoque = int(dci[nome][1] + uni)#adicionar do estoque
                        lista_lancamento.append((dci[nome][0],atualizar_estoque))# codigo , novo estoque



                # 3° Crio um dicionario e lista de lançamentos de referencia para retira do estoque
                '''
                Atualizar várias linhas de uma vez usei o comando UPDATE com uma cláusula CASE. 
                Dessa forma, posso executar uma única query para atualizar múltiplos itens.
                '''
                query = """
                    UPDATE Estoque
                    SET Quantidade = CASE
                """
                parametros = []

                # # Construir a cláusula CASE para cada item
                # # UPDATE Estoque
                # # SET Quantidade = CASE
                # #     WHEN Descrição = 'Açai' THEN 67685
                # #     WHEN Descrição = 'Milk - Shake' THEN 5768
                # #     ELSE Quantidade
                # # END

                for pedido in lista_lancamento:
                    codigo = pedido[0]  
                    quantidade = pedido[1]  
                    query += "WHEN Codigo = ? THEN ? " # THEN <<  Especifica o valor a ser atribuído quando a condição for verdadeira.
                    parametros.extend([codigo, quantidade])
                
                # Fechar a query com a cláusula WHERE
                query += "END WHERE Codigo IN ({})".format(','.join(['?'] * len(lista_lancamento)))
                parametros.extend([pedido[0] for pedido in lista_lancamento])
                # saida >> ['1, 67685, '4', 5768, '1', '4']
            
                cursor.execute(query, parametros)
                cursor.execute("DELETE FROM Pedidos WHERE Numero = ? AND Data = ?", 
                (numero_selecionados, entry_data.get()))
                treeview_pedidos.delete(posicao_selecionado)



                # 4° Reorganizar os numeros dos pedidos listado
                try:
                    
                    numero_na_sequencia = [l for l in range(1, len(treeview_pedidos.get_children()) + 1)]  # [1, 2, 3, 4]
                    numero_no_treeview = sorted([int(treeview_pedidos.item(item)['values'][0]) for item in treeview_pedidos.get_children()])
                    # lista.sort(reverse=False) [2,3,4,5]
                    
                    # Itera sobre as linhas do Treeview e a lista numerada
                    for i, item in enumerate(numero_na_sequencia):
                        # Atualiza o campo 'Numero' para cada registro correspondente no banco de dados
                        cursor.execute('UPDATE Pedidos SET Numero = ? WHERE Data = ? AND Numero = ?', 
                                    (numero_na_sequencia[i], entry_data.get(), numero_no_treeview[i]))
                except:
                    pass

                # Confirma a operação no banco de dados
                conexao.commit()
                listar_historico_pedido()
                messagebox.showinfo('Deletado','O pedido em questão foi deletado.')
                
            else:
                messagebox.showerror('Atenção','Não é possível cancelar pedidos, diferente do dia de hoje.')


        cancelar = Button(canvas,image = cancelar_pedido_img, borderwidth = 0,activebackground="#C5BCBC",
                        highlightthickness = 0,relief = "ridge",command=cancelar_peidos_feitos)
        cancelar.image = cancelar_pedido_img
        cancelar.place(x=x, y=y, width=w, height=h)

        text_exibir_pedido.bind('<KeyPress>', bloquear_texto)
        text_exibir_pedido.bind('<KeyRelease>', bloquear_texto)
        janela.mainloop()

    treeview_pedidos.bind("<Double-1>",ler_Historico_pedido)
  
except:
   messagebox.showerror('Error ao Exibir','Verifica se esse pedido existe!')

#------------------------xxxxxx Novo Pedido xxxxxx---------------------------------------------------------------------------------------------------
espaço = 9

def funcao_novo_pedido():
    global variavel_global,listar_produtos_disponiveis_pra_vender,entry_unidade_atual,complementos_set, tamanho_set,button_states
    
    variavel_global = ''
    button_states = {}
    
    # O objeto Set permite que você armazene valores exclusivos de qualquer tipo, 
    # sejam valores primitivos ou referências de objetos
    complementos_set = set()
    tamanho_set = set()

    todos_botoes = []
    listar_produtos_disponiveis_pra_vender = []
   

    


    janela_novo_pedido = tk.Toplevel(root)
    janela_novo_pedido.grab_set()# precisa ser chamado apos a criacao
    janela_novo_pedido.transient(root)  # Manter janela_novo_pedido no topo
    janela_novo_pedido.focus_force()
    
    janela_novo_pedido.resizable(False, False)
    janela_novo_pedido.title('Monte um Pedido')
    janela_novo_pedido.rowconfigure(0,weight=1)
    janela_novo_pedido.columnconfigure(0,weight=1)
    
    alturaFundo = 650
    larguraFundo = 1200
    centralizar_janela(janela_novo_pedido,larguraFundo,alturaFundo,top=30)

    canvas_novo_pedido = Canvas(
        janela_novo_pedido,
        bg = cores['Roxo Escuro'],
        height = alturaFundo,
        width = larguraFundo,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge")
    canvas_novo_pedido.place(x = 0, y = 0)
    background_img = PhotoImage(master=janela_novo_pedido,file = r"img_vendas\bg-fundo.png")
    background = canvas_novo_pedido.create_image(larguraFundo/2, alturaFundo/2, image=background_img)
   
    # Fechar conexões pendentes
    try:
        conexao.rollback()
    except:
        pass
    
    '''-----------------------------------Entry Produtos -----------------------------------'''

    x,y,w,h = posicionar_OBJ_tela(valor_x = 23,
                              valor_y = 69,                              
                              w = 401,
                              h = 40,
                              padding=5)

    # criar um evento que abri frame produtos
    def lista_comb(event):

        trocar_frame(0,0,largura,'Produtos')

    entry_produtos = Entry(janela_novo_pedido,
                            bd = 0,
                            bg = cores['Branca'],
                            highlightthickness = 0,font='Arial 15')

    canvas_novo_pedido.create_window(x, y, anchor="nw", width=w, height=h, window=entry_produtos)
    entry_produtos.bind('<Button-1>',lista_comb)



    '''-----------------------------------Commbox Unidades -----------------------------------'''

    def lista_comb(event):
        fechar_frame_dinamico(frame_topcos)

    def limpa_texto(event):
        '''Limpa o text quando selecionado'''
        if entry_unidade.get() == texto_padrao or entry_unidade.get() != texto_padrao:
            entry_unidade.delete(0, END)
    def restaurar_texto(event):
        '''Retorna o texto padrao'''
        if entry_unidade.get() == "":
            entry_unidade.insert(0, texto_padrao)

    texto_padrao = '1'
    entry_unidade_atual = '1'
    x,y,w,h = posicionar_OBJ_tela(valor_x = 435,
                              valor_y = 69,                              
                              w = 91,
                              h = 40,
                              padding=5)

    entry_unidade = Entry(janela_novo_pedido,
                            bd = 0,
                            bg = cores['Branca'],
                            highlightthickness = 0,font='Arial 15',justify='center')
    
    canvas_novo_pedido.create_window(x, y, anchor="nw", width=w, height=h, window=entry_unidade)
    entry_unidade.bind('<Button-1>',lista_comb)
    entry_unidade.insert(0,texto_padrao)
    entry_unidade.bind("<FocusIn>", limpa_texto)
    entry_unidade.bind("<FocusOut>", restaurar_texto)


    '''-----------------------------------Commbox Tamanho -----------------------------------'''

    x,y,w,h = posicionar_OBJ_tela(valor_x = 546,
                              valor_y = 69,                              
                              w = 170,
                              h = 40,
                              padding=5)

    # Função para bloquear a entrada de texto do teclado
    def bloquear_texto(event):
        return "break"

    def lista_comb(event):
        # global entry_produtos
        # global bancodedados

        if entry_produtos.get() in ['AÇAI','SORVETE','MILK - SHAKE']:
            ''' Antes de listar o botao tamanho verifico valores'''
            if entry_produtos.get() == 'MILK - SHAKE':
                bancodedados.update({'Tamanho':('Categoria','TAMANHO MK')})
            
            else:
                bancodedados.update({'Tamanho':('Categoria','TAMANHO')})
            
            trocar_frame(0,2,145,'Tamanho')

    tamanho_copos = Entry(janela_novo_pedido, bd = 0,bg = cores['Branca'],highlightthickness = 0,
                font='Arial 15',justify='center')

    canvas_novo_pedido.create_window(x, y, anchor="nw", width=w, height=h, window=tamanho_copos)

    # Associar eventos para bloquear a entrada de texto do teclado
    tamanho_copos.bind('<Button-1>',lista_comb)
    tamanho_copos.bind('<KeyPress>', bloquear_texto)
    tamanho_copos.bind('<KeyRelease>', bloquear_texto)

    '''-----------------------------------BOTAO REINICIAR-----------------------------------'''
    def reiniciar_botoes():
        global complementos_set
        global tamanho_set
        global button_states
            
        # 1° fechar o frame
        fechar_frame_dinamico(frame_topcos)
            
        # 2° limpar todas as variáveis
        complementos_set = set()
        tamanho_set = set()
        button_states = {}
        
        # Limpar os campos Entry
        entry_produtos.delete(0, tk.END)
        tamanho_copos.delete(0, tk.END)
        
        # Limpar e reiniciar o campo Text
        entry_observacoes.delete('1.0', tk.END)
        entry_observacoes.insert('1.0', 'Observações...')
        
        
        # Limpar e reiniciar o campo Entry
        entry_unidade.delete(0, tk.END)
        entry_unidade.insert(0, '1')

    x,y,w,h = posicionar_OBJ_tela(valor_x = 757,
                              valor_y = 69,                              
                              w = 54,
                              h = 45)
    
    imgreini = PhotoImage(file = r"img_vendas\botao-reiniciar.png")
    bt_reiniciar = Button(canvas_novo_pedido,image = imgreini,borderwidth = 0,activebackground="#280D2B", highlightthickness = 0, command = reiniciar_botoes, fg="black",relief = "ridge")
    bt_reiniciar.place(x=x, y=y, width=w, height=h)

  
    '''-----------------------------------FRAME PARA ITENS DINAMICOS -----------------------------------'''


    # x, y = 16, 118
    largura=818
    altura=340
    largura_topcos = 235
    padding = 5

    # Criar o frame principal
    frame_janela = tk.Frame(canvas_novo_pedido,background=cores['Roxo Escuro'])
    # frame_janela.pack_propagate(False)
    frame_janela.place(x=16, y=118)

    # Criar o sub-frame dentro do frame principal
    frame_axi = tk.Frame(frame_janela,width=788, height=345,background=cores['Roxo Escuro'])##280D2B
    frame_axi.pack()
    

    # Cria o frame da chamada dos botoes
    frame_topcos = tk.Frame(frame_axi)


    def busca_itens_no_bd(tupla_buscar):
        col,cojunto = tupla_buscar # umpack
        cursor.execute(f"SELECT * FROM Estoque WHERE {col} == ?",(cojunto))
        lista_retorno = [col[2] for col in cursor.fetchall()]# busca a descricao
        return lista_retorno
        

        
    bancodedados = {
            'Acréscimo' : ('Categoria','ACRÉSCIMO'),       # Acrescimo
            'Tamanho' : ('Categoria','TAMANHO'),           # Tamanhos
            'Produtos' : ('Natureza','Produto Final'),     # Produtos
            'Complementos' : ('Categoria','COMPLEMENTOS'), # Complemntos
            'Coberturas' : ('Categoria','COBERTURAS')}     # Coberturas

    
    # Função para alternar o estado do botão
    def mudar_cor_botao(button,selecao_complementos):
    
        text = button.text
        
        if variavel_global in ['Tamanho',]:
            # Desmarcar todos os botões
            for btn in todos_botoes:
                btn.config(bg="white")
                selecao_complementos.discard(btn.text)
                button_states[btn.text] = False
            
            # Marcar o botão selecionado         
            button.config(bg=cores['Botao selecao'])
            selecao_complementos.add(text)
            button_states[text] = True

            # passar o botao certo para o entry
            fechar_frame_dinamico(frame_topcos)
            tamanho_copos.delete(0,END)
            tamanho_copos.insert(0,text[1])
        

        elif variavel_global == 'Complementos' and entry_produtos.get() == 'MILK - SHAKE':
            # Desmarcar todos os botões se for milk-shake
            for btn in todos_botoes:
                btn.config(bg="white")
                selecao_complementos.discard(btn.text)
                button_states[btn.text] = False
            
            # Marcar o botão selecionado
            button.config(bg=cores['Botao selecao'])
            selecao_complementos.add(text)
            button_states[text] = True
            

        else:
            if text in selecao_complementos:
                button.config(bg="white")
                selecao_complementos.remove(text)
                button_states[text] = False
            else:
                button.config(bg=cores['Botao selecao'])
                selecao_complementos.add(text)
                button_states[text] = True

        # print(selecao_complementos,'<<<RELATORIO')

    # Função para criar um botão com os parâmetros corretos
    def criar_botao(master, row, col, arm, txt_bt, estado_inicial=False):
        button = tk.Button(
            master=master,font='Arial 12 bold',
            text=txt_bt,
            command=lambda: mudar_cor_botao(button, arm),
            bg=cores['Botao selecao'] if estado_inicial else "white"  # Definindo cor inicial
        )
        button.grid(row=row, column=col, padx=5, pady=5, sticky='wnse')
        button.text = (variavel_global,txt_bt)  # Adiciona atributo personalizado 'text'
        if estado_inicial:
            arm.add(button.text)
        if variavel_global in ['Tamanho'] or variavel_global == 'Complementos' and entry_produtos.get() == 'MILK - SHAKE':
            todos_botoes.append(button)  # Adiciona o botão à lista de todos os botões
        
        return button


    

    # Deletar filhos do frame
    def deletar_filhos_frame(frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def posicionar_no_frame_bt(master,valores_bd,selecao_complementos):
        global variavel_global,escopo
        

        deletar_filhos_frame(master)
        axi_coluna = 0
        linha = 0
        itens = valores_bd

        if variavel_global in ['Produtos']:
            global colunasProdutos,largura_colunas_treeview,cores
            entry_produtos.delete(0,END)
            def evento_selecao_produto(event):

                linha = treeview_listar_produto.selection()
                produto_selecionado = treeview_listar_produto.item(linha, "values")
                reiniciar_botoes()
                entry_produtos.insert(0,str(produto_selecionado[1]).upper())
                fechar_frame_dinamico(frame_topcos)

            def filtro_de_produtos(event):
                
                #if - se
                #Verifica se os campos estão vazio
                if not entry_produtos.get():

                    #Se ambos os campos estiverem vazios, não faz nada
                    listar_produtos_salvo()
                    return
                
                sql = f"SELECT Codigo, Descrição FROM Estoque"
                
                params = []
                
            
                # Verifica se ao codigo esta correto
                comando = f'SELECT Codigo, Descrição FROM Estoque WHERE Codigo LIKE ? AND Natureza == ?'
                cursor.execute(comando,(entry_produtos.get() + '%','Produto Final'))
                codigo = cursor.fetchall()
                
                if codigo:
                    if int(entry_produtos.get()).is_integer() == True:
                        sql += " WHERE Codigo LIKE ?" 
                        
                        """
                        Parâmetro de consulta dinamicamente com base 
                        no texto digitado esse curinga % considera qualquer numero de caracteres 
                        antes do padrao de corespondência.
                        """
                        params.append('%' + entry_produtos.get() + '%')

                else:
                   
                    
                    sql += " WHERE Descrição LIKE ?" 
                    
                    """
                    Parâmetro de consulta dinamicamente com base 
                    no texto digitado esse curinga % considera qualquer numero de caracteres 
                    antes do padrao de corespondência.
                    """
                    params.append('%' + str(entry_produtos.get()).title() + '%')

                    
                    
                            
                # passe os valores para o filtro LIKE do banco de dados
                
                params.extend(['Produto Final',0,0])
                cursor.execute(sql + " AND Natureza = ? AND Quantidade > ? AND Preço > ?", tuple(params))
                produtos_vender = cursor.fetchall()
                    
                #Limpa os dados da treeview
                limparTreeview(treeview_listar_produto)
                    
                #Preenche treeview com os dados filtrados
                for index,valor in enumerate(produtos_vender):

                    if index % 2 == 0:# ocorrencia de repeticao 2 em 2 ou 3 em 3
                        treeview_listar_produto.insert("", "end", values=(valor[0], valor[1]), tags=('evenrow',))
                    else:
                        treeview_listar_produto.insert("", "end", values=(valor[0], valor[1]), tags=('oddrow',))
    

            colunasProdutos = ['Codigo','Descrição']
            largura_colunas_treeview = [100,700]# Tamanho das colunasDinamicas do treeview

            # altura,largura,x,y = 336, 1090, 15, 296

            treeview_listar_produto = ttk.Treeview(master,padding=5)
            treeview_listar_produto.pack(fill='both')

            

            # Adicionar barras de rolagem
            scrollbar_y = tk.Scrollbar(treeview_listar_produto, orient=tk.VERTICAL)

            # Criar o Treeview e configurá-lo com barras de rolagem
            treeview_listar_produto = ttk.Treeview(treeview_listar_produto, yscrollcommand=scrollbar_y.set)
            scrollbar_y.config(command=treeview_listar_produto.yview)
            scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
            treeview_listar_produto.pack(fill='both')
            

            
            def listar_produtos_salvo():
                global colunasProdutos,cores,largura_colunas_treeview,listar_produtos_disponiveis_pra_vender
                
                # Adicionando itens a treeview de exibir -----------------------------------------------
                style = ttk.Style()
                style.configure("Custom.Treeview", font=("Arial", 14),
                                background='white',foreground="black",fieldbackground="red")
                style.configure("Treeview.Heading", font = "Arial 10 bold")

                treeview_listar_produto.config(style='Custom.Treeview')
                
                

                #Limpa os valores da treeview_listar_produto
                limparTreeview(treeview_listar_produto)
                
                #Armazena os valores retornados pelo comando SQL em uma variável
                cursor.execute(f"SELECT Codigo, Descrição FROM Estoque WHERE Natureza == ?",('Produto Final',))
                valores = cursor.fetchall()
                

                # modificar o cabeçario dinamico
            

                treeview_listar_produto.config(columns=(colunasProdutos),show="headings")

                # cor linhas treeview
                treeview_listar_produto.tag_configure('oddrow', background='white')
                treeview_listar_produto.tag_configure('evenrow', background=cores['Linha_tre'])

                for i,coluna in enumerate(colunasProdutos):
                    treeview_listar_produto.heading(coluna, text=coluna)
                    treeview_listar_produto.column(coluna,width=largura_colunas_treeview[i],anchor= CENTER)

                # Adiciona cor as linhas do Treeview
                for index,valor in enumerate(valores):

                    if index % 2 == 0:# ocorrencia de repeticao 2 em 2 ou 3 em 3
                        treeview_listar_produto.insert("", "end", values=(valor[0], valor[1]), tags=('evenrow',))
                    else:
                        treeview_listar_produto.insert("", "end", values=(valor[0], valor[1]), tags=('oddrow',))
                
                listar_produtos_disponiveis_pra_vender = [treeview_listar_produto.item(filho, 'values') for filho in treeview_listar_produto.get_children()]


                treeview_listar_produto.bind("<<TreeviewSelect>>", evento_selecao_produto)
                entry_produtos.bind("<KeyRelease>",filtro_de_produtos)
                return

                
            listar_produtos_salvo()

            
        
        else:

            if variavel_global in ['Tamanho']:
                # Limpar a lista de todos os botões antes de adicionar novos

                todos_botoes.clear()
                selecao_complementos = tamanho_set# troca o repositorio

            elif variavel_global == 'Complementos' and entry_produtos.get() == 'MILK - SHAKE':
                todos_botoes.clear()
                

            for coluna, iten in enumerate(itens):
                if coluna % escopo == 0 and coluna != 0:
                    linha += 1
                    axi_coluna = 0
                else:
                    axi_coluna = coluna % escopo
                
                # passar pro estado inicial uma tupla COLUNA E VALOR
                chave = (variavel_global, iten.upper())
                estado_inicial = button_states.get(chave, False)

                criar_botao(master, linha, axi_coluna, selecao_complementos, txt_bt=iten.upper(), estado_inicial=estado_inicial)

    

    def adaptar_framer(variavel,lista):
        global escopo
        # Inicializo as linhas e colunas do frame para depois adaptar
        for i in range(5):  
            frame_topcos.columnconfigure(i, weight=0)
            frame_topcos.rowconfigure(i, weight=0)


        if variavel in ['Acréscimo','Tamanho']:

            # Adaptar tamanho em linha e coluna a coluna simula uma lista suspensa
            frame_topcos.columnconfigure(0,weight=1)
            lista = [t for t in range(int(len(lista)))]
            frame_topcos.rowconfigure(lista,weight=1) 
            escopo = 1
                  
        elif 'Produtos' != variavel:
            lis_ativa = len(lista)
            escopo = ''

            if lis_ativa <= 4:
                escopo = lis_ativa
            else:
                escopo = 4


            for lin in range(escopo):
               
                
                # A propriedade `weight=1` define que cada coluna terá o mesmo peso
                # quando o frame for redimensionado, permitindo que as colunas cresçam proporcionalmente.
                frame_topcos.columnconfigure(lin, weight=1)
 


            # Verifica se o comprimento da lista dividido por "escopo" tem resto.
            # Se tiver resto (não for divisível igualmente), adiciona 1 ao comprimento para ajustar.
            # Isso garante que todos os itens da lista sejam acomodados em linhas, 
            # mesmo que sobrem elementos.
            verificar_resto = lis_ativa + 1 if lis_ativa % escopo != 0 else lis_ativa 
           

            # Cria uma nova lista que contém índices para configurar as linhas do frame.
            # O número de elementos na lista é baseado em "verificar_resto / escopo".
            # Isso divide os elementos da lista igualmente em "escopo" linhas.
            lista = [t for t in range(int(verificar_resto / 2))]
            
            frame_topcos.rowconfigure(lista, weight=1)


    def mudar_valores_milk(variavel_global,entry_produtos,frame_topcos,padding,bancodedados,lar,linha,coluna):
        

        if variavel_global == 'Complementos':
            if entry_produtos == 'MILK - SHAKE':
                ''' Antes de listar o botao tamanho verifico valores'''
                bancodedados.update({'Complementos':('Categoria','SABORES')})
                frame_topcos.config(width=lar,height=120,background=cores['Frame dinamico'])
                frame_topcos.grid(row=linha, column=coluna,columnspan=3, sticky='we',pady=padding)
                

    # Função deixa os frames dinamicos
    def trocar_frame(linha,coluna,lar,botao):
        """Mostra ou oculta o frame principal."""
        
        # Muda o nome de acordo com o botao ativo
        if type(botao) != str:
            botao_ativo = botao.cget('text')
        else: 
            botao_ativo = botao
    
        global variavel_global
        altura_padrao = 190
            
        bancodedados.update({'Complementos':('Categoria','COMPLEMENTOS')})

        # Tratamento para novas interações -------------------------------------------------------
        if botao_ativo != variavel_global:
            # Fecha 
            if frame_topcos.winfo_ismapped():

                # Remova o mapeamento deste widget - Usando grid
                frame_topcos.grid_forget()

                #Abri - 'Coberturas' ou 'Acréscimo'
                if botao_ativo in ['Coberturas','Acréscimo']:
                    frame_topcos.config(width=lar,height=altura_padrao,background=cores['Frame dinamico'])
                    variavel_global = botao_ativo
                    if variavel_global == 'Coberturas':
                        frame_topcos.grid(row=linha, column=coluna,columnspan=3, sticky='we',pady=padding)
                    else:
                        frame_topcos.grid(row=linha, column=coluna,pady=padding)

                    
                elif botao_ativo in 'Tamanho':
                    frame_topcos.config(width=lar,height=210,background=cores['Frame dinamico'])
                    frame_topcos.grid(row=linha, column=coluna,pady=5,sticky='w')
                    variavel_global = botao_ativo
                    
                    
                else:
                    frame_topcos.config(width=lar,height=altura_padrao,background=cores['Frame dinamico'])
                    frame_topcos.grid(row=linha, column=coluna,columnspan=3, sticky='we',pady=padding)
                    variavel_global = botao_ativo
                    mudar_valores_milk(variavel_global,entry_produtos.get(),frame_topcos,padding,bancodedados,lar,linha,coluna)
     
            #Abri 
            else:

                #Abri - 'Coberturas' ou 'Acréscimo'
                if botao_ativo in ['Coberturas','Acréscimo']:
                    frame_topcos.config(width=lar,height=altura_padrao,background=cores['Frame dinamico'])
                    variavel_global = botao_ativo
                    if variavel_global == 'Coberturas':
                        frame_topcos.grid(row=linha, column=coluna,columnspan=3, sticky='we',pady=padding)
                    else:
                        frame_topcos.grid(row=linha, column=coluna,pady=padding)
                

                elif botao_ativo in 'Tamanho':
                    frame_topcos.config(width=lar,height=210,background=cores['Frame dinamico'])
                    frame_topcos.grid(row=linha, column=coluna,pady=5,sticky='w')
                    variavel_global = botao_ativo
                    

                else:
                    frame_topcos.config(width=lar,height=altura_padrao,background=cores['Frame dinamico'])
                    frame_topcos.grid(row=linha, column=coluna,columnspan=3, sticky='we',pady=padding)
                    variavel_global = botao_ativo
                    mudar_valores_milk(variavel_global,entry_produtos.get(),frame_topcos,padding,bancodedados,lar,linha,coluna)
                    

        # Tratamento para quem esta repetindo -------------------------------------------------------
        else:
            
            if frame_topcos.winfo_ismapped():
                # Remova o mapeamento deste widget - Usando grid
                frame_topcos.grid_forget()

            
            #Abri - 'Coberturas' ou 'Acréscimo'
            else:

                #Abri - 'Coberturas' ou 'Acréscimo'
                if botao_ativo in ['Coberturas','Acréscimo']:
                    frame_topcos.config(width=lar,height=altura_padrao,background=cores['Frame dinamico'])
                    if variavel_global == 'Coberturas':
                        frame_topcos.grid(row=linha, column=coluna,columnspan=3, sticky='we',pady=padding)
                    else:
                        frame_topcos.grid(row=linha, column=coluna,pady=padding)

                elif botao_ativo in 'Tamanho':
                    frame_topcos.config(width=lar,height=210,background=cores['Frame dinamico'])
                    frame_topcos.grid(row=linha, column=coluna,pady=5,sticky='w')
                    variavel_global = botao_ativo

                else:
                    frame_topcos.config(width=lar,height=altura_padrao,background=cores['Frame dinamico'])
                    frame_topcos.grid(row=linha, column=coluna,columnspan=3, sticky='we',pady=padding)
                    mudar_valores_milk(variavel_global,entry_produtos.get(),frame_topcos,padding,bancodedados,lar,linha,coluna)
                    
        
        

        # Mudar os valores dos frames 
        frame_topcos.grid_propagate(False)
        lista_buscada_bd = busca_itens_no_bd(bancodedados[variavel_global])

        adaptar_framer(variavel_global,lista_buscada_bd)
        posicionar_no_frame_bt(frame_topcos,lista_buscada_bd,complementos_set)

            


    '''----------------------------------- Criar o botão complementos -----------------------------------'''
    def nenhuma_operacao():
        try:
            trocar_frame()
        except Exception:
            pass  # Silencia qualquer erro

    def permissao_para_framer_complemento(event):
       
        if str(entry_produtos.get()) in ['AÇAI','SORVETE','MILK - SHAKE']:
            botao_complementos.config(command=lambda: trocar_frame(2, 0, largura, botao_complementos))

        else:
            botao_complementos.config(command=nenhuma_operacao)# passsar uma funcao vazia

    complementosImagem = ImageTk.PhotoImage(Image.open(r"img_vendas\button-complementos.png"))
    botao_complementos = Button(frame_axi, text='Complementos',image=complementosImagem, 
                                borderwidth=0, highlightthickness=0,
                                fg="black", bg=cores['Roxo Escuro'], 
                                relief='ridge', width=largura,
                                activebackground=cores['Roxo Escuro'], height=38)

    botao_complementos.grid(row=1, column=0,sticky='we', columnspan=3,pady=padding)
    botao_complementos.bind('<Button-1>', permissao_para_framer_complemento)



    '''-----------------------------------Criar o botão coberturas-----------------------------------'''
    
    def permissao_para_framer_cobertura(event):
        
        if entry_produtos.get() in ['AÇAI','SORVETE']:
            botao_coberturas.config(command=lambda : trocar_frame(4,0,largura,botao_coberturas))
        else:
            botao_coberturas.config(command=nenhuma_operacao)# passsar uma funcao vazia

    coberturaImagem = ImageTk.PhotoImage(Image.open(r"img_vendas\button-coberturas.png"))
    
    botao_coberturas = Button(frame_axi, text='Coberturas',
                            image=coberturaImagem, borderwidth=0,
                            highlightthickness=0,
                                fg="black", bg=cores['Roxo Escuro'], 
                                relief="ridge", width=largura_topcos,
                                activebackground=cores['Roxo Escuro'],height=38)

    botao_coberturas.grid(row=3, column=0,sticky='we',pady=padding)
    botao_coberturas.bind('<Button-1>',permissao_para_framer_cobertura)



    '''-----------------------------------Criar o botão acréscimo-----------------------------------'''
    
    def permissao_para_framer_acrescimo(event):
        
        if entry_produtos.get() in ['AÇAI','SORVETE']:
            botao_acrescimo.config(command=lambda : trocar_frame(4,1,235,botao_acrescimo))
        else:
            botao_acrescimo.config(command=nenhuma_operacao)# passsar uma funcao vazia


    acrescimoImagem = ImageTk.PhotoImage(Image.open(r"img_vendas\button-acrescimo.png"))

    botao_acrescimo = Button(frame_axi, text='Acréscimo',
                            image=acrescimoImagem, borderwidth=0, 
                            highlightthickness=0,
                            activebackground=cores['Roxo Escuro'], fg="black", 
                            bg=cores['Roxo Escuro'], anchor='center',
                            relief="ridge", width=largura_topcos, height=38)

    botao_acrescimo.grid(row=3, column=1,sticky='we',pady=padding)
    botao_acrescimo.bind('<Button-1>',permissao_para_framer_acrescimo)

    '''-----------------------------------Criar o botão +pedido-----------------------------------'''
    
    pedidoImagem = ImageTk.PhotoImage(Image.open(r"img_vendas\button-pedido.png"))

    def pedido():
        global auto_scroll,listar_produtos_disponiveis_pra_vender,entry_unidade_atual
    
        if frame_topcos.winfo_ismapped():
            frame_topcos.grid_forget()

        produto = entry_produtos.get()
        unidade = entry_unidade.get()
        tamanho = tamanho_copos.get()
        lista_produto_axi_disponivel = [produto_disponivel[1] for produto_disponivel in listar_produtos_disponiveis_pra_vender]

        if produto in ['AÇAI', 'SORVETE','MILK - SHAKE'] and tamanho == '':
            messagebox.showwarning('Atenção', 'Seleciona um tamanho.')

        elif produto == 'MILK - SHAKE' and len(complementos_set) == 0:
            messagebox.showwarning('Atenção', 'Verifica se tem algum sabor selecionado.')
        elif unidade == '':
            messagebox.showwarning('Atenção', 'Selecione alguma quantidade.')
        elif produto.title() in lista_produto_axi_disponivel:

            # Descontar no banco de dados
            index = lista_produto_axi_disponivel.index(produto.title())
            cursor.execute(f'SELECT Codigo,Quantidade,Base FROM Estoque WHERE Codigo = ?',(listar_produtos_disponiveis_pra_vender[index][0]))
            produto_atual_a_vender = cursor.fetchall()
            entry_unidade_atual = entry_unidade.get()

          
            for cod,estoque,base in produto_atual_a_vender:
                
                if cod in [1,3,4]:
                    try:
                        # Pegando o tamanho de acordo com o nome passado
                        tamanho_selecionado = int(str(tamanho).replace('ML','')) * int(entry_unidade_atual)
               
                    except:
                        if 'MARMITA' in str(tamanho):
                            tamanho_selecionado = int(550 * int(entry_unidade_atual))

                    atualizar_estoque = int(estoque - tamanho_selecionado)#retirando do estoque
                    percent = int((atualizar_estoque/base)*100)
                    if atualizar_estoque >= 0:
                        if percent <= 20:
                            messagebox.showwarning('Quase no Fim',f'Se organize para turbinar seu estoque, antes que acabe.\nVeja seu estoque atual {estoque} ml.')

                        cursor.execute(f"UPDATE Estoque SET Quantidade = ? WHERE Codigo = ?",(atualizar_estoque,cod))
                        auto_scroll = True
                        preencher_texto()
                        reiniciar_botoes()
                    else:
                        messagebox.showerror('Sem Estoque',f'Produto em falta no estoque.\nVeja seu estoque atual {estoque} ml.')
                        
                else:
                    atualizar_estoque = int(estoque - int(entry_unidade_atual))#retirando do estoque
                    percent = int((atualizar_estoque/base)*100)
                    if atualizar_estoque >= 0:
                        if percent <= 20:
                            messagebox.showwarning('Quase no Fim',f'Se organize para turbinar seu estoque, antes que acabe.\nVeja seu estoque atual {estoque} unidades.')
                            
                        cursor.execute(f"UPDATE Estoque SET Quantidade = ? WHERE Codigo = ?",(atualizar_estoque,cod))
                        auto_scroll = True
                        preencher_texto()
                        reiniciar_botoes()
                        
                    else:
                        messagebox.showerror('Sem Estoque',f'Produto em falta no estoque.\nVeja seu estoque atual {estoque} unidades.')
       
        else:
            messagebox.showerror('Erro', 'Selecione algum produto disponível.')


    botao_pedido = Button(frame_axi, text='+Pedido',
                        borderwidth=0,image=pedidoImagem,
                            highlightthickness=0,command=pedido, 
                                fg="black", bg=cores['Roxo Escuro'], 
                                relief="ridge", width=largura_topcos,
                                activebackground=cores['Roxo Escuro'], height=38)

    botao_pedido.grid(row=3, column=2,sticky='we',pady=padding)





    '''-----------------------------------Criar o entry observaçoes-----------------------------------'''

    def lista_comb(event):
        '''Fecha Frame aberto'''
        if frame_topcos.winfo_ismapped():
            frame_topcos.grid_forget()

    def clear_text(event):
        '''Limpa o text quando selecionado'''
        if entry_observacoes.get("1.0", "end-1c") == padrao_texto:
            entry_observacoes.delete("1.0", "end")

    def restore_text(event):
        '''Retorna o texto padrao'''
        if entry_observacoes.get("1.0", "end-1c") == "":
            entry_observacoes.insert("1.0", padrao_texto)

    def limit_chars(event):
        '''Limita meu text'''
        current_text = entry_observacoes.get("1.0", "end-1c")
        clear_text(event)
        if len(current_text) >= max_caracteres:
            if event.keysym != "BackSpace":
                return "break"


    padrao_texto = "Observações..."
    max_caracteres = 150

    
    entry_observacoes = Text(frame_axi,bd = 0,height=2, 
                             bg = cores['Branca'],highlightthickness = 0,padx=padding,pady=padding, font='Arial 13')
    entry_observacoes.grid(row=5, column=0,sticky='we',columnspan=3,pady=10,padx=5)

    entry_observacoes.bind('<Button-1>',lista_comb)
    entry_observacoes.insert("1.0", padrao_texto)
    entry_observacoes.bind("<FocusIn>", clear_text)
    entry_observacoes.bind("<FocusOut>", restore_text)
    entry_observacoes.bind("<KeyPress>", limit_chars)


    '''-----------------------------------BOTAO Pesquisar cliente-----------------------------------''' 
    
    def buscar_fegues():
        global colunas_fregues,pontuacao,variavel_endereco

        # print(len(text_exibir_pedido.get('1.0',END)))
        janela_fregues = tk.Toplevel(janela_novo_pedido)
        janela_fregues.grab_set()# precisa ser chamado apos a criacao
        janela_fregues.transient(root)  # Manter janela_fregues no topo
        janela_fregues.focus_force()  # Força o foco na janela

        fregues_largura = 1100
        fregues_altura = 600
        janela_fregues.title("Interface de Relátorio")
        janela_fregues.columnconfigure([0, 1], weight=1)
        centralizar_janela(janela_fregues, fregues_largura, fregues_altura,top=30)
        janela_fregues.config(bg=cores['Branca'])
        janela_fregues.resizable(False, False)

        frame_fregues = tk.Frame(janela_fregues, bg=cores["Roxo Escuro"])
        frame_fregues.pack(side="left", fill='both', expand=True)

        canvas_fregues = tk.Canvas(
            frame_fregues,
            bg=cores['Roxo Escuro'],
            height=fregues_altura,
            width=fregues_largura,
            bd=0,
            highlightthickness=0,
            relief="ridge")
        canvas_fregues.pack(fill=tk.BOTH, expand=True)

        segundoImagem = ImageTk.PhotoImage(Image.open(r"img_vendas\bg_fundo_fregues.png"))
        background = canvas_fregues.create_image(fregues_largura / 2, fregues_altura / 2, image=segundoImagem)
        
        
        colunas_fregues = ['Id','Nome','Rua','Numero/Apartamento','Bairro','Tel']
        largura_colunas_treeview = [70,180,200,150,160,150]# Tamanho das colunas_fregues do treeview
        x,y,largura,altura = 22, 163, 1056, 311

        pontuacao = str.maketrans('','',string.punctuation)
        treeview_fregues = ttk.Treeview(canvas_fregues)
        exibir_relatorio = canvas_fregues.create_window(x, y, anchor=tk.NW, width=largura,
                                        height=altura, window=treeview_fregues)
        # Adicionar barras de rolagem
        scrollbar_y = tk.Scrollbar(treeview_fregues, orient=tk.VERTICAL)

        # Criar o Treeview e configurá-lo com barras de rolagem
        treeview_fregues = ttk.Treeview(treeview_fregues, yscrollcommand=scrollbar_y.set)
        scrollbar_y.config(command=treeview_fregues.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        treeview_fregues.pack(fill=tk.BOTH, expand=True)
        
        # cria as colunas
        def listar_colunas_Fregues():
            global colunas_fregues,cores
    
            # Adicionando itens a treeview de exibir -----------------------------------------------
            style = ttk.Style()
            style.configure("Custom.Treeview", font=("Arial", 12),
                            background='white',foreground="black",fieldbackground="red")
            style.configure("Treeview.Heading", font = "Arial 10 bold")

            treeview_fregues.config(style='Custom.Treeview')
            
          
            #Limpa os valores da treeview_fregues
            for i in treeview_fregues.get_children():        
                treeview_fregues.delete(i)
            
            # modificar o cabeçario dinamico
            treeview_fregues.config(columns=(colunas_fregues),show="headings")

            for i,coluna in enumerate(colunas_fregues):
                treeview_fregues.heading(coluna, text=coluna)
                treeview_fregues.column(coluna,width=largura_colunas_treeview[i],anchor= CENTER)

        listar_colunas_Fregues() 
            
        def filtro_fregues(entry_filtro_fregues,treeview_fregues):
            global colunas_fregues,cores
            #if - se
            #Verifica se os campos estão vazio
            if not entry_filtro_fregues.get():

                # Se ambos os campos estiverem vazios, limpar tudo
                listar_colunas_Fregues()       
                return
            
            sql = f"SELECT * FROM Fregues"
            
            params = []
            
            # Verifica se ao codigo esta correto
            comando = f'{sql} WHERE {colunas_fregues[0]} LIKE ?'
            cursor.execute(comando,(entry_filtro_fregues.get() + '%',))
            id = cursor.fetchall()
            
            if id:

                sql += f" WHERE {colunas_fregues[0]} LIKE ?"         
                params.append(entry_filtro_fregues.get() + '%')

            else:
                # Verifica se a categoria esta correto
                digitando_title = str(entry_filtro_fregues.get()).title()
                comando = f'SELECT * FROM Fregues WHERE {colunas_fregues[1]} LIKE ?'
                cursor.execute(comando,(digitando_title + '%',))
                nome = cursor.fetchall()

                if nome:
                
                    sql += f" WHERE {colunas_fregues[1]} LIKE ?" 
                    params.append(digitando_title + '%')

                
                else:
                    # Verifica se a descricao esta correto
                    comando = f'SELECT * FROM Fregues WHERE {colunas_fregues[2]} LIKE ?'
                    cursor.execute(comando,('%' + entry_filtro_fregues.get() + '%',))
                    rua = cursor.fetchall()

                    if rua:
                        sql += f" WHERE {colunas_fregues[2]} LIKE ?" 
                        params.append('%' + entry_filtro_fregues.get() + '%')
                    else:# bairro
                        sql += f" WHERE {colunas_fregues[4]} LIKE ?" 
                        params.append('%' + entry_filtro_fregues.get() + '%')

            
            #Limpa os dados da treeview
            for i in treeview_fregues.get_children():        
                treeview_fregues.delete(i)
            
            cursor.execute(sql , tuple(params))
            todos_fregues = cursor.fetchall()
            
                
            #Preenche treeview com os dados filtrados
            for index,valor in enumerate(todos_fregues):

                if index % 2 == 0:# ocorrencia de repeticao 2 em 2 ou 3 em 3
                    treeview_fregues.insert('', 'end', values=(valor[0], valor[1], valor[2], valor[3], valor[4], valor[5]), tags=('evenrow',))
                else:
                    treeview_fregues.insert('', 'end', values=(valor[0], valor[1], valor[2], valor[3], valor[4], valor[5]), tags=('oddrow',))
       
        altura = 36.29
        largura = 666
        x, y = 215.56+3, 90.04

        padding = 5
        text_x = x + padding
        text_y = y + padding
        text_largura = largura - 2 * padding
        text_altura = altura - 2 * padding


        entry_filtro_fregues = Entry(janela_fregues,bd=0, bg="#ffffff", highlightthickness=0,font='Arial 12',relief='flat')
        filtro_pedido = canvas_fregues.create_window(text_x, text_y,anchor="nw",width=text_largura, 
                            height=text_altura, window=entry_filtro_fregues)

        entry_filtro_fregues.bind("<KeyRelease>",lambda e: filtro_fregues(entry_filtro_fregues,treeview_fregues))


        # botoes / fregues
        def selecionar_fregues_evento(event):
            selecionar_fregues()


        def selecionar_fregues():
            global fregues_selecionados,valores_completo_fregues,variavel_endereco
            selecao_fregues = treeview_fregues.selection()[0]
            
            #Obtém os valores do item selecionado passando a posicao da linha 
            fregues_selecionados = treeview_fregues.item(selecao_fregues)['values']
            variavel_endereco = True
            valores_completo_fregues = f'\nNome  : {fregues_selecionados[1]}\nCel : {fregues_selecionados[5]}\nEnd : {fregues_selecionados[2]}, {fregues_selecionados[3]} {fregues_selecionados[4]}'
            
            janela_fregues.destroy()
            reiniciar_botoes()
            preencher_texto()

        selecionar_img = PhotoImage(file=r"img_vendas\bt_sel_fregues.png")
        x,y,largura,altura = 776,496,302+3,84+7
        botao_selecionar_fregues = tk.Button(canvas_fregues, image=selecionar_img, activebackground='#C1BAC1', 
                                             highlightthickness=0,borderwidth=0,command=selecionar_fregues)
        canvas_fregues.create_window(x, y, anchor=tk.NW,width=largura,
                                       height=altura,window=botao_selecionar_fregues)
        
        def filhos(treeview,coluna):
                '''Verifica se o valor passado já está em uso na coluna passada.'''
                return [treeview.item(filho, "values")[coluna] for filho in treeview.get_children()]


        def adicionar_novo_cliente():
            global pontuacao


            # Criando uma janela secundaria porcima da principal -> Toplevel

            janela_novo_fregues = Toplevel(janela_fregues)#telinha sobre a pai
            janela_novo_fregues.grab_set() # <<<< Trava os elementos que vem por traz 
            janela_novo_fregues.title("Novo Freguês")#titulo
            centralizar_janela(janela_novo_fregues,650,350,top=30)#centralizar tela
            janela_novo_fregues.rowconfigure([0,1,2,3],weight=1)#adaptar seu filhos na linha
            janela_novo_fregues.columnconfigure([0,1],weight=1)#adaptar seu filhos na coluna
            janela_novo_fregues.configure(bg=cores['Linha_tre'])#cor fundo
            janela_novo_fregues.resizable(False,False)#bloquear seu crescimento ou reducao


            # NOME
            Label(janela_novo_fregues,text='Nome:',font=('Arial',16),bg=cores['Linha_tre']).grid(row=0, column=0, padx=10, pady=10, stick="WNS")
            nome_fregues = Entry(janela_novo_fregues, font=("Arial", 16),bg='#FFFFFF')
            nome_fregues.grid(row=0, column=1, padx=10, pady=10,sticky='WENS')
            

            # RUA
            Label(janela_novo_fregues, text="Rua:", font=("Arial", 16), bg=cores['Linha_tre']).grid(row=1, column=0, padx=10, pady=10, stick="WNS")

            rua_fregues = Entry(janela_novo_fregues, 
                                            font=("Arial", 16),bg='#FFFFFF')
            rua_fregues.grid(row=1, column=1, padx=10, pady=10,sticky='WENS')
            
            
            # NUMERO         
            Label(janela_novo_fregues, text="Numero/Apartamento:", font=("Arial", 16), bg=cores['Linha_tre']).grid(row=2, column=0, padx=10, pady=10, stick="WNS")
            numero_fregues = Entry(janela_novo_fregues, 
                                            font=("Arial", 16),bg='#FFFFFF')
            numero_fregues.grid(row=2, column=1, padx=10, pady=10,sticky='WENS')
            


            # BAIRRO
            Label(janela_novo_fregues, text="Bairro:", font=("Arial", 16), bg=cores['Linha_tre']).grid(row=3, column=0, padx=10, pady=10, stick="WNS")
            bairro_fregues = Entry(janela_novo_fregues, 
                                        font=("Arial", 16), bg='#FFFFFF')
            bairro_fregues.grid(row=3, column=1, padx=10, pady=10,sticky='WNES')
        
            

            # TEL
            Label(janela_novo_fregues, text="Telefone ex:(DD98888-8888):", font=("Arial", 16), bg=cores['Linha_tre']).grid(row=4, column=0, padx=10, pady=10, stick="WNS")
            tel_fregues = Entry(janela_novo_fregues, 
                                            font=("Arial", 16), bg='#FFFFFF')
            tel_fregues.grid(row=4, column=1, padx=10, pady=10,sticky='WNES')
            
            def adicionar_fregues():
                global valores_completo_fregues,variavel_endereco
                valores_fregues = (nome_fregues.get().title(), rua_fregues.get().title(),numero_fregues.get(),bairro_fregues.get().title(),tel_fregues.get())
                    
                if len(str(tel_fregues.get()).translate(pontuacao).replace(' ','')) >= 9:
                    if '' not in valores_fregues:
                        if str(tel_fregues.get()).translate(pontuacao).replace(' ','')[-9:] not in [filho.translate(pontuacao).replace(' ','')[-9:] for filho in filhos(treeview_fregues,5)]:
                            
                            
                            # 1° INSERI TUDO QUE TIVER ESCRITO
                            cursor.execute("INSERT INTO Fregues ('Nome','Rua','Numero/Apartamento','Bairro','Tel') Values (?, ?, ?, ?, ?)", 
                                        valores_fregues)
                            if len(text_exibir_pedido.get('1.0',END)) == 1:
                                conexao.commit()
                            janela_novo_fregues.destroy()
                            
                            
                            if messagebox.askokcancel('Use esse endereço','Deseja selecionar o cliente(a) criado?'):
                                variavel_endereco = True
                                valores_completo_fregues = f'\nNome  : {valores_fregues[0]}\nCel : {valores_fregues[4]}\nEnd : {valores_fregues[1]}, {valores_fregues[2]} {valores_fregues[3]}\n'
                                
                                janela_fregues.destroy()
                                reiniciar_botoes()
                                preencher_texto()

                        else:
                            messagebox.showwarning('Opss!','Esse telefone já está sendo usado.')

                    else:
                        messagebox.showwarning('Atenção','Verifica se preencheu todos os campos!\nE tente mais tarde.')
        
            
                else:
                    messagebox.showwarning('Atenção','No campo telefone esperamos no minimo 9 Numeros.')


            botao_salvar = Button(janela_novo_fregues,text='Adicionar',command=adicionar_fregues,font='Arial 16',bg="#008000",fg="#FFFFFF")
            botao_salvar.grid(row=5, column=0,columnspan=1, padx=20, pady=10,sticky='nsew')
            



            botao_cancelar = Button(janela_novo_fregues,text='Cancelar',command=janela_novo_fregues.destroy,font='Arial 16',bg="#FF0000",fg="#FFFFFF")
            botao_cancelar.grid(row=5, column=1,columnspan=1, padx=20, pady=10,sticky='nsew')
                
        
        novo_fregues_img = PhotoImage(file=r"img_vendas\bt_novo_fregues.png")
        x,y,largura,altura = 410,504,255+3,67+7
        botao_novo_fregues = tk.Button(canvas_fregues, image=novo_fregues_img, activebackground='#C1BAC1', 
                                       highlightthickness=0,borderwidth=0,command=adicionar_novo_cliente)
        canvas_fregues.create_window(x, y, anchor=tk.NW,width=largura,
                                       height=altura,window=botao_novo_fregues)
     

        def editar_fregues_treeview():
            try:
                '''Quando o usuario clicar duas vezes sobre as linhas do treeview '''
                
                global colunas_fregues
               
                
                # retorna a posicao da linha selecionada
                posicao_selecionado = treeview_fregues.selection()[0]
                
                #Obtém os valores do item selecionado passando a posicao da linha 
                valores_selecionados = treeview_fregues.item(posicao_selecionado)['values']
                

                # Criando uma janela secundaria porcima da principal -> Toplevel

                janela_edicao_fregues = Toplevel(janela_fregues)#telinha sobre a pai
                janela_edicao_fregues.grab_set() # <<<< Trava os elementos que vem por traz 
                janela_edicao_fregues.title("Editar Freguês")#titulo
                centralizar_janela(janela_edicao_fregues,650,350,top=30)#centralizar tela
                janela_edicao_fregues.rowconfigure([0,1,2,3],weight=1)#adaptar seu filhos na linha
                janela_edicao_fregues.columnconfigure([0,1],weight=1)#adaptar seu filhos na coluna
                janela_edicao_fregues.configure(bg=cores['Linha_tre'])#cor fundo
                janela_edicao_fregues.resizable(False,False)#bloquear seu crescimento ou reducao

                # NOME
                Label(janela_edicao_fregues,text='Nome:',font=('Arial',16),bg=cores['Linha_tre']).grid(row=0, column=0, padx=10, pady=10, stick="WNS")
                nome_fregues = Entry(janela_edicao_fregues, font=("Arial", 16),bg='#FFFFFF',
                                            textvariable=StringVar(value=valores_selecionados[1]))
                nome_fregues.grid(row=0, column=1, padx=10, pady=10,sticky='WENS')
                

                # RUA
                Label(janela_edicao_fregues, text="Rua:", font=("Arial", 16), bg=cores['Linha_tre']).grid(row=1, column=0, padx=10, pady=10, stick="WNS")

                rua_fregues = Entry(janela_edicao_fregues, 
                                                font=("Arial", 16),bg='#FFFFFF',
                                                textvariable=StringVar(value=valores_selecionados[2]))
                rua_fregues.grid(row=1, column=1, padx=10, pady=10,sticky='WENS')
                
              
                # NUMERO         
                Label(janela_edicao_fregues, text="Numero/Apartamento:", font=("Arial", 16), bg=cores['Linha_tre']).grid(row=2, column=0, padx=10, pady=10, stick="WNS")
                numero_fregues = Entry(janela_edicao_fregues, 
                                                font=("Arial", 16),bg='#FFFFFF',
                                                textvariable=StringVar(value=valores_selecionados[3]))
                numero_fregues.grid(row=2, column=1, padx=10, pady=10,sticky='WENS')
                


                # BAIRRO
                Label(janela_edicao_fregues, text="Bairro:", font=("Arial", 16), bg=cores['Linha_tre']).grid(row=3, column=0, padx=10, pady=10, stick="WNS")
                bairro_fregues = Entry(janela_edicao_fregues, 
                                            font=("Arial", 16), bg='#FFFFFF',textvariable=StringVar(value=valores_selecionados[4]))
                bairro_fregues.grid(row=3, column=1, padx=10, pady=10,sticky='WNES')
            
                

                # TEL
                Label(janela_edicao_fregues, text="Telefone ex:(DD98888-8888):", font=("Arial", 16), bg=cores['Linha_tre']).grid(row=4, column=0, padx=10, pady=10, stick="WNS")
                tel_fregues = Entry(janela_edicao_fregues, 
                                                font=("Arial", 16), bg='#FFFFFF',
                                                textvariable=StringVar(value=valores_selecionados[5]))
                tel_fregues.grid(row=4, column=1, padx=10, pady=10,sticky='WNES')
             


                # BOTAO EDITAR (JANELA EDICAO DE DADOS) -------------------------------------------------------------------------------------|
                                
                def salvar_edicao():
                    global valores_fregues,pontuacao
               
                    id_selecionado = valores_selecionados[0] # recupero o id selecionado

                    valores_fregues = (id_selecionado, nome_fregues.get().title(), rua_fregues.get().title(),numero_fregues.get(),bairro_fregues.get().title(),tel_fregues.get())
                    #Pego a posição da linha selecionada e passo ou os mesmo valor ou novos
                    if len(str(tel_fregues.get()).translate(pontuacao).replace(' ','')) >= 9:
                        if '' not in valores_fregues:
                            if str(tel_fregues.get()).translate(pontuacao).replace(' ','')[-9:] not in [filho.translate(pontuacao).replace(' ','') for filho in filhos(treeview_fregues,5)][-9:]:
                                
                                treeview_fregues.item(posicao_selecionado,values=valores_fregues)
                                cursor.execute(r'UPDATE Fregues SET Nome = ?, Rua = ?, "Numero/Apartamento" = ?, Bairro = ?, Tel = ? WHERE Id = ?',
                                            (valores_fregues[1], valores_fregues[2],valores_fregues[3],valores_fregues[4],valores_fregues[5],id_selecionado))
                                
                                if len(text_exibir_pedido.get('1.0',END)) == 1:
                                    conexao.commit() #Gravando no BD

                            else:
                                
                                treeview_fregues.item(posicao_selecionado,values=valores_fregues)
                                cursor.execute(r'UPDATE Fregues SET Nome = ?, Rua = ?, "Numero/Apartamento" = ?, Bairro = ? WHERE Id = ?',
                                            (valores_fregues[1], valores_fregues[2],valores_fregues[3],valores_fregues[4],id_selecionado))
                               
                                if len(text_exibir_pedido.get('1.0',END)) == 1:
                                    conexao.commit() #Gravando no BD
                            
                            #Destruir tela cadrastrar
                            janela_edicao_fregues.destroy()
                            
                        else:
                            messagebox.showwarning('Atenção','Verifica se preencheu todos os campos!\nE tente mais tarde.')
                    
                    else:
                        messagebox.showwarning('Atenção','No campo telefone esperamos no minimo 9 Numeros.')
            
                    
            


                botao_salvar = Button(janela_edicao_fregues,text='Editar',command=salvar_edicao,font='Arial 16',bg="#008000",fg="#FFFFFF")
                botao_salvar.grid(row=5, column=0,columnspan=1, padx=20, pady=10,sticky='nsew')
                
                def deletar_fregues():

                    linha = treeview_fregues.selection()[0]
                    valores_selecionados = treeview_fregues.item(linha)['values']
                    opcao_mensagem = messagebox.askokcancel("Atenção", "Deseja deletar esse freguês?")

                    if opcao_mensagem:
                        
                        # removi do meu banco de dados
                        cursor.execute(f"DELETE FROM Fregues WHERE Id = ?",(valores_selecionados[0]))
                        
                        if len(text_exibir_pedido.get('1.0',END)) == 1:
                            conexao.commit()
                        
                        entry_filtro_fregues.delete(0,END)
                        janela_edicao_fregues.destroy()
                        listar_colunas_Fregues() 
                        
                        messagebox.showinfo("Sucesso", "Freguês removido com sucesso!")  
                botao_cancelar = Button(janela_edicao_fregues,text='Deletar',command=deletar_fregues,font='Arial 16',bg="#FF0000",fg="#FFFFFF")
                botao_cancelar.grid(row=5, column=1,columnspan=1, padx=20, pady=10,sticky='nsew')
                
            

            except Exception as e:
                logging.error(f"Erro ocorreu: {e}")
                messagebox.showwarning('Atenção','Selecione um FREGUÊS primeiro para editá-lo!')



        editar_fregues_img = PhotoImage(file=r"img_vendas\bt_edit_fregues.png")
        x,y,largura,altura = 216,505,161+3,67+7
        botao_editar_fregues = tk.Button(canvas_fregues, image=editar_fregues_img, activebackground='#C1BAC1', 
                                         highlightthickness=0,command=editar_fregues_treeview,borderwidth=0)
        canvas_fregues.create_window(x, y, anchor=tk.NW,width=largura,
                                       height=altura,window=botao_editar_fregues)
        treeview_fregues.bind('<Double-1>',selecionar_fregues_evento)
        

        def balcao_op():
            global variavel_endereco
            if messagebox.askokcancel('Restaurar','Deseja voltar para opção "Balcão"?'):
                variavel_endereco = None
                
                janela_fregues.destroy()
                reiniciar_botoes()
                preencher_texto()
        


        delete_img = PhotoImage(file=r"img_vendas\bt_bal_fregues.png")
        x,y,largura,altura = 22,505,161+3,67+7
        botao_delete_fregues = tk.Button(canvas_fregues, image=delete_img, activebackground='#C1BAC1', 
                                         highlightthickness=0,borderwidth=0,command=balcao_op)
        canvas_fregues.create_window(x, y, anchor=tk.NW,width=largura,
                                       height=altura,window=botao_delete_fregues)

        root.wait_window(janela_fregues)

    imgcli = PhotoImage(file = r"img_vendas\button-cliente.png")
    altura = 51
    largura = 321
    x,y = 856,12


    bt_cliente = Button(canvas_novo_pedido,image = imgcli, borderwidth = 0, activebackground="#938E94",highlightthickness = 0, 
                        command = buscar_fegues, fg="black",relief = "ridge")
    bt_cliente.place(x=x, y=y, width=largura, height=altura)



    '''----------------------------------- BOTAO EXIBIR PEDIDO -----------------------------------'''

    global data_atual,horas_atual,tipo,variavel_pagamento,ativo_pagamento,modelo_forma_de_pagamento,numero_pedido,calculo_acrescimo,dicionario_relatorio,variavel_endereco,entrega_taxa
    
    data_atual = None
    horas_atual = None
    tipo = 'Balcao'
    variavel_endereco = None
    bacup_pedido = []
    variavel_pagamento = False
    ativo_pagamento = False
    modelo_forma_de_pagamento = []
    dicionario_relatorio = defaultdict(list) #para inicializar automaticamente listas vazias
    entrega_taxa = ''

    # Executar a consulta SQL com o parâmetro correto
    def armazenar_texto(texto):
        r"""
        Converte uma string multi-linha em uma única linha, substituindo quebras de linha reais por '\n'.
        """
        return texto.replace("\n", "\\n")

    def buscar_numero_proximo_pedido():
        
        cursor.execute("SELECT * FROM Pedidos WHERE Data == ?",(data_atual))
        lista_retorno = cursor.fetchall()
        return len(lista_retorno)+1
    
    

    def data_dinamica():
        global data_atual,horas_atual
        agora = datetime.now()
        separacao = str(agora.date()).split('-')
        data_atual = f'{separacao[2]}/{separacao[1]}/{separacao[0]}'
        horas_atual = str(agora.time())[:5]
        return "{} - {}".format(data_atual,horas_atual)
    
    data_dinamica()
    buscar_numero_proximo_pedido()
    numero_pedido = buscar_numero_proximo_pedido()

    
    def dicioanrio_relatorio_dinamico(chave,uni,valor_unitario):
        '''Armazena valor unicos de cada pedido, nao a soma do total.'''
        global dicionario_relatorio
        tupla = (uni, valor_unitario)
        
        if chave != '':
            dicionario_relatorio[chave].append(tupla)
            dicionario_relatorio.update({f'{chave}' : dicionario_relatorio[chave]})
            
            

    def preencher_texto():
        '''Cada ação dessa função adiciona um pedido - atualiza endereco ou forma de pagamento.'''
        global ativo_pagamento,variavel_pagamento,dicionario_agrupado,valor_do_pedido,text_total,valores_completo_fregues,tipo,entrega_taxa
       
        
        modelo = []
        dicionario_agrupado = {
            'Complementos' : [],
            'Acréscimo' : [],
            'Coberturas' : []
        }
        def calcular_distancia_total(nu,text):
            valor_total = len(text)
            return nu - valor_total
        # Atualizando o dicionario_agrupado
        
        topcos_escolidos_vendendo = [dicionario_agrupado[chave].append(str(valor).title()) for chave,valor in complementos_set]
        
        # LIMPAR A FOLHA DE PEDIDO
         
        text_exibir_pedido.delete("1.0", tk.END)
        try:
            exbir_total_tela()# atualizar o total na tela
        except:
            pass
        # ENDEREÇO

        if variavel_endereco:
            tipo = 'Entrega'
            rascunho_endereco = '{}'.format(valores_completo_fregues)
        else:
            tipo = 'Balcao'
            rascunho_endereco = ''

        # CABEÇARIO
        
        pos = calcular_distancia_total(29,str(numero_pedido))
        
        rascunho_cabecario = '''N°{}{:>{}}\n\nTipo : {}'''.format(numero_pedido,data_dinamica(),pos,tipo)

        # PEDIDO
        
        if len(entry_produtos.get()) > 0:

            # print(entry_observacoes.get("1.0", tk.END),'observaçoes',len(entry_observacoes.get("1.0", tk.END)))
            modelo.append('\n\n{}° Pedido           +R$ {}\n--------------------------------'.format(len(bacup_pedido)+1,str(valor_do_pedido).replace('.',',')))
            
            #observação
            if len(entry_observacoes.get("1.0", tk.END)) <= 1 : entry_observacoes.insert("1.0", 'Observações...')
            
            modelo.append(f'obs: {str(entry_observacoes.get("1.0", tk.END).capitalize())}') if 'Observações...' not in str(entry_observacoes.get("1.0", tk.END)) else ''

            #unidade/produto/tamanho
            modelo.append(f"{entry_unidade_atual}UN - {entry_produtos.get()} - {tamanho_copos.get()}\n") if tamanho_copos.get() else modelo.append(f"{entry_unidade_atual}UN - {entry_produtos.get()}\n")

            
            
            #complementos
            modelo.append("      {}\n".format('\n      '.join(dicionario_agrupado['Complementos']))) if dicionario_agrupado['Complementos'] else ''
            
            #coberturas
            # modelo.append(f"Cobertura:\n      {'\n      '.join(dicionario_agrupado['Coberturas'])}\n") if dicionario_agrupado['Coberturas'] else ''
            modelo.append("Cobertura:\n      {}\n".format('\n      '.join(dicionario_agrupado['Coberturas']))) if dicionario_agrupado['Coberturas'] else ''

            
            #acrescimo
            modelo.append("Acréscimo:\n      {}\n".format('\n      '.join(dicionario_agrupado['Acréscimo']))) if  dicionario_agrupado['Acréscimo'] else ''
            

            rascunho_pedido = '\n'.join(modelo)


        else:
            rascunho_pedido = ''
        

        

        # Cabeçario------------------------------------------------------
        insert_text(rascunho_cabecario)
        # text_exibir_pedido.insert(tk.END, rascunho_cabecario)

        # ENDEREÇO-------------------------------------------------------
        insert_text(rascunho_endereco)
        # text_exibir_pedido.insert(tk.END, rascunho_endereco)

        # PEDIDO --------------------------------------------------------
        try:
            # so irá salvar caso conter valores
            if rascunho_pedido != '':
                bacup_pedido.append(rascunho_pedido)
                # colocando os pedidos ja registrado e os novos
            for pedido in bacup_pedido:
                insert_text(pedido)
                # text_exibir_pedido.insert(tk.END, pedido)
        except:
            pass
        
        # FORMA DE PAGAMENTO --------------------------------------------

        if variavel_pagamento:

            text_total = str(bt_total.cget('text'))
            pos = calcular_distancia_total(32,text_total)
            insert_text(modelo_forma_de_pagamento)
            insert_text('\nTotal :{:>{}}\n\n'.format(text_total,pos))
            # Definindo a tag 'negrito'
            text_exibir_pedido.tag_configure('negrito', font=('Arial', 13, 'bold'))
            variavel_pagamento = False
            ativo_pagamento = True

        else:
            ativo_pagamento = False
            if entrega_taxa:# se ela existir
                total_atual_tela = str(bt_total.cget('text')).replace('R$ ','').replace(',','.')
                calculo = f'{float(total_atual_tela) - entrega_taxa:.2f}'.replace('.',',')
                bt_total['text'] = f'R$ {calculo.replace(".", ",")}'
                entrega_taxa = ''

        
        produto_axi = f'{str(entry_produtos.get()).title()}' if entry_produtos.get() else ''
        dicioanrio_relatorio_dinamico(produto_axi,int(entry_unidade_atual),valor_do_pedido)


        

    x, y = 852, 69
    largura, altura = 318, 570
    padding = 20
    pos_scroll = 19

    text_x = x + padding
    text_y = y + padding
    text_largura = largura - 2 * padding
    text_altura = altura - 2 * padding

    def on_scroll(*args):
        global auto_scroll
        auto_scroll = False  # Desativa o scroll automático quando o usuário interage manualmente
        text_exibir_pedido.yview(*args)
    
    def insert_text(text):
        if 'Total :' in text and 'R$' in text:
            text_exibir_pedido.insert(tk.END, text, 'negrito')
        else:
            text_exibir_pedido.insert(tk.END, text)
        if auto_scroll:
            text_exibir_pedido.yview_moveto(1.0)  # Scroll para o final automaticamente

    def on_text_change(event):
        if auto_scroll:
            text_exibir_pedido.yview_moveto(1.0)  # Scroll para o final quando o texto é inserido

    def bloquear_texto(event):
            return 'break'
    
    img_exibir = PhotoImage(file = r"img_vendas\text-exibir-pedido.png")
    exibir_fundo = canvas_novo_pedido.create_image(x, y,image = img_exibir, anchor="nw")


    text_exibir_pedido = Text(janela_novo_pedido,bd = 0, bg = "#ffffff",wrap=tk.WORD,highlightthickness = 0,padx=padding,pady=padding, font='Arial 13')
    text_exibir_pedido.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Para colocar o scroll preciso dizer onde ele irar acoplar primeiro se e na tela ou em um objeto
    scrollbar = tk.Scrollbar(canvas_novo_pedido, orient=tk.VERTICAL, command=on_scroll)
    canvas_novo_pedido.create_window(1149, 88, anchor="nw", height=520, window=scrollbar)
    text_exibir_pedido.config(yscrollcommand=scrollbar.set)
    # scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas_novo_pedido.create_window(text_x, text_y - 15, anchor="nw", width=text_largura - 14, 
                                        height=text_altura, window=text_exibir_pedido)
    # Variável para controlar o scroll automático
    auto_scroll = True

    # Vincula o evento de alteração do texto ao `on_text_change`
    text_exibir_pedido.bind("<<Modified>>", on_text_change)
    text_exibir_pedido.bind("<KeyRelease>", lambda event: text_exibir_pedido.edit_modified(False))
    text_exibir_pedido.bind('<KeyPress>', bloquear_texto)
    text_exibir_pedido.bind('<KeyRelease>', bloquear_texto)

    # ---------------------------------------------------------------------------------------------------------
    # BOTAO FINALIZAR -----------------------------------
    def finalizar_pedido():
        global numero_pedido, tipo, data_atual, horas_atual, dicionario_relatorio,calculo

        if ativo_pagamento:
            pedido = armazenar_texto(text_exibir_pedido.get('1.0', END))
           
            dicionario_relatorio = tuple(dicionario_relatorio.items())
            cursor.execute("INSERT INTO Pedidos (Numero, Tipo, Pedido, Relatorio,Lançamento, Data, Hora, Total) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (numero_pedido, tipo, pedido, str(dicionario_relatorio),'False', data_atual, horas_atual, float(calculo)))
            conexao.commit()
            
            janela_novo_pedido.destroy()
            listar_historico_pedido()

            
        else:
            # print(ativo_pagamento)
            messagebox.showwarning('Erro ao Finalizar', f"Selecione um modo de Pagamento primeiro!\n(E tente mais tarde).")

    


    finaliza_img = PhotoImage(file = r"img_vendas\button-Finalizar.png")
    altura = 95
    largura = 257
    x,y = 556,542

    
    bt_finalizar = Button(canvas_novo_pedido,image = finaliza_img, borderwidth = 0,activebackground="#938E94", highlightthickness = 0, 
                command = finalizar_pedido,relief = "ridge")
    bt_finalizar.place(x=x, y=y, width=largura, height=altura)

    # ---------------------------------------------------------------------------------------------------------
    # Label TOTAL -----------------------------------
    calculo_acrescimo = 0
    def exbir_total_tela():
        '''Essa funcao tem o proposito de calcular o total de forma dinamica'''
        global dicionario_agrupado,calculo_acrescimo,valor_do_pedido,calculo,entry_unidade_atual,entrega_taxa
      
        unidade = int(entry_unidade_atual)
        
        
        dic_acrescimo = dicionario_agrupado['Acréscimo']
        calculo_acres_axi = 0
        valor_do_pedido = 0  # Valor padrão em caso de erro ou ausência de resultados

        try:
            # Para o 'açai-sorvete-milk', calcular pelo 'preço do tamanho copo'
            tamanho_recuperado = tamanho_copos.get().title()  # Recupera o tamanho
            cursor.execute("SELECT Preço FROM Estoque WHERE Descrição == ?", (tamanho_recuperado,))
            resultado = cursor.fetchall()
        
            if resultado:
                if len(dic_acrescimo) > 0:
                    for acre in dic_acrescimo:
                        tamanho_recuperado = tamanho_copos.get().title()  # Recupera os acrescimo
                        cursor.execute("SELECT Preço FROM Estoque WHERE Descrição == ?", (acre,))
                        acrescimo_valor = cursor.fetchall()
                        calculo_acres_axi += acrescimo_valor[0][0] * unidade
                   
                valor_do_pedido = (resultado[0][0] * unidade) + calculo_acres_axi   # Multiplicando pelo entry de unidades
                
                
                
            
        except Exception as e:
            print(f"Erro ao calcular pelo tamanho do copo: {e}")

        if not valor_do_pedido:
            try:
                # Os demais produtos são calculados pelo seu tamanho no banco de dados
                produto_recuperado = entry_produtos.get().title()
                cursor.execute("SELECT Preço FROM Estoque WHERE Descrição == ?", (produto_recuperado,))
                resultado = cursor.fetchall()
                if resultado:
                    
                    valor_do_pedido = resultado[0][0] * unidade  # Multiplicando pelo entry de unidades
            except Exception as e:
                print(f"Erro ao calcular pelo produto: {e}")

        # Atualiza o botão com o valor total calculado

        bt_total_limpo = str(bt_total['text']).replace('R$', '').replace(',', '.')
        calculo = f'{valor_do_pedido + float(bt_total_limpo):.2f}'
        bt_total['text'] = f'R$ {calculo.replace(".", ",")}'
        calculo_acrescimo += calculo_acres_axi
        

    total_img = PhotoImage(file = r"img_vendas\entry-total.png")
    altura = 95
    largura = 233
    x,y = 293,542
    padding = 5


    bt_total = Label(canvas_novo_pedido,image = total_img, text = 'R$ 0,00', borderwidth = 0, highlightthickness = 0, 
            compound='center',fg="black",font=('Arial', 32, 'bold'))
    bt_total.place(x=x, y=y, width=largura, height=altura)


    # ---------------------------------------------------------------------------------------------------------
    # BOTAO FORMA-PAGAMENTO -----------------------------------

    
    def criarTelaPagamentos():
        # global bt_total
        
        total_atual_tela = str(bt_total.cget('text')).replace('R$ ','')

        if total_atual_tela == '0,00':
            return  # Encerra a função caso o total seja zero

        janela_pagamento = tk.Toplevel(janela_novo_pedido)
        janela_pagamento.grab_set() # <<<< Trava os elementos que vem por traz
        janela_pagamento.title("Forma de Pagamentos")#titulo
        
        
        altura_pagamentos = 649
        largura_pagamentos = 702
        canvas_pagamentos = Canvas(
            janela_pagamento,
            bg = "#ffffff",
            height = altura_pagamentos,
            width = largura_pagamentos,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge")
        canvas_pagamentos.place(x = 0, y = 0)
        background_img = PhotoImage(master=janela_pagamento,file = r"img_vendas\fundo-pagamento.png")
        canvas_pagamentos.create_image(largura_pagamentos/2, altura_pagamentos/2, #posicionar a imagem pelo centro da janela_novo_pedido 
            image=background_img)

        
        global configurar_entry
        
        
        # RADION-----------------------------------------------------------------------------------------
        def rezetar_padrao():

            list_entry = (entry_pix,entry_dinheiro,entry_cartao,entry_troco,entry_entrega)

            for entry_selecionado in list_entry:

                entry_selecionado.delete(0,END)
                entry_selecionado.insert(0,'0,00')
        
        
        def pass_total():
            global entradas
            
            # 1° rezetar todos os campos para o padrao
            rezetar_padrao()
            
            
            # Dicionário para mapear as entradas e variáveis associadas
            entradas = {
                'PIX': entry_pix,
                'DINHEIRO': entry_dinheiro,
                'CARTAO': entry_cartao
            }

            # Variável selecionada

        

            # 2° Passar o total para a opção selecionada
            if varAXI.get() in entradas:
                entrada_selecionada = entradas[varAXI.get()]
                entrada_selecionada.delete(0, tk.END)
                entrada_selecionada.insert(0, entry_total_label.get())
                



        # Criando uma imagem para simular o botão de rádio maior
        selected_image = PhotoImage(file=r"img_vendas\clicado_modo_pagamento.png")  # Tamanho do círculo selecionado
        
        unselected_image = PhotoImage(file=r"img_vendas\nao_clicado_modo_pagamento.png")  # Tamanho do círculo não selecionado


        # Nenhum valor correspondente à lista é atribuído inicialmente
        varAXI = tk.StringVar(value='nd')

        listaOp = ['PIX', 'DINHEIRO', 'CARTAO']

        x, y = 163, 132
        btEco = tk.Radiobutton(janela_pagamento, bd=0,background= 'white',variable=varAXI, value=listaOp[0], command=pass_total,
                            image=unselected_image, selectimage=selected_image, selectcolor='white',indicatoron=False, compound="left")
        btEco.place(x=x, y=y)

        x, y = 382, 132
        btExe = tk.Radiobutton(janela_pagamento,bd=0, background= 'white',variable=varAXI, value=listaOp[1], command=pass_total,
                            image=unselected_image, selectimage=selected_image,selectcolor='white', indicatoron=False, compound="left")
        btExe.place(x=x, y=y)

        x, y = 578, 132
        btPri = tk.Radiobutton(janela_pagamento,bd=0,  background= 'white',variable=varAXI, value=listaOp[2], command=pass_total,
                            image=unselected_image, selectimage=selected_image,selectcolor='white', indicatoron=False, compound="left")
        btPri.place(x=x, y=y)
        
        # Botoes STATUS DE PAGAMENTO
        

        varAXI_STATUS = tk.StringVar(value='NÃO PAGO !!!')
        lista_STATUS = ['PAGO ***', 'NÃO PAGO !!!']

        x, y = 206, 524
        btEco = tk.Radiobutton(janela_pagamento, bd=0,background= 'white',variable=varAXI_STATUS, value=lista_STATUS[0],
                            image=unselected_image, selectimage=selected_image, selectcolor='white',indicatoron=False, compound="left")
        btEco.place(x=x, y=y)

        x, y = 554, 521
        btEco = tk.Radiobutton(janela_pagamento, bd=0,background= 'white',variable=varAXI_STATUS, value=lista_STATUS[1],
                            image=unselected_image, selectimage=selected_image, selectcolor='white',indicatoron=False, compound="left")
        btEco.place(x=x, y=y)
        
        # ENTRY -----------------------------------------------------------------------------------------
        
        def atualizar_valor(*args):

            # Valor original fixo do total
            valor_original = float(str(entry_total_label.get()).replace(",", "."))  
            valor_referencia = valor_original  # Sempre começar com o valor original

            # Determina qual campo será o principal com base na escolha dinâmica
            if varAXI.get() == 'PIX':
                campo_principal = entry_pix
                campo_aux_1 = entry_dinheiro
                campo_aux_2 = entry_cartao
            elif varAXI.get() == 'DINHEIRO':
                campo_principal = entry_dinheiro
                campo_aux_1 = entry_pix
                campo_aux_2 = entry_cartao
            elif varAXI.get() == 'CARTAO':
                campo_principal = entry_cartao
                campo_aux_1 = entry_pix
                campo_aux_2 = entry_dinheiro

            # Recupera os valores dos Entry widgets
            valor_campo_principal = float(campo_principal.get().replace(",", ".")) if str(campo_principal.get()) else 0.0
            valor_aux_1 = float(campo_aux_1.get().replace(",", ".")) if campo_aux_1.get() else 0.0
            valor_aux_2 = float(campo_aux_2.get().replace(",", ".")) if campo_aux_2.get() else 0.0
            valor_aux_3 = float(entry_entrega.get().replace(",", ".")) if entry_entrega.get() else 0.0

            # Calcula a soma dos valores auxiliares
            soma_aux = valor_aux_1 + valor_aux_2

          

            # Adiciona valor_aux_3 ao valor de referência
            novo_valor = valor_referencia + valor_aux_3

            # Limpa o campo principal
            campo_principal.delete(0, tk.END)
            campo_principal.insert(0, f"{novo_valor:.2f}".replace(".", ","))

            

            # Se a soma dos auxiliares for maior ou igual ao valor de referência, resetar os auxiliares
            if soma_aux > valor_referencia:
                for campo in [campo_aux_1, campo_aux_2]:
                    campo.delete(0, tk.END)
                    campo.insert(0, '0,00')

                # Redefine o campo principal para o valor original
                campo_principal.delete(0, tk.END)
                campo_principal.insert(0, f"{novo_valor:.2f}".replace(".", ","))

            # Se a soma for zero, também resetar os campos auxiliares
            elif soma_aux == 0:
                for campo in [campo_aux_1, campo_aux_2]:
                    campo.delete(0, tk.END)
                    campo.insert(0, '0,00')

                # Redefine o campo principal para o valor original
                campo_principal.delete(0, tk.END)
                campo_principal.insert(0, f"{novo_valor:.2f}".replace(".", ","))

            elif soma_aux:
                # Subtrai a soma dos campos auxiliares (valor_aux_1 e valor_aux_2)
                novo_valor -= soma_aux

                # Insere o novo valor no campo principal, formatado como moeda
                
                campo_principal.delete(0, tk.END)
                campo_principal.insert(0, f"{novo_valor:.2f}".replace(".", ","))
            
              
    
        # Entry - Total -------------------------
        x,y,largura,altura = 445,179,157,56

        padding = 5
        text_x = x + padding
        text_y = y + padding
        text_largura = largura - 2 * padding
        text_altura = altura - 2 * padding

        entry_total_label = Entry(janela_pagamento,
            bd = 0,
            bg = cores['Branca'],
            highlightthickness = 0,font='Arial 20',justify='center')
        entry_total_label.place(x=text_x, y=text_y, width=text_largura, height=text_altura)
        
        entry_total_label.bind('<KeyPress>', bloquear_texto)
        entry_total_label.bind('<KeyRelease>', bloquear_texto)
    
        # Entry - pix ---------------------------
        x,y,largura,altura = 445,244,157,41
        padding = 5
        text_x = x + padding
        text_y = y + padding
        text_largura = largura - 2 * padding
        text_altura = altura - 2 * padding
        entry_pix = Entry(janela_pagamento,
            bd = 0,
            bg = '#938E94',
            highlightthickness = 0,font='Arial 18',justify='center')
        entry_pix.place(x=text_x, y=text_y, width=text_largura, height=text_altura)


        # Entry - dinheiro ---------------------------
        x,y,largura,altura = 445,294,157,42
        padding = 5
        text_x = x + padding
        text_y = y + padding
        text_largura = largura - 2 * padding
        text_altura = altura - 2 * padding
        entry_dinheiro = Entry(janela_pagamento,
            bd = 0,
            bg = '#938E94',
            highlightthickness = 0,font='Arial 18',justify='center')
        entry_dinheiro.place(x=text_x, y=text_y, width=text_largura, height=text_altura)
    
        # Entry - cartao ---------------------------
        x,y,largura,altura = 445,344,157,42
        padding = 5
        text_x = x + padding
        text_y = y + padding
        text_largura = largura - 2 * padding
        text_altura = altura - 2 * padding
        entry_cartao = Entry(janela_pagamento,
            bd = 0,
            bg = '#938E94',
            highlightthickness = 0,font='Arial 18',justify='center')
        entry_cartao.place(x=text_x, y=text_y, width=text_largura, height=text_altura)
        
        # Entry - troco ---------------------------
        x,y,largura,altura = 445,395,157,42
        padding = 5
        text_x = x + padding
        text_y = y + padding
        text_largura = largura - 2 * padding
        text_altura = altura - 2 * padding
        entry_troco = Entry(janela_pagamento,
            bd = 0,
            bg = '#938E94',
            highlightthickness = 0,font='Arial 18',justify='center')
        entry_troco.place(x=text_x, y=text_y, width=text_largura, height=text_altura)

        # Entry - Taxa entrega ---------------------------
        x,y,largura,altura = 445,446,157,42
        padding = 5
        text_x = x + padding
        text_y = y + padding
        text_largura = largura - 2 * padding
        text_altura = altura - 2 * padding
        entry_entrega = Entry(janela_pagamento,
            bd = 0,
            bg = '#938E94',
            highlightthickness = 0,font='Arial 18',justify='center')
        entry_entrega.place(x=text_x, y=text_y, width=text_largura, height=text_altura)
        
        # Chamando funcao que editar as teclas
        configurar_entry(entry_pix)
        configurar_entry(entry_dinheiro)
        configurar_entry(entry_cartao)
        configurar_entry(entry_troco)
        configurar_entry(entry_entrega)

        # Vinculando os eventos de teclas para atualizar valores ao soltar uma tecla
        entry_pix.bind("<KeyRelease>", atualizar_valor)
        entry_dinheiro.bind("<KeyRelease>", atualizar_valor)
        entry_cartao.bind("<KeyRelease>", atualizar_valor)
        entry_entrega.bind("<KeyRelease>", atualizar_valor)
        # BOTÕES -----------------------------------------------------------------------------------------
        
        # Botao - Confirmar
        global entrega_taxa

        if entrega_taxa:# retirar valores pendente de taxa de entrega
            total_atual_tela = str(bt_total.cget('text')).replace('R$ ','').replace(',','.')
            calculo = f'{float(total_atual_tela) - entrega_taxa:.2f}'.replace('.',',')
            entry_total_label.insert(0,calculo)
            

        else:
            entry_total_label.insert(0,total_atual_tela)

        def montar_variavel_pagamento():
            
            global variavel_pagamento, modelo_forma_de_pagamento,entrega_taxa

            modelo_forma_de_pagamento = []
            list_entry = (entry_pix, entry_dinheiro, entry_cartao)
            
            entrega_taxa = ''
            

            if varAXI.get() != 'nd':
                variavel_pagamento = True

                try:
                    if variavel_pagamento:
                        # Cabeçalho
                        modelo_forma_de_pagamento.append('\n--------------------------------\n')
                        

                        # Status
                        modelo_forma_de_pagamento.append(f"Status : {varAXI_STATUS.get()}\n")
                        
                        # Pix
                        if list_entry[0].get() != '0,00':
                            modelo_forma_de_pagamento.append(f"Pix : R$ {list_entry[0].get()}")
                        
                        # Dinheiro
                        if entry_troco.get() != '0,00' and list_entry[1].get() != '0,00':

                            if float(entry_troco.get().replace(',','.')) > float(list_entry[1].get().replace(',','.')):
                                modelo_forma_de_pagamento.append(f"Dinheiro receber : R$ {entry_troco.get()}")

                        else:
                            if list_entry[1].get() != '0,00':
                                modelo_forma_de_pagamento.append(f"Dinheiro receber : R$ {list_entry[1].get()}")
                        
                        # Cartão
                        if list_entry[2].get() != '0,00':
                            modelo_forma_de_pagamento.append(f"Cartão : R$ {list_entry[2].get()}")
                        
                        # Troco
                        if entry_troco.get() != '0,00' and list_entry[1].get() != '0,00':
                            if float(entry_troco.get().replace(',','.')) < float(list_entry[1].get().replace(',','.')):
                                messagebox.showerror('Não é possível!','Aconteceu uma coisa inesperada..\nDigite um troco maior!')
                                return
                            else:
                                cont = f"{float(entry_troco.get().replace(',','.')) - float(list_entry[1].get().replace(',','.')):.2f}"
                                modelo_forma_de_pagamento.append("Troco freguês : R$ {}".format(cont.replace('.',',')))
                    
                        if int(calculo_acrescimo) > 0:
                            modelo_forma_de_pagamento.append("Acréscimo: R$ {:.2f}".format(calculo_acrescimo).replace('.',','))
                        
                        # Recupera o valor da entrega
                        valor_entrega = float(str(entry_entrega.get()).replace(',','.')) if str(entry_entrega.get()) != '0,00' else 0.0

                        if valor_entrega >= 0.0:
                            if valor_entrega == 0.0:
                                # Se a taxa de entrega for zero, recalcula apenas com o valor atual
                                bt_total_limpo = float(entry_total_label.get().replace(',', '.'))
                                calculo = f'{bt_total_limpo:.2f}'
                                bt_total['text'] = f'R$ {calculo.replace(".", ",")}'
                            else:
                                entrega_taxa = valor_entrega
                                # Adiciona o valor da taxa de entrega no modelo de pagamento
                                modelo_forma_de_pagamento.append(f"Taxa Entrega: R$ {entrega_taxa:.2f}".replace('.', ','))

                                # Calcula o novo total somando a taxa de entrega
                                bt_total_limpo = float(entry_total_label.get().replace(',', '.'))
                                calculo = f'{entrega_taxa + bt_total_limpo:.2f}'
                                bt_total['text'] = f'R$ {calculo.replace(".", ",")}'
                     

                        modelo_forma_de_pagamento.append('\n')
                        modelo_forma_de_pagamento = '\n'.join(modelo_forma_de_pagamento)
                        
                        janela_pagamento.destroy()
                        
                        reiniciar_botoes()
                        preencher_texto()
                        
                except ValueError as e:
                    messagebox.showerror('Error','Aconteceu uma coisa inesperada..')
            else:
                messagebox.showinfo('Atenção','Seleciona um modo de pagamento!\nE tente denovo.')


        x,y,largura,altura = 339,566,294,63

        confirma_pagamento_Imagem = ImageTk.PhotoImage(Image.open(r"img_vendas\bt-confirma-pagamento.png"))

        botao_confirma_pagamento = Button(janela_pagamento,
                                image=confirma_pagamento_Imagem, borderwidth=0,
                                highlightthickness=0, bg=cores['Branca'],
                                    relief="ridge",
                                    activebackground=cores['Branca'],command=montar_variavel_pagamento)

        botao_confirma_pagamento.place(x=x, y=y, width=largura, height=altura+10)

        # Botao - Cancelar
        x,y,largura,altura = 117,571,159,53
        
        cancelar_pagamento_Imagem = ImageTk.PhotoImage(Image.open(r"img_vendas\bt-cancelar-pagamento.png"))

        botao_cancelar_pagamento = Button(janela_pagamento,
                                image=cancelar_pagamento_Imagem, borderwidth=0,
                                            highlightthickness=0, bg=cores['Branca'], 
                                    relief="ridge",
                                    activebackground=cores['Branca'],command=janela_pagamento.destroy)

        botao_cancelar_pagamento.place(x=x, y=y, width=largura, height=altura+10)

        rezetar_padrao()
        centralizar_janela(janela_pagamento,largura_pagamentos,altura_pagamentos,top=30)
        janela_pagamento.resizable(False,False)#bloquear seu crescimento ou reducao
        janela_pagamento.mainloop()

    pagamento_img = PhotoImage(file = r"img_vendas\bt-forma-pagamento.png")
    altura = 86
    largura = 162
    x,y = 63,546


    bt_forma_pagamento = Button(canvas_novo_pedido,image = pagamento_img, borderwidth = 0, activebackground="#938E94",highlightthickness = 0, 
                command = criarTelaPagamentos,relief = "ridge")
    bt_forma_pagamento.place(x=x, y=y, width=largura, height=altura)
    pagamento_img.image = pagamento_img

    # ---------------------------------------------------------------------------------------------
    # Defina o ícone da janela_novo_pedido
    # icon_image = tk.PhotoImage(file=r"img_vendas\icone_logo.png")
    # janela_novo_pedido.iconphoto(False, icon_image)

    # janela_novo_pedido.mainloop()
    root.wait_window(janela_novo_pedido)
    

####---------------- final funcao novo pedido

x,y,w,h = posicionar_OBJ_tela(valor_x = 1024 + x_dinamica,
                              valor_y = 216 + espaço + y_dinamico*0.22,                              
                              w = 241 + 5,
                              h = 112 + 8)

novo_pedido_img = PhotoImage(file=r"img_inicio\bt_novo_pedido.png")
bt_novo_pedido = Button(image=novo_pedido_img, borderwidth=0,
                      activebackground=cores['fundo_cinza'], highlightthickness=0, 
                      relief="ridge",command=funcao_novo_pedido)

novo_pedido_criar = canvas.create_window(x, y, width=w, anchor="nw", height=h, window=bt_novo_pedido)

# Relatorio ---------------------------------------------------------------------------------------------

def funcao_relatorio():
    global colunas_relatorio,valores,entry_data,produto_lista,colunas_situacao,lista_relatorio_bd,conexao,cursor

    
    janela_relatorio = tk.Toplevel(root)
    janela_relatorio.grab_set()# precisa ser chamado apos a criacao
    janela_relatorio.transient(root)  # Manter janela_relatorio no topo
    janela_relatorio.focus_force()  # Força o foco na janela

    relatorio_largura = 900
    relatorio_altura = 650
    janela_relatorio.title("Interface de Relátorio")
    janela_relatorio.columnconfigure([0, 1], weight=1)
    centralizar_janela(janela_relatorio, relatorio_largura, relatorio_altura,top=30)
    janela_relatorio.config(bg=cores['Branca'])
    janela_relatorio.resizable(False, False)

    frame_relatorio = tk.Frame(janela_relatorio, bg=cores["Roxo Escuro"])
    frame_relatorio.pack(side="left", fill='both', expand=True)

    canvas_relatorio = tk.Canvas(
        frame_relatorio,
        bg=cores['Roxo Escuro'],
        height=relatorio_altura,
        width=relatorio_largura,
        bd=0,
        highlightthickness=0,
        relief="ridge")
    canvas_relatorio.pack(fill=tk.BOTH, expand=True)

    segundoImagem = ImageTk.PhotoImage(Image.open(r"img_relatorio\bg_relatorio.png"))
    background = canvas_relatorio.create_image(relatorio_largura / 2, relatorio_altura / 2, image=segundoImagem)

    # Fechar conecção antes do ultimo commit
    try:
        conexao.rollback()
    except:
        pass

    # Busca pedidos na data
    def conexao_inicial():
        global lista_relatorio_bd,numero_de_pedidos_feito
        cursor.execute("SELECT Relatorio FROM Pedidos WHERE Lançamento = ? AND  Data = ?",('True',entry_data.get()))
        lista_relatorio_bd = cursor.fetchall()
        # Trava caso nao exista pedidos
        numero_de_pedidos_feito = treeview_pedidos.get_children()

        if len(numero_de_pedidos_feito) == 0:
            janela_relatorio.destroy()
            messagebox.showerror('Nada encontrado','Nenhum pedido foi encontrado nesta data!\nTente vender ou use uma data que tenha registro.')
            return
    conexao_inicial()
   
   # Data -----------------------------------------------------------------------------------------------------
    x,y,largura,altura = 777,38,100,19
    label_data_relatorio = tk.Label(canvas_relatorio,text = f'{entry_data.get()}',
                            font='Arial 14',bg='white',justify='left')
    exibir_data = canvas_relatorio.create_window(x, y, anchor=tk.NW,width=largura,
                                       height=altura,window=label_data_relatorio)


    # Status -----------------------------------------------------------------------------------------------------
    

    texto_status = ''

    x,y,largura,altura = 0,96,relatorio_largura,19
    label_status = tk.Label(canvas_relatorio,text = texto_status,
                            font='Arial 16',bg='white',justify='center')
    exibir_status = canvas_relatorio.create_window(x, y, anchor=tk.NW,width=largura,
                                        height=altura,window=label_status)
    def status_label():   
        if len(numero_de_pedidos_feito) == len(lista_relatorio_bd):
            
            label_status.config(fg='green')
            label_status['text'] = 'Status - Está tudo certo por aqui!'

        else:
            
            label_status.config(fg='red')
            label_status['text'] = 'Status - Existe pedido sem lançamento!'
    status_label() 
    # 1 Resumo das vendas ----------------------------------------------------------------------------------------
   

    # FATURAMENTO
    x,y,largura,altura = 216,173,104,30
    label_faturamento = tk.Label(canvas_relatorio,text = '',
                            font='Arial 14',bg='#F1E6F6',justify='center')
    exibir_faturamento = canvas_relatorio.create_window(x, y, anchor=tk.NW,width=largura,
                                       height=altura,window=label_faturamento)
    
    # TOTAL PEDIDOS
    x,y,largura,altura = 457,173,104,30
    label_total_pedidos = tk.Label(canvas_relatorio,text = '',
                            font='Arial 14',bg='#F1E6F6',justify='center')
    exibir_t_pedidos = canvas_relatorio.create_window(x, y, anchor=tk.NW,width=largura,
                                       height=altura,window=label_total_pedidos)
    # VENDAS MEDIA
    x,y,largura,altura = 747,173,104,30
    label_media_vendas = tk.Label(canvas_relatorio,text = '',
                            font='Arial 14',bg='#F1E6F6',justify='center')
    exibir_media = canvas_relatorio.create_window(x, y, anchor=tk.NW,width=largura,
                                       height=altura,window=label_media_vendas)



    # 2 Desempenho do produto ----------------------------------------------------------------------------------------

    
    colunas_relatorio = ['Produtos Vendidos','Unidades','Faturamento']
    valores = []
    largura_colunas_treeview = [260,120,120]# Tamanho das colunas_relatorio do treeview

    altura,largura,x,y = 162, 524, 43, 281

    treeview_relatorio = ttk.Treeview(canvas_relatorio)
    exibir_relatorio = canvas_relatorio.create_window(x, y, anchor=tk.NW, width=largura,
                                       height=altura, window=treeview_relatorio)
    # Adicionar barras de rolagem
    scrollbar_y = tk.Scrollbar(treeview_relatorio, orient=tk.VERTICAL)

    # Criar o Treeview e configurá-lo com barras de rolagem
    treeview_relatorio = ttk.Treeview(treeview_relatorio, yscrollcommand=scrollbar_y.set)
    scrollbar_y.config(command=treeview_relatorio.yview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

    treeview_relatorio.pack(fill=tk.BOTH, expand=True)
    
       
    def listar_Desempenho_produtos():
        global colunas_relatorio,valores,produto_lista,vendas_lista
        vendas_lista = []
        produto_lista = []
        # Adicionando itens a treeview de exibir -----------------------------------------------
        style = ttk.Style()
        style.configure("Custom.Treeview", font=("Arial", 12),
                        background='white',foreground="black",fieldbackground="red")
        style.configure("Treeview.Heading", font = "Arial 10 bold")

        treeview_relatorio.config(style='Custom.Treeview')
        # treeview_relatorio.config(style=style.theme_use('default'))
        #Executa um comando SQL para selecionar todos os valores da tabela de Produtos
        cursor.execute("Select * From Estoque")

        #Limpa os valores da treeview_relatorio
        for i in treeview_relatorio.get_children():        
            treeview_relatorio.delete(i)
        
        # modificar o cabeçario dinamico
        treeview_relatorio.config(columns=(colunas_relatorio),show="headings")

        # cor linhas treeview
        treeview_relatorio.tag_configure('oddrow', background='white')
        treeview_relatorio.tag_configure('evenrow', background=cores['Linha_tre'])

        for i,coluna in enumerate(colunas_relatorio):
            treeview_relatorio.heading(coluna, text=coluna)
            treeview_relatorio.column(coluna,width=largura_colunas_treeview[i],anchor= CENTER)

        # Adiciona cor as linhas do Treeview
        # E listar ela na ordem do maior para o menor
        for index,valor in enumerate(sorted(aprensentar_dicionario_desempenho(lista_relatorio_bd), key=lambda x: x[2], reverse=True)):
            # Pegando 
            produto_lista.append(valor[0])
            vendas_lista.append(valor[2])
            

            if index % 2 == 0:# ocorrencia de repeticao 2 em 2 ou 3 em 3
                treeview_relatorio.insert("", "end", values=(valor[0], valor[1], valor[2]), tags=('evenrow',))
            else:
                treeview_relatorio.insert("", "end", values=(valor[0], valor[1], valor[2]), tags=('oddrow',))
        
        
       
    listar_Desempenho_produtos()

    
    def atualizar_faturamento():
        global soma_faturamento_bruto,faturamento_axi,vendas_lista
        # Atualizar Faturamento
        soma_faturamento_bruto = sum(vendas_lista)
        faturamento_axi = f'{soma_faturamento_bruto:_.2f}'.replace('.',',').replace('_','.')
        label_faturamento['text'] = f'R$ {faturamento_axi}'

        # Atualizar Media Venda
                
        array = np.array(vendas_lista)
        if len(array) > 0:
            tabela_axi = f'{array.mean():_.2f}'.replace('.',',').replace('_','.')
            label_media_vendas['text'] = f'R$ {tabela_axi}'
        else:
            label_media_vendas['text'] = f'R$ 0,00'

        # Atualizar 
        label_total_pedidos['text'] = len(lista_relatorio_bd)
        
    atualizar_faturamento()
    # 3 Situacao do estoque ----------------------------------------------------------------------------------------
    # Função para aplicar cores às linhas com base no valor do estoque

    


    # Criando o Treeview

    largura_treeview_situacao = [150,70]# Tamanho das colunas_relatorio do treeview
    colunas_situacao = ['Produto','Estoque']
    altura,largura,x,y = 162, 280, 589, 281

    treeview_situacao = ttk.Treeview(canvas_relatorio)
    exibir_relatorio = canvas_relatorio.create_window(x, y, anchor=tk.NW, width=largura,
                                       height=altura, window=treeview_situacao)
    # Adicionar barras de rolagem
    scrollbar_y_situacao = tk.Scrollbar(treeview_situacao, orient=tk.VERTICAL)

    # Criar o Treeview e configurá-lo com barras de rolagem
    treeview_situacao = ttk.Treeview(treeview_situacao,yscrollcommand=scrollbar_y_situacao.set)
    scrollbar_y_situacao.config(command=treeview_situacao.yview)
    scrollbar_y_situacao.pack(side=tk.RIGHT, fill=tk.Y)

    treeview_situacao.pack(fill=tk.BOTH, expand=True)

    def aplicar_cores(treeview):
        for item in treeview.get_children():
            # Obtém o valor da célula "Estoque" e remove o símbolo de porcentagem
            estoque = int(treeview.item(item, 'values')[1].replace('%', ''))
            
            # Define a cor com base nos intervalos de estoque
            if 0 <= estoque <= 25:
                treeview.item(item, tags=('vermelho',))
            elif 26 <= estoque <= 40:
                treeview.item(item, tags=('amarelo_claro',))
            elif 41 <= estoque <= 50:
                treeview.item(item, tags=('amarelo',))
            elif 51 <= estoque <= 65:
                treeview.item(item, tags=('verde',))
            elif 66 <= estoque <= 85:
                treeview.item(item, tags=('azul_claro',))
            else:  # 86% a 100%
                treeview.item(item, tags=('azul',))

    
    def lista_situacao():
        global colunas_situacao,valores,produto_lista
 
        # Adicionando itens a treeview de exibir -----------------------------------------------
        style = ttk.Style()
        style.configure("Custom.Treeview", font=("Arial", 12),
                        background='white',fieldbackground="red")
        style.configure("Treeview.Heading", font = "Arial 12 bold")

        treeview_situacao.config(style='Custom.Treeview')
        

        #Limpa os valores da treeview_situacao
        for i in treeview_situacao.get_children():        
            treeview_situacao.delete(i)
        
        # modificar o cabeçario dinamico
        treeview_situacao.config(columns=(colunas_situacao),show="headings")

        # Definindo as cores das tags
        treeview_situacao.tag_configure('vermelho', background='#FF4A4A')
        treeview_situacao.tag_configure('amarelo_claro', background='#EAEA79')
        treeview_situacao.tag_configure('amarelo', background='#FFFF44')
        treeview_situacao.tag_configure('verde', background='#67D17F')
        treeview_situacao.tag_configure('azul_claro', background='#7CADFF')
        treeview_situacao.tag_configure('azul', background='#3F97DC')

        for i,coluna in enumerate(colunas_situacao):
            treeview_situacao.heading(coluna, text=coluna)
            treeview_situacao.column(coluna,width=largura_treeview_situacao[i],anchor= CENTER)

          
        # Construa dinamicamente o número correto de placeholders "?" para a consulta SQL
        parametro = ', '.join(['?'] * len(produto_lista))

        # Crie um fragmento SQL para a cláusula ORDER BY usando CASE para manter a ordem dos produtos
        preserva_ordem = ' '.join([f"WHEN ? THEN {i}" for i, _ in enumerate(produto_lista)])

        # Consulta SQL usando IN e CASE para garantir a ordem correta
        sql_query = f"""
        SELECT Descrição, Quantidade, Base 
        FROM Estoque 
        WHERE Descrição IN ({parametro})
        ORDER BY CASE Descrição {preserva_ordem} END
        """

        # # Combine produto_lista com ela mesma para duplicar a lista de parâmetros para os placeholders e o CASE
        params = produto_lista + produto_lista

        # Executa a consulta passando a lista de produtos como parâmetros
        try:
            
            cursor.execute(sql_query, params)
        except:
            return# finalizar caso de alguma coisa de errado ou nao foi lançado nada

        # Processa os resultados
        if label_status['text'] == 'Status - Está tudo certo por aqui!':
            for produto_bd, quantidade, base in cursor.fetchall():
                if quantidade > 0 and base > 0:
                    situacao_percent = f'{int((quantidade / base) * 100)}%'
                    treeview_situacao.insert("", "end", values=(produto_bd, situacao_percent))


            aplicar_cores(treeview_situacao)
       
    lista_situacao()




    # 4 Comparativos ----------------------------------------------------------------------------------------
   
    # Percentual de Vendas
    x,y,largura,altura = 214,499,655,20
    label_percentual = tk.Label(canvas_relatorio,text = '',
                            font='Arial 14',bg='white',anchor='w')
    exibir_percentual = canvas_relatorio.create_window(x, y, anchor=tk.NW,width=largura,
                                       height=altura,window=label_percentual)

    # Número de Pedidos:
    x,y,largura,altura = 214,526,655,20
    label_numero_pedidos = tk.Label(canvas_relatorio,text = '',
                            font='Arial 14',bg='white',anchor='w')
    exibir_numero_Pedidos = canvas_relatorio.create_window(x, y, anchor=tk.NW,width=largura,
                                       height=altura,window=label_numero_pedidos)
    
   

    def valores_anterior():
            
            data_antiga = ''.join(str(entry_data.get()).split('/'))

            dia = int(data_antiga[:2]) 
            mes = int(data_antiga[2:4]) 
            ano = int(data_antiga[4:]) 
            busca_incrementada = 1

            data_atual = datetime(ano, mes, dia) 
            
            # Subtrair o intervalo da data
            while True:
                intervalo = timedelta(days=busca_incrementada)
                nova_data = data_atual - intervalo
                
                cursor.execute("SELECT Relatorio FROM Pedidos WHERE Lançamento = ? AND  Data = ?",('True',nova_data.strftime('%d/%m/%Y')))
                valores_antes_recuperado = cursor.fetchall()
                if len(valores_antes_recuperado) != 0 or busca_incrementada >= 10:
                    try:
                        fatu_antes = sum([valor[2] for valor in aprensentar_dicionario_desempenho(valores_antes_recuperado)])
                        quanti_antes = len(valores_antes_recuperado)
                        return tuple((fatu_antes,quanti_antes))
                    except:
                        return tuple((0,0))
                busca_incrementada += 1
    

    def comparativo_dia_anteriror():
        global soma_faturamento_bruto
        dia_anterior_var = valores_anterior()

        # Dia atual
        fat_valor = float(f'{soma_faturamento_bruto:.2f}')
        num_pedidos = len(lista_relatorio_bd)

        # Dia anterior
        fat_anterior = float(dia_anterior_var[0])
        num_pedidos_anterior = dia_anterior_var[1]

        if fat_valor:
            if fat_valor > fat_anterior:
                
                percente_faturamento = int(((fat_valor - fat_anterior)/fat_valor)* 100)
                lista_superamos = [
                    f'Ótimo, superamos a receita de ontem com +{percente_faturamento}%! Bom trabalho!',
                    f'Uhuuul! Faturamos hoje heim.. com +{percente_faturamento}%! Estamos a todo vapor.',
                    f'Parabéns! O esforço valeu apena, vendemos +{percente_faturamento}% a mais.'
                    
                ]
                label_percentual['text'] = np.random.choice(lista_superamos)
                

            else:

                lista_nao_superamos = [
                    'Hoje não superamos os ganhos de ontem, mas nada de desânimo!',
                    'Faltou um pouco para superar ontem mas firme na luta.',
                    ]
                label_percentual['text'] = np.random.choice(lista_nao_superamos)

        if num_pedidos:
            if num_pedidos > num_pedidos_anterior:
                quantidade_pedidos = int(num_pedidos - num_pedidos_anterior)

                lista_superamos_pedidos = [
                    f'Mandamos bem hoje! Superamos ontem com {quantidade_pedidos} pedidos a mais.',
                    f'Uau, número de pedidos subindo! Conseguimos {quantidade_pedidos} mais do que ontem.',
                    f'Mais pedidos, mais sucesso! Hoje superamos o dia anterior com {quantidade_pedidos} pedidos.'
                ]
                label_numero_pedidos['text'] = np.random.choice(lista_superamos_pedidos)
            

            else:
                if num_pedidos != num_pedidos_anterior:
                    quantidade_pedidos = int(num_pedidos_anterior - num_pedidos)

                    lista_nao_superamos_pedidos = [
                        f'Vixi, por {quantidade_pedidos} pedidos não superamos ontem... Foi por pouco!',
                        f'Hoje o número de pedidos foi menor que ontem em {quantidade_pedidos} pedidos.',
                        f'Faltaram {quantidade_pedidos} pedidos para bater ontem.',
                        f'Por pouco não superamos ontem! Por {quantidade_pedidos} pedidos.'
                    ]
                    label_numero_pedidos['text'] = np.random.choice(lista_nao_superamos_pedidos)
                else:
                    lista_nao_superamos_pedidos_iguais = [
                            f'Vixi, ficamos com o mesmo numero de vendas que ontem!',
                            f'Hoje o número de pedidos foi igual os de ontem.',
                            f'Por pouco não superamos ontem! Hoje ficou no empate.'
                        ]
                    label_numero_pedidos['text'] = np.random.choice(lista_nao_superamos_pedidos_iguais)

    comparativo_dia_anteriror()    

    # Botoes ----------------------------------------------------------------------------------------
    
        # Cancelar ------------------------------------
    cancelar_img = PhotoImage(file=r"img_relatorio\bt_cancelar.png")
    x,y,largura,altura = 35,577,135,50
    botao_cancelar = tk.Button(canvas_relatorio, image=cancelar_img, activebackground='#FFFFFF', 
                               highlightthickness=0,borderwidth=0,command=janela_relatorio.destroy)
    canvas_relatorio.create_window(x, y, anchor=tk.NW,width=largura,
                                       height=altura,window=botao_cancelar)
    
        # Baixar ------------------------------------
    def baixar_relatorio():
        global enviar_texto_para_impressora_especifica
        if label_status['text'] != 'Status - Está tudo certo por aqui!':
            if messagebox.askyesno('Alerta','Deseja imprimir o relatório desatualizado?') == False:
                return
        # Exemplo de dados da tabela
        data = {
            'Produtos Vendido': produto_lista,
            'Faturamento': vendas_lista
        }

        df = pd.DataFrame(data)

        # Converte o DataFrame para uma string formatada
        df_string = df.to_string(index=False)

        # Função para exibir o DataFrame no Text
        def mostrar_tabela():
            text_widget.insert(tk.END, "    RELATORIO DE DESEMPENHO     \n\n")
            text_widget.insert(tk.END, f"Vendas do dia:       {entry_data.get()}\n")
            text_widget.insert(tk.END, "--------------------------------\n\n")
            text_widget.insert(tk.END, ' ' + df_string)
            
            text_widget.insert(tk.END, "\n\n\n--------------------------------\n")
            text_widget.insert(tk.END, "Total de Pedidos:{:>14}\n".format(len(lista_relatorio_bd)))
            text_widget.insert(tk.END, "Faturamento     :{:>14}\n\n".format(f'R$ {faturamento_axi}'))

            return text_widget.get('1.0',tk.END)

        # Text axiliar para criar o relatorio
        text_widget = tk.Text(wrap=tk.NONE,width=32,height=20)
        
        enviar_texto_para_impressora_especifica(mostrar_tabela(),janela_relatorio)

    
    baixar_img = PhotoImage(file=r"img_relatorio\bt_baixar.png")
    x,y,largura,altura = 184,577,135,50
    botao_baixar = tk.Button(canvas_relatorio,highlightthickness=0,borderwidth=0,image=baixar_img,
                             activebackground='#FFFFFF',command=baixar_relatorio)
    canvas_relatorio.create_window(x, y, anchor=tk.NW,width=largura,
                                       height=altura,window=botao_baixar)
    
        # Atualizar BD ------------------------------------
    
    def atualizar_status():

        if label_status['text'] == 'Status - Está tudo certo por aqui!':
            messagebox.showinfo('Tudo Atualizado','Não há pedidos pendentes.')
            return 
        label_status['text'] = 'Atualizando o estoque...'
       
        
        
        # Espera 2 segundos (2000 milissegundos) antes de executar acao2
        root.after(2000, atualizar_estoque_bd)

    def atualizar_estoque_bd():
        '''Funcao que calcula as vendas de um item pedente e retira do banco de dados. 
        Ele nao verifica se tem unidades para retirar fica a cardo da funcao de pedidos verificar isso antes de fazer o pedido.'''
       
          
        cursor.execute(f"UPDATE Pedidos SET Lançamento = ? WHERE Data = ?",('True',entry_data.get()))
        label_status['text'] = 'Status - Está tudo certo por aqui!'
        label_status.config(fg='green')
        
        
        conexao_inicial()
        status_label()
        listar_Desempenho_produtos()
        atualizar_faturamento()
        lista_situacao()
        comparativo_dia_anteriror()


    
    atualizar_bd_img = PhotoImage(file=r"img_relatorio\bt_atualizar.png")
    x,y,largura,altura = 334,577,214,50
    botao_atualizar_bd = tk.Button(canvas_relatorio, highlightthickness=0,borderwidth=0,image=atualizar_bd_img,activebackground='#FFFFFF', command= atualizar_status)
    canvas_relatorio.create_window(x, y, anchor=tk.NW,width=largura,
                                       height=altura,window=botao_atualizar_bd)
    
        # Fechar Caixa ------------------------------------
    def fechar_caixa():
        global soma_faturamento_bruto
        if label_status['text'] != 'Status - Está tudo certo por aqui!':
            if messagebox.askyesno('Atualiza seu relatório','Posso atualizar para voçê?'):
                atualizar_status()
            return
            
        if messagebox.askokcancel("Fechar Caixa", "Deseja fechar seu caixa?"):
            conexao.commit()# salvar as alteracoes no banco de dados
            janela_relatorio.destroy()
            fat_valor = f'{soma_faturamento_bruto:.2f}'
            if float(fat_valor) < 200.00:
                
                lista_ruim_dia = [
                                'Hoje hoje faturamos pouco, poxaaa..\nDeixa comigo. Amanhã vou acelerar minhas capacidades + 53%.\n\nVamos faturar na casa dos 4 diritos!\n',
                                'Hoje o saldo ficou meio tímido...\nMas relaxa! Amanhã vou virar super-sistema, capa e tudo.\n\nNos vemos na casa dos milhões!\n',
                                'Hmm... não foi o melhor dia, né?\nMas já tenho a solução: café extra forte amanhã e foco total!\n\nVamos conquistar o mundo (ou pelo menos o mercado)!\n',
                                'Hoje foi devagar, mas amanhã? Ah, amanhã vamos voar!\nVou até dormir mais cedo pra sonhar com estratégias milionárias!\n\nBora lucrar como nunca!\n',
                                'Parece que a sorte foi tirar um cochilo hoje...\nMas fica tranquilo! Amanhã vou fazer ela acordar de vez.',
                                'O faturamento tirou folga hoje...\nMas já avisei que amanhã não tem desculpa!\n\nAmanhã é dia de fazer história e bater recorde!\n'
                                ]
                
                messagebox.showinfo('Sucesso ao fechar!',np.random.choice(lista_ruim_dia))
                return # finalizar a funcao
            
            elif 200.00 <= float(fat_valor) < 1000.00:
                lista_bom_dia = [
                                'Ótimo trabalho! Todo esforço no final sempre vale a pena.\nAmanhã, vamos continuar nessa pegada. Foco e planejamento são a chave!\n',
                                'Hoje foi incrível, mas amanhã? Amanhã vai ser épico!\nVamos manter o ritmo e dobrar o resultado!\n',
                                'Missão cumprida por hoje! Cada centavo é uma vitória.\nAmanhã a gente repete o sucesso... mas com mais zeros no saldo!\n',
                                'Parabéns! Hoje foi um passo para o topo.\nAmanhã, a gente voa ainda mais alto – foguete não tem ré!\n',
                                'Excelente dia! A cada venda, o sonho tá mais perto.\nAmanhã? A meta é triplicar e fazer história!\n'
                                ]
                messagebox.showinfo('Sucesso ao fechar!',np.random.choice(lista_bom_dia))
                return # finalizar a funcao

            elif  float(fat_valor) >= 1000.00:
                lista_otimo_dia = [
                                    'Nossa, hoje eu cansei, mas estamos ricos kkk! Te falei que se continuasse na pegada iria dar bom.\nAmanhã, vou até pedir folga. Que loucura!\n\nParabéns!\n',
                                    'Alerta de sucesso: batemos meta e ainda sobrou energia! Vamos pedir um aumento? Amanhã a gente faz história de novo!\n\nUhuul!\n',
                                    'Hoje foi incrível! Se a gente continuar assim, vamos ter que abrir outra conta só para caber todo o dinheiro kkk!\n\nVamo que vamo!\n',
                                    'Vendemos tanto que o sistema quase derreteu! Amanhã vamos superar ainda mais. E olha, vou sonhar com dinheiro hoje kkk!\n\nRumo ao topo!\n',
                                    'Amanhã vou ter que contratar um segurança pra proteger o faturamento de hoje kkk! O céu não é mais o limite, vamos além!\n\nParabéns!\n',
                                    'Hoje foi épico! O saldo da conta já tá sorrindo pra gente. Amanhã é mais um capítulo dessa história milionária!\n\nTamo junto!\n',
                                    'Se eu contar o que a gente faturou hoje, ninguém acredita kkk! Vamos celebrar hoje e amanhã repetir o feito.\n\nBora lucrar mais!\n',
                                    'Ufa, mal posso contar os zeros que entraram hoje! Vou até comemorar, mas amanhã tamo de volta pra continuar essa maratona de sucesso!\n\nParabéns, campeão!\n',
                                    'Hoje foi dia de quebrar recorde, vender tudo e ainda sobrar estoque de felicidade kkk! Amanhã vamos fazer mais história.\n\nVoa alto!\n',
                                    'Tô até pensando em pedir férias depois de um dia desses, porque o sucesso foi tão grande que vou precisar descansar! Amanhã a gente dobra esse resultado!\n\nVem mais lucro!\n'
                                  ]

                # Seleciona uma mensagem aleatória e exibe no messagebox
                messagebox.showinfo('Sucesso ao fechar!', np.random.choice(lista_otimo_dia))
                return # finalizar a funcao

    fechar_caixa_img = PhotoImage(file=r"img_relatorio\bt_fechar_caixa.png")
    x,y,largura,altura = 651,566,229,72
    botao_fechar_caixa = tk.Button(canvas_relatorio,highlightthickness=0,borderwidth=0,
                                   image=fechar_caixa_img,activebackground='#FFFFFF',command=fechar_caixa)
    canvas_relatorio.create_window(x, y, anchor=tk.NW,width=largura,
                                       height=altura,window=botao_fechar_caixa)


    root.wait_window(janela_relatorio)
    
x,y,w,h = posicionar_OBJ_tela(valor_x = 1024 + x_dinamica,
                              valor_y = 351 + espaço + y_dinamico*0.45,                              
                              w = 241 + 5,
                              h = 113 + 8)

relatorio_img = PhotoImage(file=r"img_inicio\bt_relatorio.png")
bt_relatorio = Button(image=relatorio_img, borderwidth=0,
                      activebackground=cores['fundo_cinza'], background="#280D2B", highlightthickness=0, 
                      command=funcao_relatorio,relief="ridge")

relatorio_criar = canvas.create_window(x, y, width=w,anchor="nw", height=h, window=bt_relatorio)



# Analise --------------------------------------------------------------------------------------------------

x,y,w,h = posicionar_OBJ_tela(valor_x = 1024 + x_dinamica,
                              valor_y = 486 + espaço + y_dinamico*0.67,                             
                              w = 241 + 5,
                              h = 112 + 8)

analise_img = PhotoImage(file=r"img_inicio\bt_analise.png")
def manuntencao_analise():
    messagebox.showinfo('Manutenção','Calma, suas análises no momento não estão disponíveis.')
analise_bt = Button(image=analise_img, borderwidth=0, background="#280D2B", activebackground=cores['fundo_cinza'], highlightthickness=0, 
                        relief="ridge",command=manuntencao_analise)
analise_criar = canvas.create_window(x, y, width=w, anchor="nw",height=h, window=analise_bt)

#------------------------xxxxxx Estoque xxxxxx---------------------------------------------------------------------------------------------------


def funcao_estoque():
    global colunasDinamicas,salva_posicao
   
    def limitar_texto(event, entry, max_length=22):
        current_text = entry.get()
        if len(current_text) > max_length:
            entry.delete(max_length, tk.END)

    def bloquear_texto(event):
        return "break"

    janela_estoque = tk.Toplevel(root)
    janela_estoque.grab_set()# precisa ser chamado apos a criacao
    janela_estoque.transient(root)  # Manter janela_estoque no topo
    janela_estoque.focus_force()  # Força o foco na janela

    janela_estoque.title("Interface de Estoque")
    janela_estoque.columnconfigure([0, 1], weight=1)
    centralizar_janela(janela_estoque, 1120, 650,top=30)
    janela_estoque.config(bg=cores['Branca'])
    janela_estoque.resizable(False, False)

    
    estoque_largura = 1120
    estoque_altura = 650
    id_Protegidos = [1, 3, 4, 14, 15, 16, 17, 18, 19, 20, 21]  # ids
    # Frame direito
    frame_direito = tk.Frame(janela_estoque, bg=cores["Roxo Escuro"])
    frame_direito.pack(side="left", fill='both', expand=True)

    canvas_estoque = tk.Canvas(
        frame_direito,
        bg=cores['Roxo Escuro'],
        height=estoque_altura,
        width=estoque_largura,
        bd=0,
        highlightthickness=0,
        relief="ridge")
    canvas_estoque.pack(fill=tk.BOTH, expand=True)

    segundoImagem = ImageTk.PhotoImage(Image.open(r"img_estoque\fundo_estoque.png"))
    background = canvas_estoque.create_image(estoque_largura / 2, estoque_altura / 2, image=segundoImagem)

    def filtro_dos_itens(entry_produto):
    
        #if - se
        #Verifica se os campos estão vazio
        if not entry_produto.get():

            #Se ambos os campos estiverem vazios, não faz nada
            listar_Dados_estoque()       
            return
        
        sql = f"SELECT * FROM Estoque"
        
        params = []
        
    
        # Verifica se ao codigo esta correto
        comando = f'SELECT * FROM Estoque WHERE Codigo LIKE ?'
        cursor.execute(comando,(entry_produto.get() + '%'))
        codigo = cursor.fetchall()
        
        if codigo:
            if int(entry_produto.get()).is_integer() == True:
                sql += " WHERE Codigo LIKE ?" 
                
                """
                Parâmetro de consulta dinamicamente com base 
                no texto digitado esse curinga % considera qualquer numero de caracteres 
                antes do padrao de corespondência.
                """
                params.append('%' + entry_produto.get() + '%')

        else:
            # Verifica se a categoria esta correto
            digitando_maiusculo = str(entry_produto.get()).upper()
            comando = f'SELECT * FROM Estoque WHERE Categoria LIKE ?'
            cursor.execute(comando,('%' + digitando_maiusculo + '%'))
            categoria = cursor.fetchall()

            if categoria:
            
                sql += " WHERE Categoria LIKE ?" 
                
                """
                Parâmetro de consulta dinamicamente com base 
                no texto digitado esse curinga % considera qualquer numero de caracteres 
                antes do padrao de corespondência.
                """
                params.append('%' + digitando_maiusculo + '%')

            
            else:
                # Verifica se a descricao esta correto
                comando = f'SELECT * FROM Estoque WHERE Descrição LIKE ?'
                cursor.execute(comando,('%' + entry_produto.get() + '%'))
                descricao = cursor.fetchall()

                if descricao:
                    sql += " WHERE Descrição LIKE ?" 
                    params.append('%' + entry_produto.get() + '%')
                else:
                    sql += " WHERE Natureza LIKE ?" 
                    params.append('%' + entry_produto.get() + '%')
                    
        # passe os valores para o filtro LIKE do banco de dados
        
        cursor.execute(sql, tuple(params))
        produtos = cursor.fetchall()
            
        #Limpa os dados da treeview
        limparTreeview(treeview_estoque)
            
        #Preenche treeview com os dados filtrados
        for index,valor in enumerate(produtos):

            if index % 2 == 0:# ocorrencia de repeticao 2 em 2 ou 3 em 3
                treeview_estoque.insert("", "end", values=(valor[0], valor[1], valor[2], valor[3], valor[4], valor[6]), tags=('evenrow',))
            else:
                treeview_estoque.insert("", "end", values=(valor[0], valor[1], valor[2], valor[3], valor[4], valor[6]), tags=('oddrow',))
    
    altura = 32
    largura = 409
    x, y = 670, 62

    padding = 5
    text_x = x + padding
    text_y = y + padding
    text_largura = largura - 2 * padding
    text_altura = altura - 2 * padding

    produto_img = PhotoImage(file=r"img_estoque\entry_produto.png")
    canvas_estoque.create_image(x, y, anchor="nw",image=produto_img )

    entry_produto = tk.Entry(janela_estoque, bd=0, bg=cores['Branca'],font="Arial 16", highlightthickness=0)
    canvas_estoque.create_window(text_x, text_y, anchor="nw", width=text_largura, height=text_altura, window=entry_produto)


    #Eventos de cada sequencia de letras filtra minha lista de profutos na Treeview
    entry_produto.bind("<KeyRelease>",lambda e: filtro_dos_itens(entry_produto))



    # ANALISE ESTOQUE ----------------------------------------------------
    x,y,largura,altura = 43,196,209,39
    label_unidades_estoque = tk.Label(canvas_estoque,text = '',
                            font='Arial 20 bold',bg='#280D2B',fg='white',justify='center')
    exibir_unidades = canvas_estoque.create_window(x, y, anchor=tk.NW,width=largura,
                                       height=altura,window=label_unidades_estoque)
    
    x,y,largura,altura = 289,196,209,39
    label_restante_estoque = tk.Label(canvas_estoque,text = '',
                            font='Arial 20 bold',bg='#280D2B',fg='white',justify='center')
    exibir_restante = canvas_estoque.create_window(x, y, anchor=tk.NW,width=largura,
                                       height=altura,window=label_restante_estoque)
    
    x,y,largura,altura = 532,196,209,39
    label_valor_estoque = tk.Label(canvas_estoque,text = '',
                            font='Arial 20 bold',bg='#280D2B',fg='white',justify='center')
    exibir_valor = canvas_estoque.create_window(x, y, anchor=tk.NW,width=largura,
                                       height=altura,window=label_valor_estoque)
    

    # EXIBIR -----------------------------------------------------

    cursor.execute("SELECT * FROM Estoque")
    colunasDinamicas = [coluna[0] for coluna in cursor.description if coluna[0] not in ['Base','Medida']]
    largura_colunas_treeview = [81,150,300,150,100,100]# Tamanho das colunasDinamicas do treeview

    altura,largura,x,y = 336, 1090, 15, 296

    treeview_estoque = ttk.Treeview(canvas_estoque)
    exibir_estoque = canvas_estoque.create_window(x, y, anchor=tk.NW, width=largura,
                                       height=altura, window=treeview_estoque)
    # Adicionar barras de rolagem
    scrollbar_y = tk.Scrollbar(treeview_estoque, orient=tk.VERTICAL)

    # Criar o Treeview e configurá-lo com barras de rolagem
    treeview_estoque = ttk.Treeview(treeview_estoque, yscrollcommand=scrollbar_y.set)
    scrollbar_y.config(command=treeview_estoque.yview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

    treeview_estoque.pack(fill=tk.BOTH, expand=True)

    def limparTreeview(treeview):
        for i in treeview.get_children():        
            treeview.delete(i)


    def criar_tabelaDinamica(valores):
        global df_analise_estoque

        def reduzirBalde(balde):
            '''converter mililitros para litros'''
            mililitros = balde * 1
            balde_Atualizado = mililitros / 1000
            return balde_Atualizado
        
        # try:
        coluna_analise_estoque = ['Codigo', 'Categoria', 'Descrição', 'Natureza', 'Quantidade', 'Base','Preço','Medida']
       
        # from_records para criar com tuplas o data
        dataFrameDinamico = pd.DataFrame.from_records(valores,columns=[coluna_analise_estoque])
        dataFrameDinamico.to_csv('dataFrameDinamico.csv',index=False)
        df_analise_estoque = pd.read_csv('dataFrameDinamico.csv',dtype={'Quantidade': float,'Base' : float})
        df_analise_estoque = df_analise_estoque[['Codigo','Descrição','Quantidade','Base','Preço']]

        for i in [1,3,4]:
            local = df_analise_estoque.loc[df_analise_estoque['Codigo'] == i,['Quantidade','Base']]
            df_analise_estoque.loc[df_analise_estoque['Codigo'] == i, ['Quantidade','Base']] = reduzirBalde(local)
    
        #UNIDADES
        unidades = df_analise_estoque['Quantidade'].sum()
        label_unidades_estoque['text'] = f'{int(unidades)}'

        #VALOR
        df_analise_estoque['Valor'] = df_analise_estoque['Quantidade'] * df_analise_estoque['Preço']
        valor = df_analise_estoque['Valor'].sum()
        label_valor_estoque['text'] = f'R${valor:,.2f}'

        

        #RESTANTE
        df_analise_estoque['Restante'] = df_analise_estoque['Quantidade']/df_analise_estoque['Base']*100
        restante = df_analise_estoque['Restante'].mean()
        try:
            label_restante_estoque['text'] = f'{int(restante)}%'

        except:
            label_restante_estoque['text'] = '0%'

        # except:
        #     messagebox.showerror('Atenção!','Criação de Tabela com erro!')
    salva_posicao = None

    def evento_selecao_linha(event):
        '''Evento que atualiza QUANTIDADE - VALOR - RESTANTE pela linha selecionada do treeview'''
        global df_analise_estoque,salva_posicao
        
        # Eu faço a seguinte pergunta (se não selecionei essa coluna entao prossiga)
        if salva_posicao != treeview_estoque.selection():
            for item in treeview_estoque.selection():
                
                linha_selecionada = treeview_estoque.item(item, "values")            
                cod = int(linha_selecionada[0])

                local = df_analise_estoque.loc[df_analise_estoque['Codigo'] == cod,['Quantidade','Valor','Restante','Preço']].values[0]
                
                #UNIDADE
                if cod in [1,3,4]:
                    label_unidades_estoque['text'] = f'{int(local[0])}L' 
                else:
                    label_unidades_estoque['text'] = f'{int(local[0])}' 
                 
                if int(local[0]) == 0:  
                    #VALOR       
                    label_valor_estoque['text'] = f'R$ {local[3]:,.2f}'

                    #RESTANTE
                    label_restante_estoque['text'] = f'{int(0)}%'

                else:
                    #VALOR       
                    label_valor_estoque['text'] = f'R$ {local[1]:,.2f}'
                    #RESTANTE
                    label_restante_estoque['text'] = f'{int(local[2])}%'

                
            
            salva_posicao = treeview_estoque.selection()
        
        else:
            # Caso já selecionei listo denovo minha tabela e reseto a referencia da linha
            listar_Dados_estoque()
            salva_posicao = None

    
    def listar_Dados_estoque():
        global colunasDinamicas
        
        # Adicionando itens a treeview de exibir -----------------------------------------------
        style = ttk.Style()
        style.configure("Custom.Treeview", font=("Arial", 12),
                        background='white',foreground="black",fieldbackground="red")
        style.configure("Treeview.Heading", font = "Arial 10 bold")

        treeview_estoque.config(style='Custom.Treeview')
        # treeview_estoque.config(style=style.theme_use('default'))
        #Executa um comando SQL para selecionar todos os valores da tabela de Produtos
       
        cursor.execute(f"Select * From Estoque")

        #Limpa os valores da treeview_estoque
        for i in treeview_estoque.get_children():        
            treeview_estoque.delete(i)
        #Armazena os valores retornados pelo comando SQL em uma variável
        valores = cursor.fetchall()


        # modificar o cabeçario dinamico
       

        treeview_estoque.config(columns=(colunasDinamicas),show="headings")

        # cor linhas treeview
        treeview_estoque.tag_configure('oddrow', background='white')
        treeview_estoque.tag_configure('evenrow', background=cores['Linha_tre'])

        for i,coluna in enumerate(colunasDinamicas):
            treeview_estoque.heading(coluna, text=coluna)
            treeview_estoque.column(coluna,width=largura_colunas_treeview[i],anchor= CENTER)

        # Adiciona cor as linhas do Treeview
        filtro_produtosfinais = list(filter(lambda x: 'Produto Final' in x, valores))
        for index,valor in enumerate(filtro_produtosfinais):

            if index % 2 == 0:# ocorrencia de repeticao 2 em 2 ou 3 em 3
                treeview_estoque.insert("", "end", values=(valor[0], valor[1], valor[2], valor[3], valor[4], valor[6]), tags=('evenrow',))
            else:
                treeview_estoque.insert("", "end", values=(valor[0], valor[1], valor[2], valor[3], valor[4], valor[6]), tags=('oddrow',))
        
        entry_produto.delete(0,END)

        # criacao da tabela 
        criar_tabelaDinamica(valores)

    listar_Dados_estoque()
    
    # EVENTO DA TREEVIEW
    # def edicao_dados(event):
    #     editar_linha_treeview()
            
    # Evento de duplo click na lista
    # treeview_estoque.bind("<Double-1>",edicao_dados)
    # quando eu interagir com essa lista algo ira acontecer
    treeview_estoque.bind("<<TreeviewSelect>>", evento_selecao_linha)

        # Botão editar
    editar_img = PhotoImage(file=r"img_estoque\bt_editar.png")

    def editar_linha_treeview():
        try:
            '''Edita ou deleta a linha selecionada na treeview'''
            
            global colunasDinamicas
            global descricao_produto_edicao
        
            # retorna a posicao da linha selecionada
            posicao_selecionado = treeview_estoque.selection()[0]
            
            #Obtém os valores do item selecionado passando a posicao da linha 
            valores_selecionados = treeview_estoque.item(posicao_selecionado)['values']

            
            # Criando uma janela secundaria porcima da principal -> Toplevel

            janela_edicao = Toplevel(janela_estoque)#telinha sobre a pai
            janela_edicao.grab_set() # <<<< Trava os elementos que vem por traz 
            janela_edicao.title("Editar ou Deletar")#titulo
            centralizar_janela(janela_edicao,650,350,top=30)#centralizar tela
            janela_edicao.rowconfigure([0,1,2,3,4,5],weight=1)#adaptar seu filhos na linha
            janela_edicao.columnconfigure([0,1],weight=1)#adaptar seu filhos na coluna

            janela_edicao.resizable(False,False)#bloquear seu crescimento ou reducao
            janela_edicao.configure(bg=cores['Linha_tre'])#cor fundo

            #Adiciona borda para cada campo de entrada
            # estilo_borda = {'borderwidth': 2,'relief': 'groove'}  >> **estilo_borda,

            # CATEGORIA
            lista_categoria = ['ACRÉSCIMO', 'SABORES', 'BEBIDAS', 'COMPLEMENTOS', 'GELADOS', 'TAMANHO', 'ALIMENTOS', 'COBERTURAS', 'TAMANHO MK']
            Label(janela_edicao, text="Categoria:", font=("Arial", 16), bg=cores['Linha_tre']).grid(row=0, column=0, padx=10, pady=10, stick="WNS")
            categoria_produto_edicao = ttk.Combobox(janela_edicao, 
                                                    values=lista_categoria,font="Arial 16")
            
            categoria_produto_edicao.grid(row=0, column=1, padx=10, pady=10,sticky='WENS')
            categoria_produto_edicao.current(lista_categoria.index(str(valores_selecionados[1])))
            categoria_antiga = valores_selecionados[1]
            categoria_produto_edicao.bind('<KeyPress>', bloquear_texto)
            categoria_produto_edicao.bind('<KeyRelease>', bloquear_texto)

            # DESCRIÇÃO
            Label(janela_edicao, text="Descrição do Produto:", font=("Arial", 16), bg=cores['Linha_tre']).grid(row=1, column=0, padx=10, pady=10, stick="WNS")

            descricao_produto_edicao = Entry(janela_edicao, 
                                            font=("Arial", 16),bg='#FFFFFF',
                                            textvariable=StringVar(value=valores_selecionados[2]))
            descricao_produto_edicao.grid(row=1, column=1, padx=10, pady=10,sticky='WENS')
            descricao_antiga = valores_selecionados[2]
            
            
            # Usando trace para limitar o comprimento do texto
            descricao_produto_edicao.bind('<KeyRelease>', lambda event: limitar_texto(event, descricao_produto_edicao))

            

            # NATUREZA         

            Label(janela_edicao, text="Explique sua Natureza:", font=("Arial", 16), bg=cores['Linha_tre']).grid(row=2, column=0, padx=10, pady=10, stick="WNS")
            natureza_produto_edicao = ttk.Combobox(janela_edicao, 
                                                    values=["Produto Final", "Insumo"],
                                            font="Arial 16")
            natureza_produto_edicao.grid(row=2, column=1, padx=10, pady=10,sticky='WENS')
            natureza_produto_edicao.current(["Produto Final", "Insumo"].index(str(valores_selecionados[3])))
            natureza_antiga = valores_selecionados[3]
            natureza_produto_edicao.bind('<KeyPress>', bloquear_texto)
            natureza_produto_edicao.bind('<KeyRelease>', bloquear_texto)


            # NOVAS UNIDADES
            Label(janela_edicao, text="Novas Unidades:", font=("Arial", 16), bg=cores['Linha_tre']).grid(row=3, column=0, padx=10, pady=10, stick="WNS")
            novas_unidades_edicao = Entry(janela_edicao, 
                                        font=("Arial", 16), bg='#FFFFFF')
            novas_unidades_edicao.grid(row=3, column=1, padx=10, pady=10,sticky='WNES')
            unidades_antigo = valores_selecionados[4] # valor para somar com o novo passado
            

            # Seu Valor
            Label(janela_edicao, text="Valor Unitário:", font=("Arial", 16), bg=cores['Linha_tre']).grid(row=4, column=0, padx=10, pady=10, stick="WNS")
            preco_edicao = Entry(janela_edicao, 
                                            font=("Arial", 16), bg='#FFFFFF')
            preco_edicao.grid(row=4, column=1, padx=10, pady=10,sticky='WNES')
            preco_antigo = valores_selecionados[5] # valor para somar com o novo passado

            configurar_entry(preco_edicao)
            valor_recuperado = str(valores_selecionados[5])
            
            if len(valor_recuperado[valor_recuperado.index('.'):]) < 3:
                preco_edicao.insert('end',valor_recuperado + '0' )# 5.2 para 5.20 <<
            else:
                preco_edicao.insert('end',valor_recuperado)

            # BOTAO EDITAR (JANELA EDICAO DE DADOS) -------------------------------------------------------------------------------------|
                        
            def salvar_edicao():
                
                categoria_produto = str(categoria_produto_edicao.get()).upper()
                descricao_produto =  str(descricao_produto_edicao.get()).title()
                natureza_produto = str(natureza_produto_edicao.get()).title()
                preco_produto = '{:.2f}'.format(float(preco_edicao.get().replace(',','.')))
                id_selecionado = valores_selecionados[0] # recupero o id selecionado

                # Somando com as quantidades
                uni_antigo = int(unidades_antigo) if int(unidades_antigo) else 0
                if descricao_produto in ['Açai','Sorvete','Milk - Shake']:# adaptando isso 2 l para salva 2.000 ml
                    if novas_unidades_edicao.get():
                        quantidade_produto = (int(novas_unidades_edicao.get()) * 1000) + uni_antigo
                    else:
                        quantidade_produto =  uni_antigo
                else :
                    if novas_unidades_edicao.get():
                        quantidade_produto =  int(novas_unidades_edicao.get()) + uni_antigo
                    else:
                        quantidade_produto =  uni_antigo

                
                # Área de edição controlada dos ids -------------------------------------------------------------------------------------------------------

                if id_selecionado in id_Protegidos: 
                
                    # Criei uma trava para nao ser possivel adicionar preco nos baldes de acai
                    # Passa sempre o valor antigo em algumas colunas
                    if id_selecionado in [1,3,4]:
                        valoresPassados = (id_selecionado,categoria_antiga,descricao_antiga,natureza_antiga,quantidade_produto) 
                        cursor.execute(f"UPDATE Estoque SET Quantidade = ?,Base = ? WHERE Codigo = ?",(quantidade_produto,quantidade_produto,id_selecionado))
                    else:
                        valoresPassados = (id_selecionado,categoria_antiga,descricao_antiga,natureza_antiga,quantidade_produto,preco_produto) 
                        cursor.execute(f"UPDATE Estoque SET Quantidade = ?, Base = ?, Preço = ? WHERE Codigo = ?",(quantidade_produto,quantidade_produto,preco_produto,id_selecionado))

                    # Pego a posicao das colunas na tela
                    treeview_estoque.item(posicao_selecionado,values=(valoresPassados))
                    conexao.commit() #Gravando no BD
                    listar_Dados_estoque()
                    #Destruir tela cadrastrar
                    janela_edicao.destroy()

                else:
                    # Atualizar os dados no banco de dados - usa asplas para caso colunas com espaços no nome
                    #Pego a posição da linha selecionada e passo ou os mesmo valor ou novos

                    treeview_estoque.item(posicao_selecionado,values=(id_selecionado,# id da linha selecioanda
                                                                    categoria_produto,
                                                                    descricao_produto,
                                                                    natureza_produto,
                                                                    quantidade_produto,
                                                                    preco_produto))
                    cursor.execute(f"UPDATE Estoque SET Categoria = ?, Descrição = ?, Natureza = ?, Quantidade = ?, Base = ?, Preço = ? WHERE Codigo = ?",
                                (categoria_produto, descricao_produto,natureza_produto,quantidade_produto,quantidade_produto,preco_produto,id_selecionado))
                    
                    conexao.commit() #Gravando no BD
                    listar_Dados_estoque()
                    #Destruir tela cadrastrar
                    janela_edicao.destroy()
        


            botao_salvar = Button(janela_edicao,text='Editar',command=salvar_edicao,font='Arial 16',bg=cores['Verde_bt'],fg=cores['text_botao_claro'])
            botao_salvar.grid(row=5, column=0,columnspan=1, padx=20, pady=10,sticky='nsew')
                # BOTAO DELETAR (JANELA EDICAO DE DADOS) -------------------------------------------------------------------------------------|
            def deletar_produto():
                
                linha_deletar = treeview_estoque.selection()[0]
                opcao_mensagem = messagebox.askokcancel("Atenção", "Deseja deletar esse produto?")

                if opcao_mensagem:
                    
                    id = treeview_estoque.item(linha_deletar)['values'][0]# id no banco de dados

                    if id in id_Protegidos:
                        janela_edicao.destroy()
                        messagebox.showerror("Erro", "Não é possível deletar esse item!")
                        

                    else:
                        # removi do meu banco de dados
                        cursor.execute(f"DELETE FROM Estoque WHERE Codigo = ?",(id))
                        conexao.commit()

                        janela_edicao.destroy()
                        listar_Dados_estoque()

                        messagebox.showinfo("Sucesso", "Produto retirado com sucesso!")

            botao_cancelar = Button(janela_edicao,text='Deletar',command=deletar_produto,font='Arial 16',bg=cores['vermelho_bt'],fg=cores['text_botao_claro'])
            botao_cancelar.grid(row=5, column=1,columnspan=1, padx=20, pady=10,sticky='nsew')
            

        except Exception as e:
            logging.error(f"Erro ocorreu: {e}")
            messagebox.showinfo('Atenção','Seleciona um item para editar!')

    altura = 56
    largura = 143
    x, y = 945, 173

    bt_editar = Button(canvas_estoque,borderwidth=0,image=editar_img,
                        activebackground=cores["Roxo Escuro"], background=cores['Branca'], highlightthickness=0, 
                        relief="ridge",command=editar_linha_treeview)
    # bt_editar.image = editar_img
    editar_criar = canvas_estoque.create_window(x, y, width=largura,anchor="nw", height=altura, window=bt_editar)

    # Botão Novo Produto
    novo_produto_img = PhotoImage(file=r"img_estoque\bt_produto.png")
    def cadastrar():
        # Criando uma janela secundaria porcima da principal -> Toplevel
        try:
            global colunasDinamicas,descricao_produto_cadastrar
            

            janela_cadastrar = Toplevel(janela_estoque)#telinha sobre a pai
            janela_cadastrar.grab_set() # <<<< Trava os elementos que vem por traz
            janela_cadastrar.title("Cadastrar Produto")#titulo
            centralizar_janela(janela_cadastrar,650,350)#centralizar tela
            janela_cadastrar.rowconfigure([0,1,2,3,4,5],weight=1)#adaptar seu filhos na linha
            janela_cadastrar.columnconfigure([0,1],weight=1)#adaptar seu filhos na coluna
            janela_cadastrar.configure(bg=cores['Linha_tre'])#cor fundo
            janela_cadastrar.resizable(False,False)#bloquear seu crescimento ou reducao

            #Adiciona borda para cada campo de entrada
            # estilo_borda = {'borderwidth': 2,'relief': 'groove'}
            
                    
            # CATEGORIA
            fundo_label = cores['Linha_tre']
            Label(janela_cadastrar, text="Categoria:", font=("Arial", 16), bg=fundo_label).grid(row=0, column=0, padx=10, pady=10, stick="WNS")
            categoria_produto_cadastrar = ttk.Combobox(janela_cadastrar, 
                                                    values=['ACRÉSCIMO', 'SABORES', 'BEBIDAS', 'COMPLEMENTOS', 'GELADOS', 'TAMANHO', 'ALIMENTOS', 'COBERTURAS', 'TAMANHO MK'],
                                            font="Arial 16")
            categoria_produto_cadastrar.grid(row=0, column=1, padx=10, pady=10,sticky='WENS')
            categoria_produto_cadastrar.bind('<KeyPress>', bloquear_texto)
            categoria_produto_cadastrar.bind('<KeyRelease>', bloquear_texto)

            # DESCRIÇÃO
            Label(janela_cadastrar, text="Descrição do Produto:", font=("Arial", 16), bg=fundo_label).grid(row=1, column=0, padx=10, pady=10, stick="WNS")

            descricao_produto_cadastrar = Entry(janela_cadastrar, 
                                            font=("Arial",16),bg='#FFFFFF')
            descricao_produto_cadastrar.grid(row=1, column=1, padx=10, pady=10,sticky='WENS')
            #  Usando trace para limitar o comprimento do texto
            descricao_produto_cadastrar.bind('<KeyRelease>', lambda event: limitar_texto(event, descricao_produto_cadastrar))


            # NATUREZA
            Label(janela_cadastrar, text="Explique sua Natureza:", font=("Arial", 16), bg=fundo_label).grid(row=2, column=0, padx=10, pady=10, stick="WNS")
            natureza_produto_cadastrar = ttk.Combobox(janela_cadastrar, 
                                                    values=["Produto Final", "Insumo"],
                                            font="Arial 16")
            natureza_produto_cadastrar.grid(row=2, column=1, padx=10, pady=10,sticky='WENS')
            natureza_produto_cadastrar.current(1) # valor padrao
            natureza_produto_cadastrar.bind('<KeyPress>', bloquear_texto)
            natureza_produto_cadastrar.bind('<KeyRelease>', bloquear_texto)

            # NOVAS UNIDADES
            Label(janela_cadastrar, text="Novas Unidades:", font=("Arial", 16), bg=fundo_label).grid(row=3, column=0, padx=10, pady=10, stick="WNS")
            novas_unidades_cadastrar = Entry(janela_cadastrar, 
                                        font=("Arial", 16),bg='#FFFFFF')
            novas_unidades_cadastrar.grid(row=3, column=1, padx=10, pady=10,sticky='WNES')

            # Seu Valor
            Label(janela_cadastrar, text="Valor Unitário:", font=("Arial", 16), bg=fundo_label).grid(row=4, column=0, padx=10, pady=10, stick="WNS")
            preco_cadastrar = Entry(janela_cadastrar, 
                                            font=("Arial", 16),bg='#FFFFFF')
            preco_cadastrar.grid(row=4, column=1, padx=10, pady=10,sticky='WNES')
            configurar_entry(preco_cadastrar)
            def filhos(treview,coluna):
                return [treview.item(filho, "values")[coluna] for filho in treview.get_children()]
           
        
            def salvar_produto():
                
                # Verificar se a descrição do produto já está presente no Treeview
                if descricao_produto_cadastrar.get().title() not in filhos(treeview_estoque, 2):
                    # Verificar se os campos obrigatórios estão preenchidos
                    if '' not in (categoria_produto_cadastrar.get(), descricao_produto_cadastrar.get(),natureza_produto_cadastrar.get()):
                        
                        # Campos obrigatorios
                        nova_categoria = categoria_produto_cadastrar.get().upper()
                        descricao_produto = descricao_produto_cadastrar.get().title()
                        natureza_produto = natureza_produto_cadastrar.get().title()
                        
                        # Campo quantidade
                        novas_quantidade = novas_unidades_cadastrar.get()
                        
                        if novas_quantidade:
                            novas_quantidade = int(novas_unidades_cadastrar.get())
                        else:
                            novas_quantidade = 0

                        # Campo preço
                        preco_novo = float(str(preco_cadastrar.get()).replace(',','.'))
                        
                            

                        # Inserir os dados no Treeview e no banco de dados
                        try:
                            novo_produto_cadastrar = (nova_categoria, descricao_produto, natureza_produto, novas_quantidade,novas_quantidade, preco_novo)
                            
                            # Inserir no banco de dados
                            cursor.execute("INSERT INTO Estoque (Categoria, Descrição, Natureza, Quantidade,Base, Preço) Values (?, ?, ?, ?, ?, ?)", 
                                        novo_produto_cadastrar)
                            conexao.commit()  # Gravar no BD
                            
                            # Atualizar a interface e fechar a janela de cadastro
                            treeview_estoque.insert("", "end", values=novo_produto_cadastrar)
                            janela_cadastrar.destroy()
                            listar_Dados_estoque()
                        except Exception as db_error:
                            logging.error(f"Erro ao inserir dados no banco de dados: {db_error}")
                            messagebox.showerror("Erro", "Ocorreu um erro ao salvar os dados. Tente novamente mais tarde.")
                    else:
                        
                        messagebox.showwarning('Atenção', 'Preencha todos os campos obrigatórios.')
                else:
                    messagebox.showwarning('Atenção', 'Produto já cadastrado.')


            
            botao_salvar = Button(janela_cadastrar,text='Cadastrar Produto',command=salvar_produto,font='Arial 16',fg="#FFFFFF",bg="#008000")
            botao_salvar.grid(row=5, column=0,columnspan=1, padx=10, pady=10,sticky='WNES')

            botao_cancelar = Button(janela_cadastrar,text='Cancelar',command=janela_cadastrar.destroy,font='Arial 16',bg="#FF0000",fg="#FFFFFF")
            botao_cancelar.grid(row=5, column=1,columnspan=1, padx=10, pady=10,sticky='WNES')



        except Exception as e:
            logging.error(f"Erro inesperado: {e}")
            messagebox.showerror('Erro', 'Ocorreu um erro inesperado. Verifique os campos e tente novamente.')
                            


        


        
    
    altura = 56
    largura = 155
    x, y = 781, 173

    bt_produto = Button(canvas_estoque,borderwidth=0,image=novo_produto_img,
                        activebackground=cores["Roxo Escuro"], background=cores['Branca'], 
                        highlightthickness=0, relief="ridge",command=cadastrar)
    # bt_produto.image = novo_produto_img
    produto_criar = canvas_estoque.create_window(x, y, width=largura,anchor="nw", height=altura, window=bt_produto)
    
    # janela_estoque.lift()  # Levanta a janela_estoque acima da root
    # janela_estoque.focus_force()  # Forçar foco novamente na janela_estoque
    # Esperar até que a janela seja fechada
    root.wait_window(janela_estoque)

x,y,w,h = posicionar_OBJ_tela(valor_x = 1024 + x_dinamica,
                              valor_y = 616 + espaço + y_dinamico*0.90,                             
                              w = 241 + 5,
                              h = 112 + 8)

estoque_img = PhotoImage(file=r"img_inicio\bt_estoque.png")
analise_bt = Button(image=estoque_img, borderwidth=0, background="#280D2B", activebackground=cores['fundo_cinza'], 
                    highlightthickness=0, relief="ridge",command=funcao_estoque)
estoque_criar = canvas.create_window(x, y, width=w,anchor="nw", height=h, window=analise_bt)


root.mainloop()

cursor.close()
conexao.close()