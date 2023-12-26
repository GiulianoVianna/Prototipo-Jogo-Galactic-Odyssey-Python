import pygame
import random

# Inicialização
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(16)  

# Configurações
LARGURA_TELA = 1845
ALTURA_TELA = 700
TITULO_JOGO = "Galactic Odyssey"
VELOCIDADE_JOGADOR = 3
VELOCIDADE_TIRO = 20
VELOCIDADE_NAVE_INIMIGA = 3
INTERVALO_TROCA_NAVE = 100
ALTURA_CHAO = 88
ESPACAMENTO_MINIMO = 120   
TAMANHO_EXPLOSAO = (209, 179)

# Variáveis
jogo_rodando = True
naves_inimigas = []   
vida_atual_jogador = 6   
pontuacao = 0    
ultimo_tempo_criacao_nave = 0
explosoes = []
tempo_colisao = 0
em_colisao = False
tempo_ultima_troca_dano = 0
indice_imagem_nave_dano_atual = 0

# Tela
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption(TITULO_JOGO)

# Sons 
musica_fundo = pygame.mixer.music.load("assets/audio/som_espaço.mp3")
som_tiro = pygame.mixer.Sound("assets/audio/som_tiro.mp3")
som_tiro.set_volume(0.2)
som_explosao = pygame.mixer.Sound("assets/audio/som_explosao.mp3")
som_explosao.set_volume(0.1)
canal_explosao = pygame.mixer.Channel(0)

# Imagens
def carregar_escalar_imagem(caminho_imagem, tamanho_imagem):
  imagem = pygame.image.load(caminho_imagem).convert_alpha()
  return pygame.transform.scale(imagem, tamanho_imagem)

fundo = carregar_escalar_imagem("assets/img/fundo_1.png", (LARGURA_TELA, ALTURA_TELA))
chao = carregar_escalar_imagem("assets/img/chao_1.png", (LARGURA_TELA, 88))
imagens_nave = [carregar_escalar_imagem(f"assets/img/nave_{i}.png", (200, 105)) for i in range(1, 4)]
imagens_nave_colisao = [carregar_escalar_imagem("assets/img/nave_colisao.png", (200, 105))] 
imagens_nave_dano = [carregar_escalar_imagem(f"assets/img/nave_dano_{i}.png", (200, 105)) for i in range(1, 4)]
tiro = carregar_escalar_imagem("assets/img/tiro_1.png", (60, 44))
imagens_nave_inimiga = [carregar_escalar_imagem(f"assets/img/nave_inimiga_model{i}.png", (122, 105)) for i in range(1, 3)]
imagens_explosao = [carregar_escalar_imagem(f"assets/img/explosao_{i}.png", TAMANHO_EXPLOSAO) for i in range(1, 5)]
imagens_vidas = [carregar_escalar_imagem(f"assets/img/vida_{i}.png", (302, 39)) for i in range(1, 7)]

# Posições iniciais
retangulo_nave = imagens_nave[0].get_rect(midbottom=(LARGURA_TELA // 2, ALTURA_TELA - 300))
retangulo_tiro = tiro.get_rect(midleft=(retangulo_nave.centerx, retangulo_nave.centery))
retangulo_nave_inimiga = imagens_nave_inimiga[0].get_rect(midright=(LARGURA_TELA // 2, random.randint(50, ALTURA_TELA - 50)))  
posicao_x_chao, tiro_ativo, indice_imagem_nave_atual, indice_imagem_nave_inimiga_atual, tempo_ultima_troca, tempo_ultima_troca_nave_inimiga = 0, False, 0, 0, 0, 0

# Reproduz música
pygame.mixer.music.play(-1)

# Funções  

# Mostrar tela inicial
def mostrar_tela_inicial():
    imagem_tela_inicial = carregar_escalar_imagem("assets/img/tela_inicial.png", (LARGURA_TELA, ALTURA_TELA))
    tela.blit(imagem_tela_inicial, (0, 0))
    pygame.display.flip()

    esperar_inicio = True
    while esperar_inicio:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    esperar_inicio = False
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

# Processar eventos
def processar_eventos():

  global tiro_ativo, indice_imagem_nave_atual, tempo_ultima_troca, em_colisao

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
  if teclas[pygame.K_DOWN] and retangulo_nave.bottom < ALTURA_TELA - ALTURA_CHAO:
    retangulo_nave.y += VELOCIDADE_JOGADOR
  if teclas[pygame.K_SPACE] and not tiro_ativo:
    tiro_ativo = True
    som_tiro.play()
    retangulo_tiro.midleft = retangulo_nave.midright

  return True

# Mostrar game over
def mostrar_game_over():
    tela.fill((0, 0, 0))

    # Carrega a imagem game_over.png
    imagem_game_over_original = pygame.image.load("assets/img/game_over.png")
    largura_original, altura_original = imagem_game_over_original.get_size()

    # Calcula a nova altura mantendo a proporção
    nova_largura = 600
    nova_altura = int((nova_largura / largura_original) * altura_original)

    # Escala a imagem
    imagem_game_over = pygame.transform.scale(imagem_game_over_original, (nova_largura, nova_altura))
    
    # Obtém o retângulo da imagem e centraliza na tela
    imagem_game_over_rect = imagem_game_over.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2))

    # Renderiza o texto "Pressione ESPAÇO para continuar ou ESC para sair" e obtém o seu retângulo
    texto_continuar = pygame.font.Font(None, 36).render("Pressione ESPAÇO para continuar ou ESC para sair", True, (255, 255, 255))
    rect_continuar = texto_continuar.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 + nova_altura // 2 + 30))

    # Blita a imagem de game over e o texto de continuar
    tela.blit(imagem_game_over, imagem_game_over_rect)
    tela.blit(texto_continuar, rect_continuar)

    pygame.display.flip()

# Contagem regressiva para reiniciar o jogo
def contagem_regressiva():
    contador = 5
    fonte = pygame.font.Font(None, 74 * 2)  # Aumenta o tamanho da fonte
    fonte_menor = pygame.font.Font(None, 36 * 2)  # Fonte menor para a mensagem

    while contador > 0:
        tela.fill((0, 0, 0))  # Limpa a tela

        # Mensagem
        mensagem = fonte_menor.render("O Jogo vai reiniciar em:", True, (255, 255, 255))
        rect_mensagem = mensagem.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 - 60))
        tela.blit(mensagem, rect_mensagem)

        # Número da contagem
        texto_contagem = fonte.render(str(contador), True, (255, 255, 255))
        rect_texto = texto_contagem.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 + 20))
        tela.blit(texto_contagem, rect_texto)

        pygame.display.flip()
        pygame.time.wait(1000)  # Espera um segundo
        contador -= 1

# Reiniciar o jogo  
def reiniciar_jogo():
    global vida_atual_jogador, naves_inimigas, pontuacao, explosoes

    contagem_regressiva()  # Contagem regressiva para reiniciar o jogo

    vida_atual_jogador = 6
    naves_inimigas = []
    pontuacao = 0
    explosoes = []
      
# Mover chão
def mover_chao():
  
  global posicao_x_chao
  posicao_x_chao -= 2
  if posicao_x_chao <= -LARGURA_TELA:
    posicao_x_chao = 0

# Mover tiro  
def mover_tiro():
  
  global tiro_ativo
  if tiro_ativo:
    retangulo_tiro.x += VELOCIDADE_TIRO
    if retangulo_tiro.x > LARGURA_TELA:
      tiro_ativo = False

# Criar nave inimiga
def criar_nave_inimiga():
  
  global ultimo_tempo_criacao_nave

  tempo_atual = pygame.time.get_ticks()
  if len(naves_inimigas) < 15 and tempo_atual - ultimo_tempo_criacao_nave > 1000:
    
    pos_x = LARGURA_TELA + random.randint(100, 400)
    pos_y = random.randint(50, ALTURA_TELA - ALTURA_CHAO - 105)
    retangulo_nova_nave_inimiga = imagens_nave_inimiga[0].get_rect(midright=(pos_x, pos_y))

    espaco_adequado = True
    for retangulo_nave_inimiga_existente in naves_inimigas:
      
      if abs(retangulo_nova_nave_inimiga.x - retangulo_nave_inimiga_existente.x) < ESPACAMENTO_MINIMO:
        espaco_adequado = False
        break

    if espaco_adequado:
      naves_inimigas.append(retangulo_nova_nave_inimiga)
      ultimo_tempo_criacao_nave = tempo_atual

# Mover naves inimigas  
def mover_naves_inimigas():
  
  global tempo_ultima_troca_nave_inimiga, indice_imagem_nave_inimiga_atual
  tempo_atual = pygame.time.get_ticks()

  if tempo_atual - tempo_ultima_troca_nave_inimiga > INTERVALO_TROCA_NAVE:
    indice_imagem_nave_inimiga_atual = (indice_imagem_nave_inimiga_atual + 1) % len(imagens_nave_inimiga)
    tempo_ultima_troca_nave_inimiga = tempo_atual

  for retangulo_nave_inimiga in naves_inimigas:
    retangulo_nave_inimiga.x -= VELOCIDADE_NAVE_INIMIGA
    
    if retangulo_nave_inimiga.right < 0:
      naves_inimigas.remove(retangulo_nave_inimiga)
      retangulo_nave_inimiga.right = LARGURA_TELA + random.randint(100, 400)
      retangulo_nave_inimiga.y = random.randint(50, ALTURA_TELA - ALTURA_CHAO - retangulo_nave_inimiga.height)
      naves_inimigas.append(retangulo_nave_inimiga)
      
# Verificar colisões
def verificar_colisoes():

  global tiro_ativo, jogo_rodando 
  global vida_atual_jogador, pontuacao
  global indice_imagem_nave_atual, tempo_colisao, em_colisao
  
  for nave_inimiga in naves_inimigas[:]:

    if tiro_ativo and retangulo_tiro.colliderect(nave_inimiga):
      tiro_ativo = False
      explosoes.append([0, nave_inimiga.topleft, pygame.time.get_ticks()])
      naves_inimigas.remove(nave_inimiga)  
      pontuacao += 10
      canal_explosao.play(som_explosao)

    if retangulo_nave.colliderect(nave_inimiga):
      vida_atual_jogador -= 1
      em_colisao = True
      #indice_imagem_nave_atual = 0 # imagem de colisão
      tempo_colisao = pygame.time.get_ticks()
      naves_inimigas.remove(nave_inimiga)
      if vida_atual_jogador == 0:
        mostrar_game_over()
        while True:
          for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
              jogo_rodando = False
              return False
            if evento.type == pygame.KEYDOWN:
              if evento.key == pygame.K_ESCAPE:
                jogo_rodando = False
                return False  
              if evento.key == pygame.K_SPACE:
                reiniciar_jogo()
                return True
      else:
        explosoes.append([0, nave_inimiga.topleft, pygame.time.get_ticks()])
        canal_explosao.play(som_explosao)
        
# Remover naves inimigas  
def remover_naves_inimigas():
  
  for retangulo_nave_inimiga in naves_inimigas[:]:
    if retangulo_nave_inimiga.right < 0:
      naves_inimigas.remove(retangulo_nave_inimiga)
      
# Desenhar explosões
def desenhar_explosoes():

  tempo_atual = pygame.time.get_ticks()
  for explosao in explosoes[:]:
    indice_imagem, posicao, tempo_inicial = explosao
        
    if tempo_atual - tempo_inicial > 500:
      explosoes.remove(explosao)
    else:
      if tempo_atual - tempo_inicial > (indice_imagem + 1) * 166:
        explosao[0] = (indice_imagem + 1) % len(imagens_explosao)
            
      tela.blit(imagens_explosao[indice_imagem], posicao)

# Desenhar pontuação 
def desenhar_pontuacao():

  fonte = pygame.font.Font(None, 36)
  texto_pontuacao = fonte.render(f"Pontuação: {pontuacao}", True, (255, 255, 255))
  tela.blit(texto_pontuacao, (LARGURA_TELA - texto_pontuacao.get_width() - 10, 10))

# Desenhar vida
def desenhar_vida():

  global vida_atual_jogador  
  tela.blit(imagens_vidas[vida_atual_jogador - 1], (10, 10))

# Desenhar elementos
def desenhar():
    global indice_imagem_nave_atual, tempo_colisao, em_colisao
    global tempo_ultima_troca_dano, indice_imagem_nave_dano_atual
    tela.blit(fundo, (0, 0))
    tela.blit(chao, (posicao_x_chao, ALTURA_TELA - ALTURA_CHAO))
    tela.blit(chao, (posicao_x_chao + LARGURA_TELA, ALTURA_TELA - ALTURA_CHAO))

    tempo_atual = pygame.time.get_ticks()

    # Animação das imagens de dano
    if vida_atual_jogador <= 2:
        if tempo_atual - tempo_ultima_troca_dano > 200:  # Trocar imagem a cada 200 ms
            indice_imagem_nave_dano_atual = (indice_imagem_nave_dano_atual + 1) % len(imagens_nave_dano)
            tempo_ultima_troca_dano = tempo_atual
        imagem_nave_atual = imagens_nave_dano[indice_imagem_nave_dano_atual]
    elif em_colisao:
        imagem_nave_atual = imagens_nave_colisao[0]
        if tempo_atual - tempo_colisao > 300:
            em_colisao = False
    else:
        imagem_nave_atual = imagens_nave[indice_imagem_nave_atual]
    
    tela.blit(imagem_nave_atual, retangulo_nave)
    if tiro_ativo:
        tela.blit(tiro, retangulo_tiro)

    for retangulo_nave_inimiga in naves_inimigas:
        tela.blit(imagens_nave_inimiga[indice_imagem_nave_inimiga_atual], retangulo_nave_inimiga)
  
    desenhar_vida()
    desenhar_pontuacao()

# Loop principal
mostrar_tela_inicial()
while jogo_rodando:

  if len(naves_inimigas) < 15:
    criar_nave_inimiga()

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