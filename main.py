import pygame
import random

# Inicialização do Pygame e do módulo de mixagem de som
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(16)  # Aumenta para 16 canais de som simultâneos

# Configurações iniciais do jogo
LARGURA_TELA = 1845
ALTURA_TELA = 700
TITULO_JOGO = "Galactic Odyssey"
VELOCIDADE_JOGADOR = 3
VELOCIDADE_TIRO = 20
VELOCIDADE_NAVE_INIMIGA = 2
INTERVALO_TROCA_NAVE = 100
ALTURA_CHAO = 88
ESPACAMENTO_MINIMO = 120  # Espaçamento mínimo entre as naves inimigas - Não fazer alterações neste valor para evitar erros.
TAMANHO_EXPLOSAO = (209, 179)

naves_inimigas = []  # Lista para armazenar as naves inimigas
ultimo_tempo_criacao_nave = 0
explosoes = []  # Lista para armazenar as explosões


# Criação da janela do jogo
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption(TITULO_JOGO)

# Carregamento dos sons
musica_fundo = pygame.mixer.music.load("assets/audio/som_espaço.mp3")
som_tiro = pygame.mixer.Sound("assets/audio/som_tiro.mp3")
som_tiro.set_volume(0.2)
som_explosao = pygame.mixer.Sound("assets/audio/som_explosao.mp3")
som_explosao.set_volume(0.1)

canal_explosao = pygame.mixer.Channel(0)  # Canal reservado para tocar o som da explosão

# Reprodução da música de fundo
pygame.mixer.music.play(-1)

# Função para carregar e escalar imagens
def carregar_escalar_imagem(caminho_imagem, tamanho_imagem):
    imagem = pygame.image.load(caminho_imagem).convert_alpha()
    return pygame.transform.scale(imagem, tamanho_imagem)

# Carregamento e redimensionamento das imagens
fundo = carregar_escalar_imagem("assets/img/fundo_1.png", (LARGURA_TELA, ALTURA_TELA))
chao = carregar_escalar_imagem("assets/img/chao_1.png", (LARGURA_TELA, 88))
imagens_nave = [carregar_escalar_imagem(f"assets/img/nave_{i}.png", (200, 105)) for i in range(1, 4)]
tiro = carregar_escalar_imagem("assets/img/tiro_1.png", (60, 44))
imagens_nave_inimiga = [carregar_escalar_imagem(f"assets/img/nave_inimiga_model{i}.png", (122, 105)) for i in range(1, 4)]
imagens_explosao = [carregar_escalar_imagem(f"assets/img/explosao_{i}.png", TAMANHO_EXPLOSAO) for i in range(1, 4)]

# Posições iniciais dos elementos
retangulo_nave = imagens_nave[0].get_rect(midbottom=(LARGURA_TELA // 2, ALTURA_TELA - 300))
retangulo_tiro = tiro.get_rect(midleft=(retangulo_nave.centerx, retangulo_nave.centery))
retangulo_nave_inimiga = imagens_nave_inimiga[0].get_rect(midright=(LARGURA_TELA // 2, random.randint(50, ALTURA_TELA - 50)))
posicao_x_chao, tiro_ativo, indice_imagem_nave_atual, indice_imagem_nave_inimiga_atual, tempo_ultima_troca, tempo_ultima_troca_nave_inimiga = 0, False, 0, 0, 0, 0

# Função para mover o chão
def mover_chao():
    global posicao_x_chao
    posicao_x_chao -= 2
    if posicao_x_chao <= -LARGURA_TELA:
        posicao_x_chao = 0

# Função para processar eventos
def processar_eventos():
    global tiro_ativo, indice_imagem_nave_atual, tempo_ultima_troca
    tempo_atual = pygame.time.get_ticks()

    if tempo_atual - tempo_ultima_troca > INTERVALO_TROCA_NAVE:
        indice_imagem_nave_atual = (indice_imagem_nave_atual + 1) % len(imagens_nave)
        tempo_ultima_troca = tempo_atual

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            return False

    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_RIGHT] and retangulo_nave.right < LARGURA_TELA: retangulo_nave.x += VELOCIDADE_JOGADOR
    if teclas[pygame.K_LEFT] and retangulo_nave.left > 0: retangulo_nave.x -= VELOCIDADE_JOGADOR
    if teclas[pygame.K_UP] and retangulo_nave.top > 0: retangulo_nave.y -= VELOCIDADE_JOGADOR
    if teclas[pygame.K_DOWN] and retangulo_nave.bottom < ALTURA_TELA - ALTURA_CHAO: retangulo_nave.y += VELOCIDADE_JOGADOR
    if teclas[pygame.K_SPACE] and not tiro_ativo:
        tiro_ativo = True
        som_tiro.play()
        retangulo_tiro.midleft = retangulo_nave.midright 

    return True

# Função para mover o tiro
def mover_tiro():
    global tiro_ativo
    if tiro_ativo:
        retangulo_tiro.x += VELOCIDADE_TIRO
        if retangulo_tiro.x > LARGURA_TELA:
            tiro_ativo = False

# Função para adicionar uma nova nave inimiga
def criar_nave_inimiga():
    global ultimo_tempo_criacao_nave

    tempo_atual = pygame.time.get_ticks()
    if len(naves_inimigas) < 15 and tempo_atual - ultimo_tempo_criacao_nave > 1000:  # Adiciona uma nave a cada 2 segundos
        # Gera uma posição horizontal aleatória, garantindo que a nova nave não esteja muito próxima das outras horizontalmente
        pos_x = LARGURA_TELA + random.randint(100, 400)
        pos_y = random.randint(50, ALTURA_TELA - ALTURA_CHAO - 105)
        retangulo_nova_nave_inimiga = imagens_nave_inimiga[0].get_rect(midright=(pos_x, pos_y))

        espaco_adequado = True
        for retangulo_nave_inimiga_existente in naves_inimigas:
            # Verifica se a posição X da nova nave está suficientemente distante das outras
            if abs(retangulo_nova_nave_inimiga.x - retangulo_nave_inimiga_existente.x) < ESPACAMENTO_MINIMO:
                espaco_adequado = False
                break

        if espaco_adequado:
            naves_inimigas.append(retangulo_nova_nave_inimiga)
            ultimo_tempo_criacao_nave = tempo_atual

# Função para mover a nave inimiga
def mover_naves_inimigas():
    global tempo_ultima_troca_nave_inimiga, indice_imagem_nave_inimiga_atual
    tempo_atual = pygame.time.get_ticks()

    # Troca a imagem da nave inimiga com base no intervalo de tempo
    if tempo_atual - tempo_ultima_troca_nave_inimiga > INTERVALO_TROCA_NAVE:
        indice_imagem_nave_inimiga_atual = (indice_imagem_nave_inimiga_atual + 1) % len(imagens_nave_inimiga)
        tempo_ultima_troca_nave_inimiga = tempo_atual

    for retangulo_nave_inimiga in naves_inimigas:
        retangulo_nave_inimiga.x -= VELOCIDADE_NAVE_INIMIGA
        # Quando a nave inimiga sai da tela, ela é removida da lista e uma nova é criada em posição aleatória
        if retangulo_nave_inimiga.right < 0:
            naves_inimigas.remove(retangulo_nave_inimiga)
            retangulo_nave_inimiga.right = LARGURA_TELA + random.randint(100, 400)
            retangulo_nave_inimiga.y = random.randint(50, ALTURA_TELA - ALTURA_CHAO - retangulo_nave_inimiga.height)
            naves_inimigas.append(retangulo_nave_inimiga)

# Função para verificar colisões entre tiros e naves inimigas
def verificar_colisoes():
    global tiro_ativo
    for nave_inimiga in naves_inimigas[:]:  # Faz uma cópia da lista para iterar
        if tiro_ativo and retangulo_tiro.colliderect(nave_inimiga):
            tiro_ativo = False  # Desativa o tiro ao atingir a nave
            explosoes.append([0, nave_inimiga.topleft, pygame.time.get_ticks()])  # Adiciona explosão com índice inicial 0
            naves_inimigas.remove(nave_inimiga)  # Remove a nave inimiga atingida
            canal_explosao.play(som_explosao)  # Toca o som da explosão no canal reservado

def desenhar_explosoes():
    tempo_atual = pygame.time.get_ticks()
    for explosao in explosoes[:]:  # Itera sobre uma cópia da lista de explosões
        indice_imagem, posicao, tempo_inicial = explosao
        
        if tempo_atual - tempo_inicial > 500:  # 500 milissegundos para a explosão desaparecer
            explosoes.remove(explosao)
        else:
            # Atualiza o índice da imagem a cada 166 milissegundos para criar a animação
            if tempo_atual - tempo_inicial > (indice_imagem + 1) * 166:
                explosao[0] = (indice_imagem + 1) % len(imagens_explosao)
            
            # Agora desenha a imagem da explosão atual
            tela.blit(imagens_explosao[indice_imagem], posicao)

# Função para remover naves inimigas que saíram da tela
def remover_naves_inimigas():
    for retangulo_nave_inimiga in naves_inimigas[:]:
        if retangulo_nave_inimiga.right < 0:
            naves_inimigas.remove(retangulo_nave_inimiga)


def desenhar():
    # Desenha o fundo
    tela.blit(fundo, (0, 0))

    # Desenha o chão
    tela.blit(chao, (posicao_x_chao, ALTURA_TELA - ALTURA_CHAO))
    tela.blit(chao, (posicao_x_chao + LARGURA_TELA, ALTURA_TELA - ALTURA_CHAO))

    # Desenha a nave do jogador
    tela.blit(imagens_nave[indice_imagem_nave_atual], retangulo_nave)

    # Desenha o tiro, se ativo
    if tiro_ativo:
        tela.blit(tiro, retangulo_tiro)

    # Desenha todas as naves inimigas
    for retangulo_nave_inimiga in naves_inimigas:
        tela.blit(imagens_nave_inimiga[indice_imagem_nave_inimiga_atual], retangulo_nave_inimiga)

# Loop principal do jogo
jogo_rodando = True
while jogo_rodando:
    if len(naves_inimigas) < 15:
        criar_nave_inimiga()  # Cria novas naves inimigas periodicamente
    jogo_rodando = processar_eventos()
    mover_chao()
    mover_tiro()
    mover_naves_inimigas()
    verificar_colisoes()
    remover_naves_inimigas()
    desenhar()
    desenhar_explosoes()
    
    pygame.display.update()

pygame.quit()
