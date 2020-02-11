#!/usr/bin/python3
# -*- coding: utf-8 -*-

from tkinter.font import nametofont
from threading import Thread
from funcoes import *
from random import randint
from tkinter import filedialog
from tkinter import PhotoImage
from tkinter import messagebox
from tkinter import DISABLED
from tkinter import Toplevel
from tkinter import CURRENT
from tkinter import INSERT
from tkinter import Scrollbar
from tkinter import RAISED
from tkinter import Button
from tkinter import NORMAL
from tkinter import Frame
from tkinter import Menu
from tkinter import NSEW
from tkinter import FLAT
from tkinter import Text
from tkinter import font
from tkinter import END
from tkinter import Tk
from time import sleep
from time import time
from json import load
from os import listdir
from re import finditer
from re import findall

__author__      = 'Gabriel Gregório da Silva'
__email__       = 'gabriel.gregorio.1@outlook.com'
__project__     = 'Combratec'
__github__      = 'https://github.com/Combratec/'
__description__ = 'Linguagem de programação focada em lógica'
__status__      = 'Desenvolvimento'
__date__        = '01/08/2019'
__last_update__ = '08/02/2020'
__version__     = '0.1'

# funcao que está sendo analisada
global funcao_em_analise

# Contém o link e o texto do arquivo
global arquivo_aberto_atualmente

# A tela está em full screen
global bool_tela_em_fullscreen

# Aconteceu algum erro durante a execução do programa
global aconteceu_erro

# impede que o programa seja iniciado enquanto outro está sendo executado
global numeros_thread_interpretador

# Altura da janela em linhas
global altura_widget

# Exibe as informações do interpretador em tempo real
global tx_terminal

# Local onde o programa é codificado
global tx_codificacao

# Comandos internos a cada função
global dic_sub_com

# Dicionário com toodos os comandos disponíveis
global dic_com

# Posição do log registrado
global numero_log

# Detecta quando o usurio pressionou enter em um comando de entrada
global esperar_pressionar_enter

# Dicionario com todas as funcoes
global dic_funcoes

# Variáveis usadas durante a interpretação do programa
global dic_variaveis

# Contador de linhas do programa
global lb_linhas

# Tema da interface principal
global dic_design

# Tema de sintaxe
global cor_da_sintaxe

# Janela do interpretador
global top_janela_terminal

# Erro já foi alertado para o usuário
global erro_alertado

# Linha sendo executada
global linhaExecucao

# Posicao corrente
global posCorrente

# Posicao absoluta na tela de codificacao
global posAbsuluta

numeros_thread_interpretador   = 0
esperar_pressionar_enter     = False
arquivo_aberto_atualmente      = {'link': None,'texto': None}
bool_tela_em_fullscreen        = False
aconteceu_erro                 = False
dic_variaveis                  = {}
dic_funcoes                    = {}
posAbsuluta                    = 0
posCorrente                    = 0
numero_log                     = 1

dic_sub_com, dic_com, dic_design, cor_da_sintaxe = atualiza_configuracoes_temas()

def salvarArquivoComoDialog(event = None):
    global arquivo_aberto_atualmente

    # Escolha um local
    arquivo = filedialog.asksaveasfile(mode='w',
        defaultextension=".fyn",
        title = "Selecione o script",
        filetypes = (("Meus scripts", "*.fyn"), ("all files", "*.*")))

    # Se não for feito nenhuma escolha
    if arquivo is None:
        return None

    # Busque o conteudo da tela principal
    text2save = str(tx_codificacao.get(1.0, END))

    try:
        # Salve no arquivo escolhido
        arquivo.write(text2save[0:-1])
        arquivo.close()

    except Exception as erro:
        messagebox.showinfo('Erro', 'Erro ao salvar programa, erro: {}'.format(erro))
        log(" Erro ao salvar o arquivo, erro: {}".format(erro))

    else:
        # Atualize os dados globais do arquivo aberto atualmente
        arquivo_aberto_atualmente['link'] = arquivo.name
        arquivo_aberto_atualmente['texto'] = text2save
        return arquivo.name

def salvarArquivo(event=None):
    global arquivo_aberto_atualmente

    # Se nenhum arquivo foi salvo
    if arquivo_aberto_atualmente['link'] == None:
        salvarArquivoComoDialog()

    else: # Se o arquivo já estava aberto
        programaCodigo = tx_codificacao.get(1.0, END)

        # Vamos salvar o arquivo por que o texto está diferente
        if arquivo_aberto_atualmente['texto'] != programaCodigo:
            try:
                arquivo = open(arquivo_aberto_atualmente['link'], 'w')
                arquivo.write(programaCodigo[0:-1])
                arquivo.close()
            except Exception as erro:
                messagebox.showinfo('Erro', 'Não foi possível salvar essa versão do código, erro: {}'.format(erro))
                log(" Não foi possível salvar essa versão do código")
            else:
                arquivo_aberto_atualmente['texto'] = programaCodigo
        else:
            log(" Programa não sofreu modificações para ser salvo novamente....")

def abrirArquivoDialog(event=None):
    global arquivo_aberto_atualmente

    ftypes = [('Scripts fyn', '*.fyn'), ('Todos os arquivos', '*')]
    dlg = filedialog.Open(filetypes = ftypes)
    filename = dlg.show()

    if filename != ():
        log(' Arquivo "{}" escolhido'.format(filename))
        arquivo = abrir_arquivo(filename)

        if arquivo != None:
            tx_codificacao.delete(1.0, END)
            tx_codificacao.insert(END, arquivo)

        atualiza_cor_sintaxe()

        arquivo_aberto_atualmente['link'] = filename
        arquivo_aberto_atualmente['texto'] = arquivo
    else:
        log(' Nenhum arquivo escolhido')

def abrirArquivo(link):
    global arquivo_aberto_atualmente

    log(' Abrindo arquivo "{}" escolhido'.format(link))

    arquivo = abrir_arquivo(link)

    if arquivo != None:
        tx_codificacao.delete(1.0, END)
        tx_codificacao.insert(END, arquivo)
        atualiza_cor_sintaxe()

        arquivo_aberto_atualmente['link'] = link
        arquivo_aberto_atualmente['texto'] = arquivo
    else:
        messagebox.showinfo('Erro', 'Aconteceu um erro ao tentar abrir o script: {}'.format(link))
        print('Arquivo não selecionado')

def colorir_uma_palavra(palavra, linha, valor1, valor2, cor):
    ''' Realiza a coloracao de uma unica palavra'''
    linha1 = '{}.{}'.format(linha , valor1)
    linha2 = '{}.{}'.format(linha , valor2)

    tx_codificacao.tag_add(palavra, linha1 , linha2)
    tx_codificacao.tag_config(palavra, foreground = cor)

def colorir_erro(palavra, valor1, valor2, cor='red'):
    global tx_terminal
    global erro_alertado

    linha = tx_terminal.get(1.0, END)
    linha = len(linha.split('\n'))-1

    linha1 = '{}.{}'.format(linha , valor1)
    linha2 = '{}.{}'.format(linha , valor2)

    tx_terminal.tag_add(palavra, linha1 , linha2)
    tx_terminal.tag_config(palavra, foreground = cor)

    erro_alertado = True

def sintaxe(palavra, cor):

    global tx_codificacao
    cor = cor['foreground']

    tx_codificacao.tag_delete(palavra)
    lista = tx_codificacao.get(1.0, END).lower().split('\n')

    '''Remoção de bugs no regex, deixe ele aqui para evitar um \* \\* \\\*\\\\* no loop'''
    palavra_comando = palavra.replace('+', '\\+')
    palavra_comando = palavra_comando.replace('/', '\\/')
    palavra_comando = palavra_comando.replace('*', '\\*')

    # Ande por todas as linhas do programa
    for linha in range(len(lista)):

        # Se a palavra for apontada como string
        if palavra == '"':
            for valor in finditer("""\"[^"]*\"""", lista[linha]):
                colorir_uma_palavra(
                    str(palavra), str(linha+1), valor.start(), valor.end(), cor)

        # se a palavra foi apontada como numérico
        elif palavra == "numerico":
            for valor in finditer(
                '(^|\\s|\\.|\\,)[0-9]{1,}($|\\s|\\.|\\,)', lista[linha]):
                colorir_uma_palavra(
                    str(palavra), str(linha+1), valor.start(), valor.end(), cor)

        # Se a palavra foi apontada como comentário
        elif palavra == "comentario":
            for valor in finditer('(#|\\/\\/).*$', lista[linha]):
                colorir_uma_palavra(
                    str(palavra), str(linha+1), valor.start(), valor.end(), cor)

        # Se for uma palavra especial
        else:
            palavra_comando = palavra_comando.replace(' ','\\s*')
            for valor in finditer('(^|\\s){}(\\s|$)'.format(palavra_comando), lista[linha]):
                colorir_uma_palavra(
                    str(palavra), str(linha+1), valor.start(), valor.end(), cor)

# Cores que as palavras vão assumir
def atualiza_cor_sintaxe(event=None):

    global dic_com
    global tx_codificacao
    global cor_da_sintaxe
    configuracoes(ev = None)

    # SE O EVENTO NÃO MODIFICAR O CÓDIGO
    if event != None:
        if event.keysym in ('Down','Up','Left','Right'):
            return 0
    try:
        # PRINCIPAIS COMANDOS
        for comando in dic_com['declaraVariaveis']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["atribuicao"])

        for comando in dic_com['declaraListas']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["lista"])

        for comando in dic_com['adicionarItensListas']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["lista"])

        for comando in dic_com['tiverLista']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["lista"])

        for comando in dic_com['RemoverItensListas']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["logico"])

        for comando in dic_com['tamanhoDaLista']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["lista"])

        for comando in dic_com['digitado']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["tempo"])

        for comando in dic_com['loopsss']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["lista"])

        for comando in dic_com['repita']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["lista"])

        for comando in dic_com['se']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["condicionais"])

        for comando in dic_com['mostre']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["exibicao"])

        for comando in dic_com['mostreNessa']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["exibicao"])

        for comando in dic_com['funcoes']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["tempo"])

        for comando in dic_com['aguarde']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["tempo"])

        for comando in dic_com['aleatorio']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["tempo"])

        for comando in dic_com['limpatela']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["tempo"])

        # COMANDOS INTERNOS DE CADA COMANDO
        for comando in dic_sub_com['passandoParametros']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["tempo"])

        for comando in dic_sub_com['acesarListas']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["lista"])

        for comando in dic_sub_com['adicionarItensListas']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["lista"])

        for comando in dic_sub_com['RemoverItensListas']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["lista"])

        for comando in dic_sub_com['tiverLista']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["lista"])

        for comando in dic_sub_com['recebeParametros']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["tempo"])

        for comando in dic_sub_com['esperaEm']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["tempo"])

        for comando in dic_sub_com['matematica']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["contas"])

        for comando in dic_sub_com['repitaVezes']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["lista"])

        for comando in dic_sub_com['logico']:
            sintaxe(comando[0].strip(), cor_da_sintaxe["logico"])

        sintaxe('numerico'     , cor_da_sintaxe["numerico"])
        sintaxe('"'            , cor_da_sintaxe["string"])
        sintaxe('comentario'   , cor_da_sintaxe["comentario"])

        tx_codificacao.update()
    except Exception as erro:
        print("Erro ao atualizar sintaxe", erro)

def log(mensagem):
    global numero_log
    numero_log += 1
    print(str(numero_log) + mensagem)

# inicia o interpretador
def inicializador_orquestrador_interpretador(event = None):
    global numeros_thread_interpretador
    global aconteceu_erro
    global tx_codificacao
    global dic_variaveis
    global erro_alertado
    global linhaExecucao

    # MARCA O INICIO DO PROGRAMA
    inicio = time()

    # SE ALGUM PROGRAMA JÁ ESTIVER SENDO EXECUTADO
    if numeros_thread_interpretador != 0:
        messagebox.showinfo('Problemas',"Já existe um programa sendo executado!")
        return 0

    # CONTADOR DE THREADS
    numeros_thread_interpretador = 0

    # ALERTA DE ERROS
    aconteceu_erro = False

    # VARIÁVEIS DO PROGRAMA
    dic_variaveis = {}

    # NENHUM ERRO REPORTADO DESENVOLVEDOR
    erro_alertado = False

    # LINHA SENDO EXECUTADA
    linhaExecucao = 1

    # FUNÇÕES DO INTERPRETADOR
    dic_funcoes = {}

    # INICIA O TERMINAL
    inicializador_terminal()

    # LIMPA O TERMINAL
    tx_terminal.delete('1.0', END)

    # OBTÊM O CÓDIGO DO PROGRAMA
    linhas = tx_codificacao.get('1.0', END)

    # INICIA O INTERPRETADOR
    t = Thread(target=lambda codigoPrograma = linhas: orquestrador_interpretador(codigoPrograma))
    t.start()

    # ENQUANTO O INTERPRETADOR NÃO FOR FINALIZADO
    while numeros_thread_interpretador != 0:
        tela.update()

    # INFORMAÇÕES DE FINALIZAÇÃO
    tx_terminal.insert(END, '\nScript finalizado em {:.3} segundos'.format(time() - inicio))
    tx_terminal.see("end")

def orquestrador_interpretador(linhas):
    global numeros_thread_interpretador
    global aconteceu_erro
    global dic_funcoes
    global funcao_em_analise
    global linhaExecucao

    # CONTADOR DE CARACTERES
    contador = 0

    # PENETRAÇÃO DE BLOCO DE FORMA RECURSIVA {{{}}}
    penetracao = 0

    # BLOCOS DE CÓDIGO
    ComandosParaAnalise = ''

    # NUMERO DE VEZES QUE O INTERPRETADOR FOI CHAMADO
    numeros_thread_interpretador += 1

    # INSTRUÇÕES PARA TESTES: ENQUANTO X FOR MENOR QUE Y
    linhaComCodigoQueFoiExecutado = ''

    # BLOCO DE CÓDIGO SENDO SALVO
    BlocoDeCodigoEstaEmAnalise = False

    # LER UM BLOCO DE CÓDIGO
    estadoDaCondicional = [False, None, 'vazio']

    # ENQUANTO NÃO LER TODOS OS CARACTERES  E NÃO ACONTECER UM ERRO
    while contador < len(linhas) and not aconteceu_erro:

        # Se começar um bloco e não tiver começado nenhum anteriormente
        if linhas[contador] == '{' and BlocoDeCodigoEstaEmAnalise == False:

            # Aumente a penetração
            penetracao +=1

            # Se não for uma linha vazia
            if not ComandosParaAnalise.isspace() and  ComandosParaAnalise != '':

                # Teste com a condicional anterior
                estadoDaCondicional = interpretador(ComandosParaAnalise.strip())

                # Se aconteceu um erro
                if estadoDaCondicional[0] == False:
                    aconteceu_erro = True
                    if not erro_alertado:
                        erro_texto = 'linha {} '.format(linhaExecucao) + str(estadoDaCondicional[1])
                        tx_terminal.insert(END, erro_texto)
                        colorir_erro('codigoErro', valor1=0, valor2=len(erro_texto)+1, cor='#f78b8b')

                    numeros_thread_interpretador -= 1
                    return estadoDaCondicional

                # Se não for vazia e nem for um booleano
                #..sucesso..saida..tipoSaida..ordem
                if estadoDaCondicional[0] == True and estadoDaCondicional[3] == 'exibirNaTela':

                    # Insere o texto no Terminal
                    if ":nessaLinha:" in str(estadoDaCondicional[1]):
                        tx_terminal.insert(END, str(estadoDaCondicional[1][len(":nessaLinha:"):]))
                    else:
                        tx_terminal.insert(END, str(estadoDaCondicional[1])+'\n')

                    tx_terminal.see("end")

            # Limpa os comandos para analise
            ComandosParaAnalise = ''

            # Aumenta o contador
            contador += 1

            # Começar a salvar o bloco de código
            BlocoDeCodigoEstaEmAnalise = True
            continue

        # Se tiver mais um {, aumenta a penetração
        if linhas[contador] == '{':
            penetracao +=1

        # Se tiver um }, diminui a penetração
        if linhas[contador] == '}':
            penetracao -=1

        # Se o bloco principal finalizar, se ele estava em análise e a penetração chegou a 0
        if linhas[contador] == '}' and BlocoDeCodigoEstaEmAnalise and penetracao == 0:

            # Se a condição do começo do bloco era verdadeira
            if estadoDaCondicional[1] == True or estadoDaCondicional[1] != 0:
                print(estadoDaCondicional)
                # Se acontecer um loop repetir
                if estadoDaCondicional[3] == 'declararLoop':
                    estadoDaCondicional[3] = 'fazerNada'

                    # Enquanto a condição for verdadeira
                    while linhaComOResultadoDaExecucao[1] and not aconteceu_erro:

                        # Envia um bloco completo para ser novamente executado
                        resultadoExecucao = orquestrador_interpretador(
                            ComandosParaAnalise)

                        # Se der erro na exeução do bloco
                        if resultadoExecucao[0] == False:

                            aconteceu_erro = True

                            if not erro_alertado:
                                erro_texto = 'linha {} '.format(linhaExecucao) + str(resultadoExecucao[1])
                                tx_terminal.insert(END, erro_texto)
                                colorir_erro('codigoErro', valor1=0, valor2=len(erro_texto)+1, cor='#f78b8b')

                            numeros_thread_interpretador -= 1
                            return resultadoExecucao

                        # Testa novamente a condição do loop
                        linhaComOResultadoDaExecucao = interpretador(
                            linhaComCodigoQueFoiExecutado)

                        # Se der erro na exeução do teste
                        if linhaComOResultadoDaExecucao[0] == False:
                            aconteceu_erro = True
                            if not erro_alertado:
                                erro_texto = 'linha {} '.format(linhaExecucao) + str(linhaComOResultadoDaExecucao[1])
                                tx_terminal.insert(END, erro_texto)
                                colorir_erro('codigoErro', valor1=0, valor2=len(erro_texto)+1, cor='#f78b8b')

                            numeros_thread_interpretador -= 1
                            return linhaComOResultadoDaExecucao

                # SE A FUNÇÃO FOR ATIVADA
                elif estadoDaCondicional[3] == "declararLoopRepetir":
                    estadoDaCondicional[3] = 'fazerNada'

                    print(estadoDaCondicional,'looooooooooop')

                    # Se for maior que zero, aconteceu um repit
                    for valor in range(0, estadoDaCondicional[1]):

                        # Envia um bloco completo para ser novamente executado
                        resultadoOrquestrador = orquestrador_interpretador(
                            ComandosParaAnalise)

                        # Se acontecer um erro
                        if resultadoOrquestrador[0] == False:
                            aconteceu_erro = True

                            if not erro_alertado:
                                erro_texto = 'linha {} '.format(linhaExecucao) + str(resultadoOrquestrador[1])
                                tx_terminal.insert(END, erro_texto)
                                colorir_erro('codigoErro', valor1=0, valor2=len(erro_texto)+1, cor='#f78b8b')

                            numeros_thread_interpretador -= 1
                            return resultadoOrquestrador

                    estadoDaCondicional[1] = 0
                    linhaComOResultadoDaExecucao = [True, False, 'booleano']

                # Se uma função foi ativada
                elif estadoDaCondicional[3] == "declararFuncao":
                    estadoDaCondicional[3] = "fazerNada"

                    # Atualize o dicionário de funções
                    dic_funcoes[funcao_em_analise] = [dic_funcoes[funcao_em_analise][0], ComandosParaAnalise]

                # Se for uma condição normal
                else:
                    # Envia um bloco completo para ser executado
                    resultadoOrquestrador = orquestrador_interpretador(
                        ComandosParaAnalise)

                    # Se acontecer um erro
                    if resultadoOrquestrador[0] == False:
                        aconteceu_erro = True

                        if not erro_alertado:
                            erro_texto = 'linha {} '.format(linhaExecucao) + str(resultadoOrquestrador[1])
                            tx_terminal.insert(END, erro_texto)
                            colorir_erro('codigoErro', valor1=0, valor2=len(erro_texto)+1, cor='#f78b8b')
                        numeros_thread_interpretador -= 1
                        return resultadoOrquestrador

            ComandosParaAnalise = ''
            contador += 1
            BlocoDeCodigoEstaEmAnalise = False

        # Se chegar no final do código, ou no final da linha e o bloco de código não está em análise
        if (((contador == len(linhas)) or (linhas[contador] == '\n')) ) and not BlocoDeCodigoEstaEmAnalise:

            # Se não for uma linha vazia
            if not ComandosParaAnalise.isspace() and  ComandosParaAnalise != '':

                # Inicie o interpretador com a linha
                estadoDaCondicional = interpretador(ComandosParaAnalise.strip())

                # Se deu errado ao executar
                if estadoDaCondicional[0] == False:
                    aconteceu_erro = True

                    if not erro_alertado:
                        erro_texto = 'linha {} '.format(linhaExecucao) + str(estadoDaCondicional[1])
                        tx_terminal.insert(END, erro_texto)
                        colorir_erro('codigoErro', valor1=0, valor2=len(erro_texto)+1, cor='#f78b8b')

                    numeros_thread_interpretador -= 1
                    return estadoDaCondicional

                # Salva o resultado da condição testada
                linhaComOResultadoDaExecucao = estadoDaCondicional

                # Salva o código testado
                linhaComCodigoQueFoiExecutado = ComandosParaAnalise.strip()

                # Se não for um aviso de estado
                if (estadoDaCondicional[0] == True and estadoDaCondicional[3] == 'exibirNaTela'):

                    # Insere no menu lateral
                    if ":nessaLinha:" in str(estadoDaCondicional[1]):
                        tx_terminal.insert(END, str(estadoDaCondicional[1][len(":nessaLinha:"):]))
                    else:
                        tx_terminal.insert(END, str(estadoDaCondicional[1])+'\n')

                    tx_terminal.see("end")

            # Limpar o bloco de comandos
            ComandosParaAnalise = ''

            # Avançar para os próximos caracteres
            contador += 1

            # Chegou ao final de uma execução
            continue

        # Armazena os caracteres de uma linha
        ComandosParaAnalise += linhas[contador]

        # Aumenta o contador
        contador += 1

    # Se chegar ao final do loop e a penetração ficar positiva
    if penetracao > 0:

        aconteceu_erro = True

        if penetracao == 1:
            vezesEsquecidas = '1 vez'
        else:
            vezesEsquecidas = '{} vezes'.format(penetracao)

        msgErro = "Você abriu uma chave '{' e esqueceu de fecha-la '}'  " + str(vezesEsquecidas)

        if not erro_alertado:
            erro_texto = 'linha {} '.format(linhaExecucao) + msgErro
            tx_terminal.insert(END, erro_texto)
            colorir_erro('codigoErro', valor1=0, valor2=len(erro_texto)+1, cor='#f78b8b')

        numeros_thread_interpretador -= 1
        return [False, None, 'vazia']

    # Se chegar ao final do loop e a penetração ficar negativa
    elif penetracao < 0:
        aconteceu_erro = True
        if penetracao == -1:
            vezesEsquecidas = 'uma vez'
        else:
            vezesEsquecidas = '{} vezes'.format(penetracao*-1)

        msgErro = "Você abriu uma chave '{' e fechou ela '}' " + str(vezesEsquecidas)

        if not erro_alertado:
            erro_texto = 'linha {} '.format(linhaExecucao) + msgErro
            tx_terminal.insert(END, erro_texto)
            colorir_erro('codigoErro', valor1=0, valor2=len(erro_texto)+1, cor='#f78b8b')

        numeros_thread_interpretador -= 1
        return [False, None, 'vazia']

    # Libera uma unidade no contador de Threads
    numeros_thread_interpretador -= 1
    return [True, 'Não aconteceram erros durante a execução do interpretador', 'string']

# Interpreta um conjunto de linhas
def interpretador(codigo):
    global linhaExecucao
    global aconteceu_erro
    global dic_com
    global dic_variaveis

    logs = '  > '

    linhaExecucao += 1

    if aconteceu_erro:
        return [False, 'Um erro foi encontrado ao iniciar o interpretador', 'string','exibirNaTela']

    log('> ##### INTERPRETADOR ACIONADO ##### ')

    codigo = codigo.strip()

    # Limpa o número de repeticoes
    simbolosEspeciais = ['{', '}']

    # Se o código estiver vazio
    if (codigo == '' or codigo.isspace()) or codigo in simbolosEspeciais:
        return [True, None, 'vazio','fazerNada']

    else:
        # Obtem todas as linhas
        linhas = codigo.split('\n')

        for linha in linhas:
            linha = linha.strip()

            ignoraComentario = linha.find('#')
            if ignoraComentario != -1:
                linha = linha[0:ignoraComentario]

            ignoraComentario = linha.find('//')
            if ignoraComentario != -1:
                linha = linha[0:ignoraComentario]

            if linha == '':
                continue

            for comando in dic_com['mostreNessa']:
                if len(comando[0]) < len(linha):
                    if comando[0] == linha[0:len(comando[0])]:
                       log('> Função exibicao nessa linha: "{}"'.format(codigo))
                       return funcao_exibir_na_linha(linha[len(comando[0]):], logs)

            for comando in dic_com['mostre']:
                if len(comando[0]) < len(linha):
                    if comando[0] == linha[0:len(comando[0])]:
                       log('> Função exibicao: "{}"'.format(codigo))
                       return funcao_exibir(linha[len(comando[0]):], logs)

            for comando in dic_com['limpatela']:
                if len(comando[0]) <= len(linha):
                    if comando[0] == linha:
                       log('> Função limpar a tela: "{}"'.format(codigo))
                       return funcao_limpar_tela(logs)

            for comando in dic_com['se']:
                if len(comando[0]) < len(linha):
                    if comando[0] == linha[0:len(comando[0])]:
                       log('> Função condicional: "{}"'.format(codigo))
                       return funcao_condicional(linha[len(comando[0]):], logs)

            for comando in dic_com['loopsss']:
                if len(comando[0]) < len(linha):
                    if comando[0] == linha[0:len(comando[0])]:
                       log('> Função loops enquanto: "{}"'.format(codigo))
                       return funcao_loops_enquanto(linha[len(comando[0]):], logs)

            for comando in dic_com['aguarde']:
                if len(comando[0]) < len(linha):
                    if comando[0] == linha[0:len(comando[0])]:
                       log('> Função tempo: "{}"'.format(codigo))
                       return funcao_tempo(linha[len(comando[0]):], logs)

            for comando in dic_com['funcoes']:
                if len(comando[0]) < len(linha):
                    if comando[0] == linha[0:len(comando[0])]:
                       log('> Função declarar funções: "{}"'.format(codigo))
                       return funcao_declarar_funcao(linha[len(comando[0]):], logs)

            for comando in dic_com['aleatorio']:
                if len(comando[0]) < len(linha):
                    if comando[0] == linha[0:len(comando[0])]:
                       log('> Função numero aleatório: "{}"'.format(codigo))
                       return funcao_numero_aleatorio(linha[len(comando[0]):], logs)

            for comando in dic_com['repita']:
                if len(comando[0]) < len(linha):
                    if comando[0] == linha[0:len(comando[0])]:
                       log('> Função repetir: "{}"'.format(codigo))
                       return funcao_repetir(linha[len(comando[0]):], logs)

            for comando in dic_com['digitado']:
                if len(comando[0]) <= len(linha):
                    if comando[0] == linha:
                       log('> Função digitado: "{}"'.format(codigo))
                       return funcao_digitado(linha, logs)

            for comando in dic_com['declaraListas']:

                testa = verifica_se_tem(linha, ' na posicao ', logs)

                if testa != [] and comando[0] == linha[ 0 : len(comando[0])]:
                    log('> Função Substituir valor da listas: "{}"'.format(codigo))
                    return funcao_adicionar_declarar_itens_na_lista(linha[len(comando[0]):], logs)

            for comando in dic_com['declaraListas']:
                testa = verifica_se_tem(linha, comando[0], logs)
                if testa != [] and comando[0] == linha[0:len(comando[0])]:
                    log('> Função declara listas: "{}"'.format(codigo))
                    return funcao_declarar_listas(linha[len(comando[0]):], logs)

            for comando in dic_com['tiverLista']:
                testa = verifica_se_tem(linha, comando[0], logs)
                if testa != [] and comando[0] == linha[0:len(comando[0])]:
                    log('> Função tiver listas: "{}"'.format(codigo))
                    return funcao_tiver_na_lista(linha[len(comando[0]):], logs)

            for comando in dic_com['adicionarItensListas']:
                testa = verifica_se_tem(linha, comando[0], logs)
                if testa != [] and comando[0] == linha[0:len(comando[0])]:
                    log('> Função Adicionar itens na lista: "{}"'.format(codigo))
                    return funcao_adicione_na_lista(linha[len(comando[0]):], logs)

            for comando in dic_com['RemoverItensListas']:
                testa = verifica_se_tem(linha, comando[0], logs)
                if testa != []:
                    if comando[0] == linha[0:len(comando[0])]:
                        log('> Função Remover itens na lista: "{}"'.format(codigo))
                        return funcao_remover_itens_na_lista(linha[len(comando[0]):], logs)

            for comando in dic_com['tamanhoDaLista']:
                testa = verifica_se_tem(linha, comando[0], logs)
                if testa != []:
                    if comando[0] == linha[0:len(comando[0])]:
                        log('> Função retorna a quantidade de itens da lista: "{}"'.format(codigo))
                        return funcao_tamanho_da_lista(linha[len(comando[0]):], logs)

            #for comando in dic_sub_com['acesarListas']:
            #    testa2 = verifica_se_tem(linha, comando, logs)
            #    if testa2 != []:
            #        log('> Função retorna uma posicao de uma lista: "{}"'.format(codigo))
            #        return funcao_obter_valor_lista(linha, comando, logs)

            for comando in dic_com['declaraVariaveis']:
                testa = verifica_se_tem(linha, comando[0], logs)
                if testa != []:
                    log('> Função atribuição: "{}"'.format(codigo))
                    return funcao_fazer_atribuicao(linha, comando[0], logs)

            if linha[0].isalnum():
                log('> Função executar funções: "{}"'.format(codigo))
                return funcao_executar_funcoes(linha, logs)

            ''' lista de nomes na posicao 1 recebe o que o usuario digitar'''
            log('> Comando desconhecido: "{}"'.format(codigo))
            return [False, "Um comando desconhecido foi localizado:'{}'".format(linha), 'string','exibirNaTela']

    return [True, None, 'vazio', 'fazerNada']


def verifica_se_tem(linha, a_buscar, logs):
    logs = '  ' + logs
    log(logs + 'Verifica se tem: "{}", a buscar por: "{}"'.format(linha, a_buscar))

    analisar = True
    lista = []

    for car in range(len(linha)):
        if linha[car] == '"' and analisar == True:
            analisar = False

        elif linha[car] == '"' and analisar == False:
            analisar = True

        # Se estiver disponivel para analisar
        if analisar:

            # Se não estourar o limite
            if len(linha) >= car + len(a_buscar):

                if linha[car : car + len(a_buscar) ] == a_buscar:
                    lista.append([car, car + len(a_buscar) ])

    return lista

def funcao_adicione_na_lista(linha, logs):
    logs = '  ' + logs
    log(logs + 'Função adicione na lista: "{}"'.format(linha))

    resto = ''
    variavelLista = ''

    # 1 A LISTA DE NOMES
    for sub_comando in dic_sub_com["adicionarItensListas"]:

        # 1, NOMES
        testa = verifica_se_tem(linha, sub_comando[0], logs)
        if testa != []:
            resto = linha[ : testa[0][0] ].strip()
            variavelLista = linha[testa[0][1] : ].strip()
            break

    # SE NÃO ESTIVER NA ESTRUTURA PROPOSTA
    if resto == "" or variavelLista == "":
        return [ False, 'Necessário comando separador', 'string',' exibirNaTela']

    # VERIFICA SE A VARIÁVEL EXISTE
    teste_existencia = obter_valor_variavel(variavelLista, logs)

    if teste_existencia[0] == False:
        return teste_existencia

    # SE ELA NÃO FOR UMA LISTA
    if teste_existencia[2] != 'lista':
        return[False, 'A variável "{}" não é uma lista.'.format(variavelLista), 'string']

    # ISSO É PÉSSIMO, STRINGS FERRAM O SISTEMA
    testa = verifica_se_tem(resto, ' na posicao ', logs)

    if testa != []:
        valor = resto[ : testa[0][0]].strip()
        posicao = resto[testa[0][1] : ].strip()

        testePosicao = abstrair_valor_linha(posicao, logs)

        if testePosicao[0] == False:
            return testePosicao

        if testePosicao[2] != 'float':
            return [False, 'O valor precisa ser numérico',' string', 'exibirNaTela']

        posicao = int(testePosicao[1])

    else:
        valor = resto

    # VERIFICA SE O VALOR É VÁLIDO
    teste_valor = abstrair_valor_linha(valor, logs)
    #  VERIFICA SE O VALOR E VÁLIDO
    if (teste_valor[0] == False):
        return teste_valor

    testa = verifica_se_tem(resto, ' na posicao ', logs)
    if testa != []:

        if posicao - 1 > len(dic_variaveis[variavelLista][0]):
            return [False, 'O valor está fora do escopo', 'string', 'exibirNaTela']

        if posicao < 1 :
            return [False, 'O abaixo do escopo permitido', 'string', 'exibirNaTela']
        
        dic_variaveis[variavelLista][0].insert(posicao - 1, [teste_valor[1], teste_valor[2]])

    # ADICIONAR NO COMEÇO DA LISTA
    testa  = verifica_se_tem(linha, ' no inicio ', logs)
    testa2 = verifica_se_tem(linha, ' no comeco ', logs)

    if testa != [] or testa2 != []:
        dic_variaveis[variavelLista][0].insert(0, [teste_valor[1], teste_valor[2]])
    else:
        dic_variaveis[variavelLista][0].append([teste_valor[1], teste_valor[2]])
    
    return [ True, True, 'booleano', 'fazerNada']

def obter_valor_lista(linha, logs):
    logs = '  ' + logs
    log(logs + 'Função Variavel lista: "{}"'.format(linha))

    # Ver se a variável está disponível

    teste = obter_valor_variavel(linha, logs)

    if teste[0] == False:
        return teste

    if teste[2] != 'lista':
        return[False, 'A variável "{}" não é uma lista.'.format(linha), 'string']

    return teste

def funcao_obter_valor_lista(linha, subcomando, logs):
    logs = '  ' + logs
    log(logs + 'Função Valor de lista: "{}", subcomandos: "{}"'.format(linha, subcomando))

    variavel = ''
    posicao = ''

    testa = verifica_se_tem(linha, subcomando, logs)

    if testa != []:
        variavel = linha[ : testa[0][0] ].strip()
        posicao = linha[ testa[0][1] : ].strip()

    # SE DER ERRO
    if variavel == '' or posicao == '':
        return [ False, 'Sem variavel passada','string','exibirNaTela']

    busca = abstrair_valor_linha(posicao, logs)
    if busca[0] == False:
        return [busca[0], busca[1], busca[2], 'exibirNaTela']

    try:
        posicao = int(busca[1])
    except:
        return [False, '\'{}\' não é um valor númerico'.format(busca[1]),'string', 'exibirNaTela']

    # Verifica se existe:
    variavel = variavel.strip()

    # Tentar obter o valor da lista
    teste = obter_valor_lista(variavel, logs)
    if teste[0] == False:
        return [teste[0], teste[1], teste[2], 'exibirNaTela']

    # Obtem os valores da lista
    resultado = teste[1]

    # Se estive fora do escopo
    if len(resultado) < posicao or posicao < 1:
        return [False, 'Posição \'{}\' está fora do escopo da lista {}'.format(posicao, resultado), 'exibirNaTela']

    return [True, resultado[posicao-1][0], resultado[posicao-1][1], 'fazerNada']

def funcao_tiver_na_lista(linha, logs):
    global dic_variaveis
    global dic_sub_com

    logs = '  ' + logs
    log(logs + 'Função tiver na lista: "{}"'.format(linha))

    valor = ''
    variavel = ''

    # "'olá' em nomes"
    for comando in dic_sub_com['tiverLista']:

        testa = verifica_se_tem(linha, comando[0], logs)
        if testa != []:

            valor = linha[ : testa[0][0] ].strip()
            variavel =  linha[ testa[0][1] : ].strip()
            break

    if variavel == '' or valor == '':
        return [False, 'É necessário passar um comando de referência, para indicar o que é valor e o que é variável', 'exibirNaTela']

    variavel = variavel.strip()

    teste = obter_valor_variavel(variavel, logs)

    if teste[0] == False:
        return [teste[0], teste[1], teste[2], 'exibirNaTela']

    if teste[2] != 'lista':
        return[False, 'A variável "{}" não é uma lista.'.format(linha), 'string', 'exibirNaTela']

    resultado = abstrair_valor_linha(valor, logs)
    if resultado[0] == False:
        return [resultado[0], resultado[1], resultado[2], 'exibirNaTela']

    if [resultado[1], resultado[2]] in dic_variaveis[variavel][0]:
        return [True, True, 'booleano', 'fazerNada']

    else:
        return [True, False, 'booleano', 'fazerNada']

def funcao_tamanho_da_lista(linha, logs):
    global dic_variaveis

    logs = '  ' + logs
    log(logs + 'Função obter o tamanho da lista: "{}"'.format(linha))

    linha = linha.strip()

    # Analisa se lista foi decarada e se é lista
    teste = obter_valor_lista(linha, logs)
    if teste[0] == False:
        return [teste[0], teste[1], teste[2], 'exibirNaTela']

    try:
        return [True, len(dic_variaveis[linha][0]), 'float', 'fazerNada']

    except Exception as erro:
        return [True, 'Erro ao obter o tamanho da lista. Erro: {}'.format(erro), 'string', 'exibirNaTela']

def funcao_remover_itens_na_lista(linha, logs):
    global dic_variaveis
    global dic_sub_com

    logs = '  ' + logs
    log(logs + 'Função remover itens da lista: "{}"'.format(linha))

    valor = ''
    variavel = ''

    for comando in dic_sub_com['RemoverItensListas']:

        testa = verifica_se_tem(linha, comando[0], logs)
        if testa != []:

            valor = linha[ : testa[0][0]].strip()
            variavel = linha[ testa[0][1] : ].strip()
            break

    if variavel == '' or valor == '':
        return [False, '2 É necessário passar um comando de referência, para indicar o que é valor e o que é variável. Como " Adicione 1 a lista de nomes ', 'exibirNaTela']

    variavel = variavel.strip()

    # Analisa se lista foi decarada e se é lista
    teste = obter_valor_lista(variavel, logs)
    if teste[0] == False:
        return [teste[0], teste[1], teste[2], 'exibirNaTela']

    resultado = abstrair_valor_linha(valor, logs)

    if resultado[0] == False:
        return [resultado[0], resultado[1], resultado[2], 'exibirNaTela']

    try:
        dic_variaveis[variavel][0].remove([resultado[1], resultado[2]]) 

    except Exception as erro:
        return [ False, '"{}" Não está na lista "{}"!'.format(resultado[1], variavel), 'string', 'exibirNaTela']

    return [True, None, 'vazio', 'fazerNada']

def funcao_adicionar_declarar_itens_na_lista(linha, logs):
    global dic_variaveis
    global dic_sub_com

    logs = '  ' + logs
    log(logs + 'funcao_adicionar_declarar_itens_na_lista: "{}"'.format(linha))

    variavel = ''
    resto = ''

    testa = verifica_se_tem(linha, ' na posicao ', logs)
    if testa != []:
        variavel = linha[ : testa[0][0] ].strip()
        resto = linha[ testa[0][1] : ].strip()

    if variavel == '' or resto == '':
        return [False, 'Sem comando de referência', 'string', 'exibirNaTela']

    testa = verifica_se_tem(resto, ' recebe ', logs)
    if testa != []:
        posicao = resto[ : testa[0][0]].strip()
        valor = resto[ testa[0][1] : ].strip()

    if posicao == '' or resto == '':
        return [False, 'Sem comando de referência 2', 'string', 'exibirNaTela']

    # VERIFICA SE A LISTA EXISTE
    listaExiste = obter_valor_lista(variavel, logs)
    if listaExiste[0] == False:
        return [listaExiste[0], listaExiste[1], listaExiste[2], 'exibirNaTela']

    # OBTEM O VALOR DA POSICAO
    obterValor = abstrair_valor_linha(posicao, logs)
    if obterValor[0] == False:
        return [obterValor[0], obterValor[0], obterValor[0], 'exibirNaTela']

    else:
        posicao = int(obterValor[1])

    # POSIÇÃO ESTÁ DENTRO DO INDICE
    if posicao > len(listaExiste[1]):
        return [False,'A posição {} é maior que a quantidade de itens da lista {}'.format(posicao,len(listaExiste[1]))]

    elif posicao < 1:
        return [False,'A posição {} não pode ser menor que zero'.format(posicao)]

    # OBTEM O VALOR DO VALOR
    obtemValorVariavel = abstrair_valor_linha(valor, logs)
    if obtemValorVariavel[0] == False:
        return [obtemValorVariavel[0], obtemValorVariavel[0], obtemValorVariavel[0], 'exibirNaTela']
    else:
        valor = obtemValorVariavel[1]

    dic_variaveis[variavel][0][ posicao - 1 ] = [obtemValorVariavel[1], obtemValorVariavel[2]]

    return [True, True, 'booleano','fazerNada']

def funcao_declarar_listas(linha, logs):
    global dic_variaveis
    logs = '  ' + logs
    log(logs + 'Função declarar listas: "{}"'.format(linha))


    variavel = ''
    itens = ''

    for comando in dic_sub_com['declaraListas']:
        testa = verifica_se_tem(linha, comando[0], logs)
        if testa != []:

            variavel = linha[ : testa[0][0] ].strip()
            itens = linha[ testa[0][1] : ].strip()
            break

    #     variavel)|        itens
    # linha 2 nomes|"Mariana", "Alexa", "Maria"
    if itens == '' or variavel == '':
        return [False, 'É necessário um comando de atribuição ao declar uma lista!', 'string', 'exibirNaTela']

    variavel = variavel.strip()

    teste = analisa_padrao_variavel(logs,variavel,'Lista ')
    if teste[1] != True:
        return [False, teste[1], teste[2], 'exibirNaTela']

    testa = verifica_se_tem(itens, ', ', logs)

    if testa != []:
        listaItens = []
        anterior = 0

        for valorItem in testa:
            if len(itens[anterior : valorItem[0]]) > 0:
                listaItens.append( itens[anterior : valorItem[0]] )

            anterior = valorItem[1] 

        if len(itens[anterior : ]) > 0:
            listaItens.append( itens[anterior : ] )

        listaItensDeclarar = []

        for item in listaItens:
            obterValor = abstrair_valor_linha(item, logs)

            if obterValor[0] == False:
                return [obterValor[0], obterValor[1], obterValor[2], 'exibirNaTela']

            listaItensDeclarar.append([obterValor[1], obterValor[2]])

        dic_variaveis[variavel] = [listaItensDeclarar, 'lista']
        # {'nomes': [[['', 'string'], ['', 'string']], 'lista']}
        return [True, None, 'vazio', 'fazerNada']

    else:
        obterValor = abstrair_valor_linha(itens, logs)
        if obterValor[0] == False:
            return [obterValor[0], obterValor[1], obterValor[2], 'exibirNaTela']

        dic_variaveis[variavel] = [[obterValor[1], obterValor[2]], 'lista']
        return [True, None, 'vazio', 'fazerNada']

def pressionou_enter(event=None):
    global esperar_pressionar_enter
    if esperar_pressionar_enter:
        esperar_pressionar_enter = False

def funcao_digitado(linha, logs):
    global tx_terminal
    global esperar_pressionar_enter
    global aconteceu_erro

    logs = '  ' + logs
    log(logs + 'Função digitado: "{}"'.format(linha))

    textoOriginal = len(tx_terminal.get(1.0, END))

    esperar_pressionar_enter = True

    while esperar_pressionar_enter:
        print('lendo', aconteceu_erro)
        sleep(0.01)
        if aconteceu_erro:
            print("Houve erros")
            return [False, "Interrompido","string","exibirNaTela"]

        else:
            tx_terminal.update()

    print("Sem erros")
    digitado = tx_terminal.get(1.0, END)
    digitado = digitado[textoOriginal-1:-2]

    # SE FOR NUMÉRICO
    if ' numero ' in linha:
        try:
            float(digitado)
        except:
            return[False, "Você disse que queria digitar um número, mas digitou um texto '{}'".format(digitado), 'string', 'fazerNada']
        else:
            return [True, float(digitado), 'float', 'fazerNada']
    else:
        return [True, digitado, 'string', 'fazerNada']

def funcao_limpar_tela(logs):
    global tx_terminal

    logs = '  ' + logs
    log(logs + 'Limpatela ativado!')

    tx_terminal.delete(1.0, END)
    return [True, None, 'vazio','fazerNada']

# repita 10 vezes \n{\nmostre 'oi'\n}
def funcao_repetir(linha, logs):

    logs = '  ' + logs
    log(logs + 'funcao repetir: "{}"'.format(linha))

    # Remoção de lixo
    linha = linha.replace('vezes', '')
    linha = linha.replace('vez', '')

    # Eliminação de espaços laterais
    linha = linha.strip()

    # Obter o valor da variável
    linha = abstrair_valor_linha(linha, logs)

    # Deu erro?
    if linha[0] == False:
        return [linha[0], linha[1], linha[2], 'exibirNaTela']

    if linha[2] != 'float':
        return[False, 'Você precisa passar um número inteiro para usar a função repetir: "{}"'.format(linha), 'string', 'exibirNaTela']

    # É inteiro
    try:
        int(linha[1])
    except:
        return [False, "Para usar a função repetir, você precisa passar um número inteiro. Você passou '{}'".format(linha[1]), 'string', 'exibirNaTela']
    else:
        funcao_repita = int(linha[1])

        # Não houve erros e é para repetir
        return [True, funcao_repita, 'float', 'declararLoopRepetir']

# numero aleatório entre 10 e 20
def funcao_numero_aleatorio(linha, logs):
    logs = '  ' + logs
    log(logs + 'funcao aleatório: {}'.format(linha))

    # Remova os espaços da linha
    linha = linha.strip()

    # Se tiver  e que indica intervalo
    testa = verifica_se_tem(linha, ' e ', logs)
    if testa != []:

        # Obtenção dos dois valores
        num1 = linha[ : testa[0][0]]
        num2 = linha[ testa[0][1] : ]
 
        # Obtendo ambos os valores
        num1 = abstrair_valor_linha(num1, logs)
        # Se deu para obter o valor do primeiro
        if num1[0] == False:
            return [num1[0], num1[1], num1[2], 'exibirNaTela']

        num2 = abstrair_valor_linha(num2, logs)
        # Se deu erro para obter o valor do segundo
        if num2[0] == False:
            return [num2[0], num2[1], num2[2], 'exibirNaTela']

        # Se o primeiro for numéricos
        try:
            int(num1[1])
        except:
            return [False, "O valor 1 não é numérico", 'string', 'exibirNaTela']
 
        # Se o segundo for numéricos
        try:
            int(num2[1])
        except:
            return [False, "O valor 2 não é numérico", 'string', 'exibirNaTela']

        n1 = int(num1[1])
        n2 = int(num2[1])

        if n1 == n2:
            return [False, "O valor 1 e o valor 2 da função aleatório tem que ser diferentes", 'string', 'exibirNaTela']
        elif n1 > n2:
            return [False, "O valor 1 é maior que o valor 2, o valor 1 tem que ser maior", 'string', 'exibirNaTela']

        return [True, randint(n1, n2), 'float', 'fazerNada']

    else:
        return [False, "Erro, você precisa definir o segundo valor, tipo 'entre 2 e 5'!", 'string', 'exibirNaTela']

# calcMedia passando parametros nota1, nota2
def funcao_executar_funcoes(linha, logs):
    global dic_funcoes

    logs = '  ' + logs
    log(logs + 'Executar funções: {}'.format(linha))

    # ATUMAR AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    chamarFuncoes    = ['passando parametros', 'passando parametro', 'parametros', 'parametro', 'passando']
 
    nomeDaFuncao = ''
    parametros = None

    for comando in chamarFuncoes:

        testa = verifica_se_tem(linha, comando, logs)
        if testa != []:
            nomeDaFuncao = linha[ : testa[0][0] ].strip()
            parametros = linha[testa[0][1] : ].strip()
            break

    if nomeDaFuncao == '':
        nomeDaFuncao = linha

    try:
        dic_funcoes[nomeDaFuncao]
    except:
        return [False, "A função '{}' não existe".format(nomeDaFuncao), 'string', 'exibirNaTela']
    else:

        testa = verifica_se_tem(parametros, ', ', logs)
        if testa != []:
            anterior = 0
            listaDeParametros = []

            for valorItem in testa:
                if len(parametros[anterior : valorItem[0]]) > 0:
                    listaDeParametros.append( parametros[anterior : valorItem[0]] )
                    anterior = valorItem[1]

            if len(parametros[anterior : ]) > 0:
                listaDeParametros.append( parametros[anterior : ] )

            listaFinalDeParametros = []

            for parametro in listaDeParametros:
                listaFinalDeParametros.append(parametro.strip())

            # Se tiver a mesma quantiade de parametros
            if len(dic_funcoes[nomeDaFuncao][0]) == len(listaFinalDeParametros):

                for parametroDeclarar in range(len(dic_funcoes[nomeDaFuncao][0])):
                    resultado = funcao_fazer_atribuicao('{} recebe {} '.format(dic_funcoes[nomeDaFuncao][0][parametroDeclarar], listaFinalDeParametros[parametroDeclarar]), 'recebe', logs)

                    if resultado[0] == False:
                        return [resultado[0], resultado[1], resultado[2], 'exibirNaTela']
            else:
                return [False, "A função '{}' tem {} parametros, mas você passou {} parametros!".format(nomeDaFuncao, len(dic_funcoes[nomeDaFuncao][0]), len(listaFinalDeParametros)), 'string', 'fazerNada']

        # Se tiver só um parametro
        elif parametros != None:

            if len(dic_funcoes[nomeDaFuncao][0]) == 1:
                resultado = funcao_fazer_atribuicao(
                    '{} recebe {} '.format(
                        dic_funcoes[nomeDaFuncao][0], parametros), 'recebe', logs)

                if resultado[0] == False:
                    return [resultado[0], resultado[1], resultado[2], 'exibirNaTela']
            else:
                return [False, "A função '{}' tem {} parametros, mas você passou 1 parametro!".format(nomeDaFuncao, len(dic_funcoes[nomeDaFuncao][0])), 'string', 'exibirNaTela']

        resultadoOrquestrador = orquestrador_interpretador(
            dic_funcoes[nomeDaFuncao][1])

        if resultadoOrquestrador[0] == False:
            return [resultadoOrquestrador[0], resultadoOrquestrador[1], resultadoOrquestrador[2], 'exibirNaTela']

        return [True, None, 'vazio', 'fazerNada']

# FUNCAO CALCULAMEDIA RECEBE PARAMENTOS NOTA1, NOTA2
def funcao_declarar_funcao(linha, logs):
    global funcao_em_analise

    logs = '  ' + logs
    log(logs + 'Declarar funcoes: {}'.format(linha))
    recebeParametros = ['recebe parametros', 'recebe']

    for comando in recebeParametros:

        testa = verifica_se_tem(linha, comando, logs)
        if testa != []:

            lista = []
            anterior = 0
            for valorItem in testa:
                if len(linha[ anterior : valorItem[0] ] ) > 0:
                    lista.append(linha[anterior : valorItem[0]])
                anterior = valorItem[1]

            if len( linha[ anterior: ] ) > 0:
                lista.append(linha[anterior : ])

            nomeDaFuncao = lista[0].strip() 
            teste = analisa_padrao_variavel(logs,nomeDaFuncao,'Função')

            if teste[1] != True:
                return [False, teste[1], teste[2], 'exibirNaTela']

            parametros = lista[1].strip()


            testa = verifica_se_tem(parametros, ', ', logs)
            if testa != []:
                listaDeParametros = []
                anterior = 0
                for valorItem in testa:
                    if parametros[anterior : valorItem[0]]:
                        listaDeParametros.append(parametros[ anterior : valorItem[0]])
                    anterior = valorItem[1]

                if len( parametros[anterior : ]) > 0:
                    listaDeParametros.append(parametros[ anterior : ])

                listaFinalDeParametros = []
                for parametro in listaDeParametros:
                    listaFinalDeParametros.append(parametro.strip())

                    teste = analisa_padrao_variavel(logs,parametro.strip(),'Parametro ')
                    if teste[1] != True:
                        return [False, teste[1], teste[2], 'exibirNaTela']

                dic_funcoes[nomeDaFuncao] = [listaFinalDeParametros, 'bloco']

            else:
                teste = analisa_padrao_variavel(logs,parametros,'Parametro ')
                if teste[1] != True:
                    return [False, teste[1], teste[2], 'exibirNaTela']

                dic_funcoes[nomeDaFuncao] = [parametros, 'bloco']

            funcao_em_analise = nomeDaFuncao

            return [True, True, 'booleano', 'declararFuncao']
    
    dic_funcoes[linha.strip()] = ['', 'bloco']
    funcao_em_analise = linha.strip()

    return [True, True, 'booleano', 'declararFuncao']

def funcao_exibir(linha, logs):
    logs = '  ' + logs
    log(logs + 'funcao exibição: {}'.format(linha))

    codigo = linha.strip()
    resultado = abstrair_valor_linha(codigo, logs)
    if resultado[0] == False:
        return [resultado[0], resultado[1], resultado[2], 'exibirNaTela']

    lista = []
    # Se for lista
    if resultado[2] == 'lista':
        # Ande pelos valores
        for value in resultado[1]:
            lista.append(value[0])
    else:
        lista = resultado[1]

    ''' | sucesso | saida | tipoSaida | ordem | '''
    return [resultado[0],lista, resultado[2],'exibirNaTela']

def funcao_exibir_na_linha(linha, logs):
    logs = '  ' + logs
    log(logs + 'Função exibir nessa linha ativada'.format(linha))
    codigo = linha.strip()
    resultado = abstrair_valor_linha(codigo, logs)
    if resultado[0] == False:
        return resultado

    lista = []
    ############################################################################
    # EROOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO POSSIVEL
    # Se for lista
    if resultado[2] == 'lista':
        # Ande pelos valores
        for value in resultado[1]:
            lista.append(value[0])
    else:
        lista = resultado[1]

    ''' | sucesso | saida | tipoSaida | ordem | '''
    return [resultado[0], ':nessaLinha:' + str(lista), resultado[2], 'exibirNaTela']

def funcao_tempo(codigo, logs):
    global dic_sub_com

    logs = '  ' + logs
    log(logs + 'Função tempo: {}'.format(codigo))
    codigo = codigo.strip()
   
    for comando in  dic_sub_com['esperaEm']:

        if len(comando[0]) < len(codigo):

            if comando[0] == codigo[len(codigo)-len(comando[0]):]:

                resultado = abstrair_valor_linha(
                    codigo[:len(codigo)-len(comando[0])], logs)

                if resultado != False:

                    if comando[0] == " segundos" or comando[0] == " s" or comando[0] == " segundo":
                        sleep(resultado[1])
                        return [True, None, 'vazio', 'fazerNada']

                    elif comando[0] == " milisegundos" or comando[0] == " ms" or comando[0] == "milisegundo":
                        sleep(resultado[1]/1000)
                        return [True, None, 'vazio', 'fazerNada']

                else:
                    return [False, 'Erro ao obter um valor no tempo', 'string', 'exibirNaTela']

    return [True, None, 'vazio', 'fazerNada']

# A STRING DEVE ESTAR CRUA
def obter_valor_string(string, logs):    
    logs = '  ' + logs
    log(logs + 'Obter valor de uma string: {}'.format(string))

    valorFinal = ''
    anterior = 0

    for valor in finditer("""\"[^"]*\"""", string):

        abstrair = abstrair_valor_linha(
            string[anterior:valor.start()], logs)
        if abstrair[0] == False:
            return abstrair

        valorFinal = valorFinal + str(
            abstrair[1]) + string[valor.start()+1:valor.end()-1]
        anterior = valor.end()

    # Capturar o resto        
    abstrair = abstrair_valor_linha(string[anterior:], logs)
    if abstrair[0] == False:
        return abstrair

    valorFinal = valorFinal + str(abstrair[1])

    return [True, valorFinal, 'string']

def localiza_transforma_variavel(linha, logs):
    logs = '  ' + logs
    log(logs + 'Encontrar e transformar dic_variaveis: {}'.format(linha))
    # Abstração de variáveis
    anterior = 0
    normalizacao = 0
    linha_base = linha
    tipos_obtidos = []

    for valor in finditer(' ', linha_base):
        palavra = linha[anterior : valor.start() + normalizacao]

        if palavra.isalnum() and palavra[0].isalpha():

            variavelDessaVez = abstrair_valor_linha(palavra, logs)

            if variavelDessaVez[0] == False:
                return variavelDessaVez

            tipos_obtidos.append(variavelDessaVez[2])
            linha = str(linha[:anterior]) + str(
                variavelDessaVez[1]) + str(
                    linha[valor.start() + normalizacao:]) 
            
            if len(palavra) < len(str(variavelDessaVez[1])):
                normalizacao += (len(str(variavelDessaVez[1])) - len(palavra))

            elif len(palavra) > len(str(variavelDessaVez[1])):
                normalizacao -= (len(palavra) - len(str(variavelDessaVez[1])))

        anterior = valor.end() + normalizacao

    return [True, linha, 'string']

# A string deve estar crua
def fazer_contas(linha, logs):
    logs = '  ' + logs
    log(logs + 'Fazer contas: {}'.format(linha))

    # Do maior para o menor
    linha = linha.replace(' multiplicado por ', ' * ')
    linha = linha.replace(' dividido por ', ' / ')
    linha = linha.replace(' multiplique ', ' * ')
    linha = linha.replace(' elevado por ', ' ** ')
    linha = linha.replace(' elevado a ', ' ** ')    
    linha = linha.replace(' elevado ', ' ** ')
    linha = linha.replace(' divide ', ' / ')
    linha = linha.replace(' mais ', ' + ')
    linha = linha.replace(' menos ', ' - ')

    if '"' in linha:
        # Não mude esse texto
        return [False, "Isso é uma string", 'string']

    # Removendo os espaços laterais
    linha = ' {} '.format(linha)

    simbolosEspeciais = ['+', '-', '*', '/', '%', '(', ')']
    qtd_simbolos_especiais = 0

    # Deixando todos os itens especiais com espaço em relação aos valores
    for iten in simbolosEspeciais:

        if iten in linha:
            qtd_simbolos_especiais += 1

        linha = linha.replace(iten, ' {} '.format(iten))

    # Se não tiver nenhuma operação
    if qtd_simbolos_especiais == 0:
        return [False, "Não foi possivel realizar a conta, porque não tem nenhum valor aqui. ", 'string']

    # Correção do potenciação
    linha = linha.replace('*  *', '**')
    linha = linha.replace('< =', '<=')
    linha = linha.replace('> =', '>=')
    linha = linha.replace("! =", '!=')

    linha = localiza_transforma_variavel(linha, logs)
    if linha[0] == False:
        return linha

    for caractere in linha[1]:
        if str(caractere).isalpha():
            return [False, 'não é possível fazer contas com strings: ' + str(linha[1]), 'string']

    # Tente fazer uma conta com isso
    try:
        resutadoFinal = eval(linha[1])
    except Exception as erro:
        return [False, "Não foi possivel realizar a conta |{}|".format(linha[1]), 'string']
    else:
        return [True, resutadoFinal, 'float']

def obter_valor_variavel(variavel, logs):
    logs = '  ' + logs
    log(logs + 'Obter valor da variável: "{}"'.format(variavel))

    global dic_variaveis
    global dic_com
    variavel = variavel.strip()

    variavel = variavel.replace('\n', '')

    try:
        dic_variaveis[variavel]
    except:
        return [False, "Você não definiu a variável '{}'".format(variavel), 'string']
    else:
        return [True, dic_variaveis[variavel][0], dic_variaveis[variavel][1]]

def comandos_uso_geral(possivelVariavel, logs):
    logs = '  ' + logs
    possivelVariavel = str(possivelVariavel).strip()
    log(logs + '>>Obter comando digitado ou aleatório: {}'.format(possivelVariavel))

    for comandoDigitado in dic_com['digitado']:

        if len(comandoDigitado[0]) <= len(possivelVariavel):

            if possivelVariavel == comandoDigitado[0]:
                resultado = funcao_digitado(comandoDigitado[0], logs)
                return resultado

    for comandoAleatorio in dic_com['aleatorio']:

        if len(comandoAleatorio[0]) <= len(possivelVariavel):

            if possivelVariavel[0:len(comandoAleatorio[0])] == comandoAleatorio[0]:
                resultado = funcao_numero_aleatorio(
                    possivelVariavel[len(comandoAleatorio[0]):], logs)
                return resultado

    for comando in dic_sub_com['acesarListas']:
        testa2 = verifica_se_tem(possivelVariavel, comando[0], logs)
        if testa2 != []:
            teste = funcao_obter_valor_lista(possivelVariavel, comando[0], logs)
            return teste

    resultado = tiver_valor_lista(possivelVariavel,logs)
    if resultado[0] == True and resultado[1] != None:
        return [True, resultado[1],resultado[2]]

    for comando in dic_com['tamanhoDaLista']:

        testa = verifica_se_tem(possivelVariavel, comando[0], logs)
        if testa != []:
            if comando[0] == possivelVariavel[0:len(comando[0])]:
                return funcao_tamanho_da_lista(possivelVariavel[len(comando[0]):], logs)

    # Não é nem um e nem o outro                
    return [True, None, 'vazio']

# Os valores aqui ainda estão crus, como: mostre "oi", 2 + 2
def abstrair_valor_linha(possivelVariavel, logs):
    logs = '  ' + logs
    log(logs + 'Abstrar valor de uma linha inteira com possivelVariavel: "{}"'.format(possivelVariavel))
    possivelVariavel = str(possivelVariavel).strip()

    if possivelVariavel == 'True':
        return [True, 'True', 'booleano']

    if possivelVariavel == 'False':
        return [True, 'False', 'booleano']

    if possivelVariavel == '':
        return [True, possivelVariavel, 'string']

    # Caso existam contas entre strings ( Formatação )
    if possivelVariavel[0] == ',':
        possivelVariavel = possivelVariavel[1:]

    # Caso existam contas entre strings ( Formatação )
    if len(possivelVariavel) > 1:

        if possivelVariavel[-1] == ',':
            possivelVariavel = possivelVariavel[0:len(possivelVariavel)-1]

    possivelVariavel = possivelVariavel.strip()

    # Se tiver virgulas entre os valores
    testa = verifica_se_tem(possivelVariavel, ",", logs)
    if testa != []:

        listaLinhas = [ possivelVariavel[ : testa[0][0] ],  possivelVariavel[testa[0][1] : ]]
        listaValores = ''
        for linha in listaLinhas:
            valor = abstrair_valor_linha(linha, logs)
            if valor[0] == False:
                return valor

            listaValores += str(valor[1])

        return [True, listaValores, "string"]

    if possivelVariavel == '':
        return [True, possivelVariavel, 'string']

    # ========== FAZER CONTAS  ================== #
    resultado = fazer_contas(possivelVariavel, logs)
    if resultado[0] == True:
        return resultado
    # ========== FAZER CONTAS  ================== #

    # ========== COMANDOS DIVERSOS  ================== #
    resultado = comandos_uso_geral(possivelVariavel, logs)

    if resultado[0] == True and resultado[1] != None:
        return resultado

    # Era um digitado ou aleatório, mas deu errado
    elif resultado[0] == False:
        return resultado

    # =========  COMANDOS DIVERSOS  =========== #
    testa = verifica_se_tem(possivelVariavel, '"', logs)
    if testa != []:
        return obter_valor_string(possivelVariavel, logs)

    try:
        float(possivelVariavel)
    except:
        return obter_valor_variavel(possivelVariavel, logs)
    else:
        return [True, float(possivelVariavel), 'float']

def analisa_padrao_variavel(logs,variavelAnalise, msg):
    variavel = variavelAnalise
    logs = '  ' + logs

    variavel = variavel.replace('_','a')
    variavel = variavel.lower()

    if not variavel[0].isalpha():
        return [True, msg + ' devem começar obrigatóriamente com uma letra: \'{}\' não se encaixa nessa regra'.format(variavelAnalise), 'sring']

    if not variavel.isalnum():
        return [True, msg + ' devem conter apenas letras, números ou _: \'{}\' não se encaixa nessa regra'.format(variavelAnalise), 'sring']

    return [True,True,'booleano']

def funcao_fazer_atribuicao(linha, comando, logs):
    global dic_variaveis

    logs = '  ' + logs
    log(logs + 'Função atribuição: {}'.format(linha))

    testa = verifica_se_tem(linha, comando, logs)
    if testa != []:

        variavel = linha[ : testa[0][0] ].strip()
        valor = linha[ testa[0][1] : ].strip()

    if variavel == '' or valor == '':
        return [False, 'É necessario cum comando de atribuição', 'string', 'exibirNaTela']

    teste = analisa_padrao_variavel(logs,variavel,'Variáveis')
    if teste[1] != True:
        return [False, teste[1], teste[2], 'exibirNaTela']

    valor = valor.replace('\n', '')
    valor = valor.strip()

    resultado = abstrair_valor_linha(valor, logs)
    if resultado[0] == False:
        return resultado

    if resultado[0] == True:
        dic_variaveis[variavel] = [resultado[1], resultado[2]]

        return [True, None, 'vazio', 'fazerNada']

    return [ resultado[0], resultado[1], resultado[2], 'fazerNada']

def funcao_loops_enquanto(linha, logs):
    logs = '  ' + logs
    log(logs + 'Função loops enquanto: {}'.format(linha))

    resultado = funcao_condicional(linha, logs)

    return [resultado[0], resultado[1], resultado[2], 'declararLoop']

def tiver_valor_lista(linha,logs):
    linha = linha.strip()
    logs = '  ' + logs
    log(logs + 'Função condicional: {}'.format(linha))

    for comando in dic_com['tiverLista']:

        if comando[0] in linha:
            if comando[0] == linha[0:len(comando[0])]:
                return funcao_tiver_na_lista(linha[len(comando[0]):], logs)

    return [True,None,'booleano']

def funcao_condicional(linha, logs):
    ''' 3 for maior que 20 ou 5 for menor que 1 '''
    logs = '  ' + logs
    log(logs + 'Função condicional: {}'.format(linha))

    # Padronização geral
    linha = linha.replace(' for maior ou igual a ', ' >= ')
    linha = linha.replace(' for menor ou igual a ', ' <= ')
    linha = linha.replace(' for diferente de ', ' != ')
    linha = linha.replace(' for maior que ', ' > ')
    linha = linha.replace(' for menor que ', ' < ')
    linha = linha.replace(' for igual a ', ' == ')
    linha = linha.replace(' e ' , '  and  ')
    linha = linha.replace(' && ', '  and  ')
    linha = linha.replace(' ou ', '  or  ')
    linha = linha.replace(' || ', '  or  ')

    # Adicionando um espaço
    linha = ' ' + str(linha) + ' '

    # Todos os caracteres especiais de 
    simbolosEspeciais = ['>=', '<=', '!=', '>', '<', '==', '(', ')',' and ', ' or ',' tiver ']
 
    # Quantidade de simbolos localizados
    qtd_simbolos_especiais = 0

    # Deixando todos os itens especiais com espaço em relação aos valores
    for item in simbolosEspeciais:

        # Se tiver o simbolo especial na linha, some +1
        if item in linha:

            # Aumente a quantidade de simbolos registrados
            qtd_simbolos_especiais += 1

            # Adiciona espaço para cada simbolos
            linha = linha.replace(item, '  {}  '.format(item))

    # Se não tiver nenhuma operação a fazer
    if qtd_simbolos_especiais == 0:
        return [False, "Não foi possivel realizar a condição por que não tem nenhum simbolo condicional", 'string', 'exibirNaTela']

    # Coreção de bugs ao usar o recurso de deixar espaços
    linha = linha.replace('* *', '**')
    linha = linha.replace('> =', '>=')
    linha = linha.replace('< =', '<=')
    linha = linha.replace('! =', '!=')
    linha = linha.replace('   tiver   ',' tiver ')

    # Remoçãp das linhas laterais
    linha = linha.strip()

    # Obter valor de cada valor
    simbolosArrumados = [' >= ', ' <= ', ' != ', ' > ', ' < ', ' == ', ' ( ', ' ) ',' and ', ' or ']

    # Marcar os simbolos para correta captura do regex
    for simbolo in range(len(simbolosArrumados)):

        # Marque os sinais especiais
        linha = linha.replace(
            simbolosArrumados[simbolo],'_._' + simbolosArrumados[simbolo] + '_._')
 
    linha = linha.replace('_._ < _._ =','_._ <= _._')
    linha = linha.replace('_._ > _._ =','_._ >= _._')

    # Usando Regex para isolar os simbolos
    anterior = 0
    final = ''

    # Obter os valores fora dos simbolos marcados
    for item in finditer("_\\._[^_]*_\\._", linha):

        # Abstrai um valor qual
        resultado = abstrair_valor_linha(
            linha[anterior:item.start()],logs)

        if resultado[0] == False:
            return [resultado[0], resultado[1], resultado[2], 'exibirNaTela']

        saida = resultado[1]

        # Marcar strings
        if resultado[2] == 'string':
            saida = '"' + resultado[1] + '"'

        # Reover marcadores de simbolos
        final += str(saida) + linha[item.start() + 3:item.end() - 3]

        anterior = item.end()

    boolTemTiverLista = False
    resultado = tiver_valor_lista(linha[anterior:].strip(), logs)

    if resultado[0] == False:
        return [resultado[0], resultado[1], resultado[2], 'exibirNaTela']

    if resultado[2] == 'booleano':

        if resultado[1] == 'sim':
            final += ' True '
            boolTemTiverLista = True

        elif resultado[1] == 'nao':
            final += ' False '
            boolTemTiverLista = True

    if not boolTemTiverLista:

        resultado = abstrair_valor_linha(linha[anterior:], logs)
        if resultado[0] == False:
            return [resultado[0], resultado[1], resultado[2], 'exibirNaTela']

        # Obter ultima string
        saida = resultado[1]
        if resultado[2] == 'string':
            saida = '"' + resultado[1] + '"'

        # Finalizar nova linha
        final += str(saida)

    # Tente fazer a condição com isso
    try:
        resutadoFinal = eval(final)

    except Exception as erro:
        return [False, "Não foi possivel realizar a condicao |{}|".format(final), 'string', 'exibirNaTela']

    else:
        return [True, resutadoFinal, 'booleano', 'fazerNada']

def modoFullScreen(event=None):
    global bool_tela_em_fullscreen

    if bool_tela_em_fullscreen:
        bool_tela_em_fullscreen = False

    else:
        bool_tela_em_fullscreen = True

    tela.attributes("-fullscreen", bool_tela_em_fullscreen)

def trocar_de_tela(fechar, carregar):
    fechar.grid_forget()
    carregar.grid(row=1, column=1, sticky=NSEW)

def on_closing(event=None):
    global top_janela_terminal
    global aconteceu_erro
    global numeros_thread_interpretador

    aconteceu_erro = True

    while numeros_thread_interpretador != 0:
        tela.update()
        sleep(0.01)
        print("Tentando para interpretador: ",numeros_thread_interpretador)

    top_janela_terminal.destroy()
    print('Fechou!')

def inicializador_terminal():
    global tx_terminal
    global top_janela_terminal

    top_janela_terminal = Toplevel(tela)
    top_janela_terminal.protocol("WM_DELETE_WINDOW", on_closing)
    top_janela_terminal.grid_columnconfigure(1, weight=1)
    top_janela_terminal.rowconfigure(1, weight=1)
    top_janela_terminal.geometry("720x450+150+150")

    tx_terminal = Text(top_janela_terminal)
    try:
        # Se ainda não estava carregado
        tx_terminal.configure(dic_design["tx_terminal"])
    except Exception as erro:
        print("Erro ao configurar os temas ao iniciar o terminal: ", erro)

    tx_terminal.bind('<Return>', lambda event:pressionou_enter(event))
    tx_terminal.focus_force()
    tx_terminal.grid(row=1, column=1, sticky=NSEW)

def atualizarListaDeScripts():
    for file in listdir('scripts/'):
        if len(file) > 5:       
            if file[-3:] == 'fyn':
                menu_arquivo_cascate.add_command(
                    label=file,command= lambda link = file: abrirArquivo(
                        'scripts/' + str(file)))

def atualizarListaTemas():
    for file in listdir('temas/'):
        if len(file) > 11:       
            if file[-10:] == 'theme.json':
                menu_interface_cascate_temas.add_command(
                    label=file,
                    command= lambda link = file: atualizaInterface(
                        'tema', str(link)))

def atualizarListasintaxe():
    for file in listdir('temas/'):
        if len(file) > 13:
            if file[-12:] == 'sintaxe.json':
                menu_interface_cascate_sintaxe.add_command(
                    label=file,
                    command= lambda link = file: atualizaInterface(
                        'sintaxe', str(link)) )

def atualizarListasfontes():
    fontes=list(font.families())
    fontes.sort()
    for fonte in fontes:
        menu_interface_cascate_fontes.add_command(
            label=fonte)

def atualizaInterface(alteracao, novo):
    global tela
    global tx_codificacao
    global dic_sub_com
    global dic_com
    global dic_design
    global cor_da_sintaxe

    try:
        with open('configuracoes.json') as json_file:
            configArquivoJson = load(json_file)

            configArquivoJson[alteracao] = novo
            configArquivoJson = str(configArquivoJson).replace('\'','\"')

        file = open('configuracoes.json','w')
        file.write(str(configArquivoJson))
        file.close()

    except Exception as e:
        return [None,'Erro ao atualizar o arquivo \'configuracoes.json\'. Sem esse arquivo, não é possível atualizar os temas']

    dic_sub_com, dic_com, dic_design, cor_da_sintaxe = atualiza_configuracoes_temas()
    try:
        atualiza_design_interface()
        atualiza_cor_sintaxe()
    except Exception as erro:
        print('ERRO: ', erro)
    else:
        print('Temas atualizados')

    tela.update()
    tx_codificacao.update()

def atualiza_design_interface():
    try:
        menu_interface_cascate_sintaxe.configure(dic_design["cor_menu"])
        menu_interface_cascate_temas.configure(dic_design["cor_menu"])
        menu_interface_cascate_fontes.configure(dic_design["cor_menu"])
        fr_opcoes_rapidas.configure(dic_design["fr_opcoes_rapidas"])
        menu_arquivo_cascate.configure(dic_design["cor_menu"])
        tx_codificacao.configure(dic_design["tx_codificacao"])
        menu_ferramentas.configure(dic_design["cor_menu"])
        menu_interface.configure(dic_design["cor_menu"])
        menu_localizar.configure(dic_design["cor_menu"])
        menu_executar.configure(dic_design["cor_menu"])
        menu_arquivo.configure(dic_design["cor_menu"])
        menu_editar.configure(dic_design["cor_menu"])
        menu_barra.configure(dic_design["cor_menu"])
        menu_ajuda.configure(dic_design["cor_menu"])
        menu_sobre.configure(dic_design["cor_menu"])
        menu_barra.configure(dic_design["cor_menu"])
        lb_linhas.configure(dic_design["lb_linhas"])

        scrollbar_text.configure(dic_design['scrollbar_text'])

        btn_salva.configure(dic_design["dicBtnMenus"])
        btn_corrige.configure(dic_design["dicBtnMenus"])
        btn_break.configure(dic_design["dicBtnMenus"])
        btn_play.configure(dic_design["dicBtnMenus"])
        btn_play_break_point.configure(dic_design["dicBtnMenus"])
        btn_desfazer.configure(dic_design["dicBtnMenus"])
        btn_redesfazer.configure(dic_design["dicBtnMenus"])
        btn_comentar.configure(dic_design["dicBtnMenus"])
        btn_idioma.configure(dic_design["dicBtnMenus"])
        btn_ajuda.configure(dic_design["dicBtnMenus"])
        btn_pesquisar.configure(dic_design["dicBtnMenus"])

    except Exception as erro:
        print('Erro ao atualizar o design da interface, erro: ',erro)

def configuracoes(ev):
    global altura_widget
    global lb_linhas
    global posCorrente
    global posAbsuluta

    if ev != None:
        altura_widget = int( ev.height / 24 )

    add_linha = ''

    qtdLinhas = tx_codificacao.get(1.0, 'end').count('\n')
    #print('Quantidade para : ' + str(qtdLinhas))
    #print('Atualizadoo para: ' + str(altura_widget))

    ate = qtdLinhas
    inicio = 0

    for linha in range(inicio, ate):
        add_linha = add_linha + str(linha) + '\n'

    lb_linhas.config(state=NORMAL)
    lb_linhas.delete(1.0, END)
    lb_linhas.insert(1.0, add_linha[:-1])
    #print('------------------')
    #print('altura:',altura_widget)
    #print('posAbs:',posAbsuluta)
    #print('posCor:',posCorrente)
    #print('------------------')
    
    lb_linhas.see('{}.0'.format( posCorrente + altura_widget) )
    #print('00000000000000000000')
    lb_linhas.config(state=DISABLED)

def obterPosicaoDoCursor(event=None):
    global tx_codificacao
    global posCorrente
    global posAbsuluta

    numPosicao = str(tx_codificacao.index(INSERT)) # Obter posicao
    posCorrente = int(float(tx_codificacao.index(CURRENT)))

    if '.' not in numPosicao:
        numPosicao = numPosicao + '.0'

    linha, coluna = numPosicao.split('.')
    #print(tx_codificacao.get('{}.{}'.format( int(linha), int(coluna)-1 )))
    posAbsuluta = int(linha)

    configuracoes(ev = None)

tela = Tk()
tela.title('Linguagem feynman')
tela.configure(bg='#393944')
tela.rowconfigure(2, weight=1)
tela.geometry("1100x600+100+100")
tela.grid_columnconfigure(1, weight=1)
#tela.attributes('-fullscreen', True)
tela.bind('<F11>', lambda event: modoFullScreen(event))
tela.bind('<F5>', lambda event: inicializador_orquestrador_interpretador(event))
tela.bind('<Control-s>', lambda event: salvarArquivo(event))
tela.bind('<Control-o>', lambda event: abrirArquivoDialog(event))
tela.bind('<Control-S>', lambda event: salvarArquivoComoDialog(event))

try:
    imgicon = PhotoImage(file='icone.png')
    tela.call('wm', 'iconphoto',tela._w, imgicon)  
except:
    pass

menu_barra = Menu(tela, tearoff = False)
tela.config(menu=menu_barra)

menu_ferramentas = Menu(menu_barra, tearoff = False)
menu_interface = Menu(menu_barra, tearoff = False)
menu_localizar = Menu(menu_barra, tearoff = False)
menu_executar = Menu(menu_barra, tearoff = False)
menu_arquivo = Menu(menu_barra, tearoff = False)
menu_editar = Menu(menu_barra, tearoff = False)
menu_ajuda = Menu(menu_barra, tearoff = False)
menu_sobre = Menu(menu_barra, tearoff = False)

menu_barra.add_cascade(label='Arquivo'   , menu=menu_arquivo)
menu_barra.add_cascade(label='Executar'  , menu=menu_executar)
menu_barra.add_cascade(label='Localizar' , menu=menu_localizar)
menu_barra.add_cascade(label='Interface' , menu=menu_interface)
menu_barra.add_cascade(label='Ajuda'     , menu=menu_ajuda)
menu_barra.add_cascade(label='sobre'     , menu=menu_sobre)

# ARQUIVO
menu_arquivo_cascate = Menu(menu_arquivo, tearoff = False)
menu_arquivo.add_command(label='Abrir arquivo (Ctrl+O)', command=abrirArquivoDialog)
menu_arquivo.add_command(label='Nova Guia (Ctrl-N)')
menu_arquivo.add_command(label='Abrir pasta')
menu_arquivo.add_separator()
menu_arquivo.add_command(label='Recentes')
menu_arquivo.add_cascade(label='Exemplos', menu=menu_arquivo_cascate)
atualizarListaDeScripts()

menu_arquivo.add_separator()
menu_arquivo.add_command(label='Salvar (Ctrl-S)', command=salvarArquivo)
menu_arquivo.add_command(label='Salvar Como (Ctrl-Shift-S)', command=salvarArquivoComoDialog)
menu_arquivo.add_separator()
menu_arquivo.add_command(label='imprimir (Ctrl-P)')
menu_arquivo.add_command(label='Exportar (Ctrl-E)')
menu_arquivo.add_command(label='Enviar por e-mail ')

# COMANDOS DE EXECUTAR
menu_executar.add_command(label='Executar Tudo (F5)', command=inicializador_orquestrador_interpretador)
menu_executar.add_command(label='Executar linha (F6)')
menu_executar.add_command(label='Executar até breakpoint (F7)')
menu_executar.add_command(label='Executar com delay (F8)')
menu_executar.add_command(label='Parar execução (F9)')
menu_executar.add_command(label='Inserir breakpoint (F10)')
menu_localizar.add_command(label='Localizar (CTRL + F)')
menu_localizar.add_command(label='Substituir (CTRL + R)')
menu_ferramentas.add_command(label='corrigir identação')
menu_ferramentas.add_command(label='Numero de espaços para o tab')

menu_interface_cascate_temas = Menu(menu_interface, tearoff = False)
menu_interface.add_cascade(label='Temas', menu=menu_interface_cascate_temas)
atualizarListaTemas()

menu_interface_cascate_sintaxe = Menu(menu_interface, tearoff = False)
menu_interface.add_cascade(label='sintaxe', menu=menu_interface_cascate_sintaxe)
atualizarListasintaxe()

menu_interface_cascate_fontes = Menu(menu_interface, tearoff = False)
menu_interface.add_cascade(label='fontes', menu=menu_interface_cascate_fontes)
atualizarListasfontes()

menu_ajuda.add_command(label='Ajuda (F1)')
menu_ajuda.add_command(label='Comandos Disponíveis')
menu_ajuda.add_command(label='Comunidade')
menu_sobre.add_command(label='Projeto')

# OPÇÕES RÁPIDAS
fr_opcoes_rapidas = Frame(tela)
fr_opcoes_rapidas.grid(row = 1, column =1, sticky=NSEW, columnspan=2)

icon_salva = PhotoImage(file='imagens/icon_salvar.png')
icon_corrige = PhotoImage(file='imagens/icon_arrumar.png')
icon_break = PhotoImage(file='imagens/icon_parar.png')
icon_play = PhotoImage(file='imagens/icon_play.png')
icon_play_break_point = PhotoImage(file='imagens/icon_play_breakpoint.png')
icon_desfazer = PhotoImage(file='imagens/left.png')
icon_redesfazer = PhotoImage(file='imagens/right.png')
icon_comentar = PhotoImage(file='imagens/icon_comentario.png')
icon_idioma = PhotoImage(file='imagens/icon_idioma.png')
icon_ajuda = PhotoImage(file='imagens/icon_duvida.png')
icon_pesquisar = PhotoImage(file='imagens/icon_pesquisa.png')

icon_salva = icon_salva.subsample(4,4)
icon_corrige = icon_corrige.subsample(4,4)
icon_break = icon_break.subsample(4,4)
icon_play = icon_play.subsample(4,4)
icon_play_break_point = icon_play_break_point.subsample(4,4)
icon_desfazer = icon_desfazer.subsample(4,4)
icon_redesfazer = icon_redesfazer.subsample(4,4)
icon_comentar = icon_comentar.subsample(4,4)
icon_idioma = icon_idioma.subsample(4,4)
icon_ajuda = icon_ajuda.subsample(4,4)
icon_pesquisar = icon_pesquisar.subsample(4,4)

# FLAT, SUNKEN, RAISED, GROOVE, RIDGE
btn_salva = Button(fr_opcoes_rapidas, image=icon_salva, relief = RAISED)
btn_corrige = Button(fr_opcoes_rapidas, image=icon_corrige, relief = RAISED)
btn_break = Button(fr_opcoes_rapidas, image=icon_break, relief = RAISED)
btn_play = Button(fr_opcoes_rapidas, image=icon_play, relief = RAISED, command = inicializador_orquestrador_interpretador)
btn_play_break_point = Button(fr_opcoes_rapidas, image=icon_play_break_point, relief = RAISED, command = inicializador_orquestrador_interpretador)
btn_desfazer = Button(fr_opcoes_rapidas, image=icon_desfazer, relief = RAISED)
btn_redesfazer = Button(fr_opcoes_rapidas, image=icon_redesfazer, relief = RAISED)
btn_comentar = Button(fr_opcoes_rapidas, image=icon_comentar, relief = RAISED)
btn_idioma = Button(fr_opcoes_rapidas, image=icon_idioma, relief = RAISED)
btn_ajuda = Button(fr_opcoes_rapidas, image=icon_ajuda, relief = RAISED)
btn_pesquisar = Button(fr_opcoes_rapidas, image=icon_pesquisar, relief = RAISED)

btn_salva.grid(row=1,column=1)
btn_corrige.grid(row=1,column=2)
btn_break.grid(row=1,column=3)
btn_play.grid(row=1,column=4)
btn_play_break_point.grid(row=1,column=5)
btn_desfazer.grid(row=1,column=6)
btn_redesfazer.grid(row=1,column=7)
btn_comentar.grid(row=1,column=8)
btn_idioma.grid(row=1,column=9)
btn_ajuda.grid(row=1,column=0)
btn_pesquisar.grid(row=1,column=10)

# INTERFACE GERAL
fr_principal = Frame(tela, bg='#393944')
fr_principal.grid_columnconfigure(2, weight=1)
fr_principal.rowconfigure(1, weight=1)
fr_principal.grid(row=2, column=1, sticky=NSEW)

# CONTADOR DE LINHAS
lb_linhas = Text(fr_principal, width = 5)
lb_linhas.config(state = DISABLED, border = 0, highlightthickness=0)
lb_linhas.grid(row=1, column=1, sticky=NSEW)

# TELA DE CODIFICAÇÃO
tx_codificacao = Text(fr_principal)

from tkinter import FLAT, SUNKEN, RAISED, GROOVE, RIDGE

scrollbar_text = Scrollbar(fr_principal, relief = FLAT)

tx_codificacao['yscrollcommand'] = scrollbar_text.set
scrollbar_text.config(command = tx_codificacao.yview)

tx_codificacao.focus_force()
tx_codificacao.bind('<Configure>', configuracoes )
tx_codificacao.bind('<KeyRelease>', atualiza_cor_sintaxe)
tx_codificacao.grid(row=1, column=2, sticky=NSEW)
scrollbar_text.grid(row=1, column=3, sticky=NSEW)

atualiza_design_interface()

#abrirArquivo('programa_teste.fyn')
abrirArquivo('loop.fyn')

#tx_codificacao.bind("<Button-4>", lambda tx_codificacao:scroolUp())
#tx_codificacao.bind("<Button-5>", lambda tx_codificacao:scroolDown())
#tx_codificacao.bind('<KeyRelease>', obterPosicaoDoCursor)

tela.mainloop()


