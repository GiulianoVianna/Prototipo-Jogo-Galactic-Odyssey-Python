import pygame

# Inicializa o Pygame e o módulo de mixagem de som
pygame.init()
pygame.mixer.init()

# Define as configurações iniciais do jogo
LARGURA_TELA = 1845
ALTURA_TELA = 700
TITULO_JOGO = "Galactic Odyssey"
VELOCIDADE_JOGADOR = 3
VELOCIDADE_TIRO = 20
INTERVALO_TROCA_NAVE = 100  # Intervalo de troca para animação da nave em milissegundos

# Cria a janela do jogo com o tamanho especificado
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption(TITULO_JOGO)

# Carrega os sons e define o volume do som do tiro
musica_fundo = pygame.mixer.music.load("assets/audio/som_espaço.mp3")
som_tiro = pygame.mixer.Sound("assets/audio/som_tiro.mp3")
som_tiro.set_volume(0.2)  # Reduz o volume do som do tiro para metade

# Reproduz a música de fundo continuamente
pygame.mixer.music.play(-1)

# Função para carregar e redimensionar imagens
def carregar_escalar_imagem(caminho_imagem, tamanho_imagem):
    imagem = pygame.image.load(caminho_imagem).convert_alpha()
    imagem_escalada = pygame.transform.scale(imagem, tamanho_imagem)
    return imagem_escalada

# Carrega e redimensiona as imagens do jogo
fundo = carregar_escalar_imagem("assets/img/fundo_1.png", (LARGURA_TELA, ALTURA_TELA))
chao = carregar_escalar_imagem("assets/img/chao_1.png", (LARGURA_TELA, 88))
imagens_nave = [
    carregar_escalar_imagem("assets/img/nave_1.png", (200, 105)),
    carregar_escalar_imagem("assets/img/nave_2.png", (200, 105)),
    carregar_escalar_imagem("assets/img/nave_3.png", (200, 105))
]
tiro = carregar_escalar_imagem("assets/img/tiro_1.png", (60, 44))

# Define as posições iniciais dos elementos na tela
retangulo_nave = imagens_nave[0].get_rect(midbottom=(LARGURA_TELA // 2, ALTURA_TELA - 50))
retangulo_tiro = tiro.get_rect(midleft=(retangulo_nave.centerx, retangulo_nave.centery))
posicao_x_chao = 0
tiro_ativo = False
indice_imagem_nave_atual = 0
tempo_ultima_troca = 0

# Função para mover o chão e criar um efeito de deslocamento contínuo
def mover_chao():
    global posicao_x_chao
    posicao_x_chao -= 2
    if posicao_x_chao <= -LARGURA_TELA:
        posicao_x_chao = 0

# Função para processar os eventos do jogo, como entrada do usuário e ação de fechar o jogo
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
    if teclas[pygame.K_RIGHT] and retangulo_nave.right < LARGURA_TELA:
        retangulo_nave.x += VELOCIDADE_JOGADOR
    if teclas[pygame.K_LEFT] and retangulo_nave.left > 0:
        retangulo_nave.x -= VELOCIDADE_JOGADOR
    if teclas[pygame.K_UP] and retangulo_nave.top > 0:
        retangulo_nave.y -= VELOCIDADE_JOGADOR
    if teclas[pygame.K_DOWN] and retangulo_nave.bottom < ALTURA_TELA:
        retangulo_nave.y += VELOCIDADE_JOGADOR

    if teclas[pygame.K_SPACE] and not tiro_ativo:
        tiro_ativo = True
        som_tiro.play()  
        retangulo_tiro.midleft = retangulo_nave.midright

    return True

# Função para mover o tiro na tela
def mover_tiro():
    global tiro_ativo
    if tiro_ativo:
        retangulo_tiro.x += VELOCIDADE_TIRO
        if retangulo_tiro.x > LARGURA_TELA:
            tiro_ativo = False

# Função para desenhar todos os elementos na tela
def desenhar():
    tela.blit(fundo, (0, 0))
    tela.blit(chao, (posicao_x_chao, ALTURA_TELA - 88))
    tela.blit(chao, (posicao_x_chao + LARGURA_TELA, ALTURA_TELA - 88))
    if tiro_ativo:
        tela.blit(tiro, retangulo_tiro)
    tela.blit(imagens_nave[indice_imagem_nave_atual], retangulo_nave)
    pygame.display.update()

# Loop principal do jogo, que mantém o jogo rodando
jogo_rodando = True
while jogo_rodando:
    jogo_rodando = processar_eventos()
    mover_chao()
    mover_tiro()
    desenhar()

# Limpa e encerra o Pygame quando o jogo é fechado
pygame.quit()
