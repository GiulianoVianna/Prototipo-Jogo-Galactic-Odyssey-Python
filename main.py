import pygame
import random

class Jogo:
    def __init__(self):
        # Inicialização
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(16)

        # Configurações
        self.LARGURA_TELA = 1845
        self.ALTURA_TELA = 700
        self.TITULO_JOGO = "Galactic Odyssey"
        self.VELOCIDADE_JOGADOR = 3
        self.VELOCIDADE_TIRO = 20
        self.VELOCIDADE_TIRO_INIMIGO = 2.6
        self.VELOCIDADE_NAVE_INIMIGA = 2
        self.INTERVALO_TROCA_NAVE = 100
        self.ALTURA_CHAO = 88
        self.ESPACAMENTO_MINIMO = 120   
        self.TAMANHO_EXPLOSAO = (209, 179)
        self.INTERVALO_TIRO_INIMIGO = 1000  # Intervalo de tempo entre tiros inimigos

        # Variáveis
        self.jogo_rodando = True
        self.naves_inimigas = []
        self.tiros_inimigos = []
        self.vida_atual_jogador = 6   
        self.pontuacao = 0    
        self.ultimo_tempo_criacao_nave = 0
        self.explosoes = []
        self.tempo_colisao = 0
        self.em_colisao = False
        self.tempo_ultima_troca_dano = 0
        self.indice_imagem_nave_dano_atual = 0

        # Tela
        self.tela = pygame.display.set_mode((self.LARGURA_TELA, self.ALTURA_TELA))
        pygame.display.set_caption(self.TITULO_JOGO)

        # Sons 
        pygame.mixer.music.load("assets/audio/som_espaço.mp3")
        self.som_tiro = pygame.mixer.Sound("assets/audio/som_tiro.mp3")
        self.som_tiro.set_volume(0.2)
        self.som_explosao = pygame.mixer.Sound("assets/audio/som_explosao.mp3")
        self.som_explosao.set_volume(0.1)
        self.canal_explosao = pygame.mixer.Channel(0)

        # Imagens
        self.fundo = self.carregar_escalar_imagem("assets/img/fundo_1.png", (self.LARGURA_TELA, self.ALTURA_TELA))
        self.chao = self.carregar_escalar_imagem("assets/img/chao_1.png", (self.LARGURA_TELA, 88))
        self.imagens_nave = [self.carregar_escalar_imagem(f"assets/img/nave_{i}.png", (200, 105)) for i in range(1, 4)]
        self.imagens_nave_colisao = [self.carregar_escalar_imagem("assets/img/nave_colisao.png", (200, 105))] 
        self.imagens_nave_dano = [self.carregar_escalar_imagem(f"assets/img/nave_dano_{i}.png", (200, 105)) for i in range(1, 4)]
        self.tiro = self.carregar_escalar_imagem("assets/img/tiro_1.png", (60, 44))
        self.imagens_nave_inimiga = [self.carregar_escalar_imagem(f"assets/img/nave_inimiga_model{i}.png", (122, 105)) for i in range(1, 3)]
        self.imagens_explosao = [self.carregar_escalar_imagem(f"assets/img/explosao_{i}.png", self.TAMANHO_EXPLOSAO) for i in range(1, 5)]
        self.imagens_vidas = [self.carregar_escalar_imagem(f"assets/img/vida_{i}.png", (302, 39)) for i in range(1, 7)]

        # Posições iniciais
        self.retangulo_nave = self.imagens_nave[0].get_rect(midbottom=(self.LARGURA_TELA // 2, self.ALTURA_TELA - 300))
        self.retangulo_tiro = self.tiro.get_rect(midleft=(self.retangulo_nave.centerx, self.retangulo_nave.centery))
        self.posicao_x_chao = 0
        self.tiro_ativo = False
        self.indice_imagem_nave_atual = 0
        self.indice_imagem_nave_inimiga_atual = 0
        self.tempo_ultima_troca = 0
        self.tempo_ultima_troca_nave_inimiga = 0

        # Reproduz música
        pygame.mixer.music.play(-1)

    def carregar_escalar_imagem(self, caminho_imagem, tamanho_imagem):
        imagem = pygame.image.load(caminho_imagem).convert_alpha()
        return pygame.transform.scale(imagem, tamanho_imagem)

    def mostrar_tela_inicial(self):
        imagem_tela_inicial = self.carregar_escalar_imagem("assets/img/tela_inicial.png", (self.LARGURA_TELA, self.ALTURA_TELA))
        self.tela.blit(imagem_tela_inicial, (0, 0))
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

    def processar_eventos(self):
        tempo_atual = pygame.time.get_ticks()

        if tempo_atual - self.tempo_ultima_troca > self.INTERVALO_TROCA_NAVE:
            self.indice_imagem_nave_atual = (self.indice_imagem_nave_atual + 1) % len(self.imagens_nave)
            self.tempo_ultima_troca = tempo_atual

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False

        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_RIGHT] and self.retangulo_nave.right < self.LARGURA_TELA:  
            self.retangulo_nave.x += self.VELOCIDADE_JOGADOR
        if teclas[pygame.K_LEFT] and self.retangulo_nave.left > 0:
            self.retangulo_nave.x -= self.VELOCIDADE_JOGADOR
        if teclas[pygame.K_UP] and self.retangulo_nave.top > 0:
            self.retangulo_nave.y -= self.VELOCIDADE_JOGADOR
        if teclas[pygame.K_DOWN] and self.retangulo_nave.bottom < self.ALTURA_TELA - self.ALTURA_CHAO:
            self.retangulo_nave.y += self.VELOCIDADE_JOGADOR
        if teclas[pygame.K_SPACE] and not self.tiro_ativo:
            self.tiro_ativo = True
            self.som_tiro.play()
            self.retangulo_tiro.midleft = self.retangulo_nave.midright

        return True

    def mostrar_game_over(self):
        self.tela.fill((0, 0, 0))
        imagem_game_over_original = pygame.image.load("assets/img/game_over.png")
        largura_original, altura_original = imagem_game_over_original.get_size()
        nova_largura = 600
        nova_altura = int((nova_largura / largura_original) * altura_original)
        imagem_game_over = pygame.transform.scale(imagem_game_over_original, (nova_largura, nova_altura))
        imagem_game_over_rect = imagem_game_over.get_rect(center=(self.LARGURA_TELA // 2, self.ALTURA_TELA // 2))
        texto_continuar = pygame.font.Font(None, 36).render("Pressione ESPAÇO para continuar ou ESC para sair", True, (255, 255, 255))
        rect_continuar = texto_continuar.get_rect(center=(self.LARGURA_TELA // 2, self.ALTURA_TELA // 2 + nova_altura // 2 + 30))
        self.tela.blit(imagem_game_over, imagem_game_over_rect)
        self.tela.blit(texto_continuar, rect_continuar)
        pygame.display.flip()

    def contagem_regressiva(self):
        contador = 5
        fonte = pygame.font.Font(None, 74 * 2)
        fonte_menor = pygame.font.Font(None, 36 * 2)

        while contador > 0:
            self.tela.fill((0, 0, 0))
            mensagem = fonte_menor.render("O Jogo vai reiniciar em:", True, (255, 255, 255))
            rect_mensagem = mensagem.get_rect(center=(self.LARGURA_TELA // 2, self.ALTURA_TELA // 2 - 60))
            self.tela.blit(mensagem, rect_mensagem)
            texto_contagem = fonte.render(str(contador), True, (255, 255, 255))
            rect_texto = texto_contagem.get_rect(center=(self.LARGURA_TELA // 2, self.ALTURA_TELA // 2 + 20))
            self.tela.blit(texto_contagem, rect_texto)
            pygame.display.flip()
            pygame.time.wait(1000)
            contador -= 1

    def reiniciar_jogo(self):
        self.contagem_regressiva()
        self.vida_atual_jogador = 6
        self.naves_inimigas = []
        self.tiros_inimigos = []
        self.pontuacao = 0
        self.explosoes = []

    def mover_chao(self):
        self.posicao_x_chao -= 2
        if self.posicao_x_chao <= -self.LARGURA_TELA:
            self.posicao_x_chao = 0

    def mover_tiro(self):
        if self.tiro_ativo:
            self.retangulo_tiro.x += self.VELOCIDADE_TIRO
            if self.retangulo_tiro.x > self.LARGURA_TELA:
                self.tiro_ativo = False

    def criar_nave_inimiga(self):
        tempo_atual = pygame.time.get_ticks()
        if len(self.naves_inimigas) < 15 and tempo_atual - self.ultimo_tempo_criacao_nave > 1000:
            nova_nave_inimiga = NaveInimiga(self)
            if nova_nave_inimiga.espaco_adequado(self.naves_inimigas):
                self.naves_inimigas.append(nova_nave_inimiga)
                self.ultimo_tempo_criacao_nave = tempo_atual

    def mover_naves_inimigas(self):
        for nave_inimiga in self.naves_inimigas:
            nave_inimiga.mover()

    def mover_tiros_inimigos(self):
        for tiro_inimigo in self.tiros_inimigos[:]:
            tiro_inimigo.mover()

    def verificar_colisoes(self):
        for nave_inimiga in self.naves_inimigas[:]:
            if self.tiro_ativo and self.retangulo_tiro.colliderect(nave_inimiga.rect):
                self.tiro_ativo = False
                self.explosoes.append([0, nave_inimiga.rect.topleft, pygame.time.get_ticks()])
                self.naves_inimigas.remove(nave_inimiga)  
                self.pontuacao += 10
                self.canal_explosao.play(self.som_explosao)

            if self.retangulo_nave.colliderect(nave_inimiga.rect):
                self.vida_atual_jogador -= 1
                self.em_colisao = True
                self.tempo_colisao = pygame.time.get_ticks()
                self.naves_inimigas.remove(nave_inimiga)
                if self.vida_atual_jogador == 0:
                    self.mostrar_game_over()
                    while True:
                        for evento in pygame.event.get():
                            if evento.type == pygame.QUIT:
                                self.jogo_rodando = False
                                return False
                            if evento.type == pygame.KEYDOWN:
                                if evento.key == pygame.K_ESCAPE:
                                    self.jogo_rodando = False
                                    return False  
                                if evento.key == pygame.K_SPACE:
                                    self.reiniciar_jogo()
                                    return True
                else:
                    self.explosoes.append([0, nave_inimiga.rect.topleft, pygame.time.get_ticks()])
                    self.canal_explosao.play(self.som_explosao)

        for tiro_inimigo in self.tiros_inimigos[:]:
            if self.retangulo_nave.colliderect(tiro_inimigo.rect):
                self.vida_atual_jogador -= 1
                self.em_colisao = True
                self.tempo_colisao = pygame.time.get_ticks()
                self.tiros_inimigos.remove(tiro_inimigo)
                if self.vida_atual_jogador == 0:
                    self.mostrar_game_over()
                    while True:
                        for evento in pygame.event.get():
                            if evento.type == pygame.QUIT:
                                self.jogo_rodando = False
                                return False
                            if evento.type == pygame.KEYDOWN:
                                if evento.key == pygame.K_ESCAPE:
                                    self.jogo_rodando = False
                                    return False  
                                if evento.key == pygame.K_SPACE:
                                    self.reiniciar_jogo()
                                    return True

    def desenhar_explosoes(self):
        tempo_atual = pygame.time.get_ticks()
        for explosao in self.explosoes[:]:
            indice_imagem, posicao, tempo_inicial = explosao
            if tempo_atual - tempo_inicial > 500:
                self.explosoes.remove(explosao)
            else:
                if tempo_atual - tempo_inicial > (indice_imagem + 1) * 166:
                    explosao[0] = (indice_imagem + 1) % len(self.imagens_explosao)
                self.tela.blit(self.imagens_explosao[indice_imagem], posicao)

    def desenhar_pontuacao(self):
        fonte = pygame.font.Font(None, 36)
        texto_pontuacao = fonte.render(f"Pontuação: {self.pontuacao}", True, (255, 255, 255))
        self.tela.blit(texto_pontuacao, (self.LARGURA_TELA - texto_pontuacao.get_width() - 10, 10))

    def desenhar_vida(self):
        self.tela.blit(self.imagens_vidas[self.vida_atual_jogador - 1], (10, 10))

    def desenhar(self):
        tempo_atual = pygame.time.get_ticks()
        self.tela.blit(self.fundo, (0, 0))
        self.tela.blit(self.chao, (self.posicao_x_chao, self.ALTURA_TELA - self.ALTURA_CHAO))
        self.tela.blit(self.chao, (self.posicao_x_chao + self.LARGURA_TELA, self.ALTURA_TELA - self.ALTURA_CHAO))

        if self.vida_atual_jogador <= 2:
            if tempo_atual - self.tempo_ultima_troca_dano > 200:
                self.indice_imagem_nave_dano_atual = (self.indice_imagem_nave_dano_atual + 1) % len(self.imagens_nave_dano)
                self.tempo_ultima_troca_dano = tempo_atual
            imagem_nave_atual = self.imagens_nave_dano[self.indice_imagem_nave_dano_atual]
        elif self.em_colisao:
            imagem_nave_atual = self.imagens_nave_colisao[0]
            if tempo_atual - self.tempo_colisao > 300:
                self.em_colisao = False
        else:
            imagem_nave_atual = self.imagens_nave[self.indice_imagem_nave_atual]
        
        self.tela.blit(imagem_nave_atual, self.retangulo_nave)
        if self.tiro_ativo:
            self.tela.blit(self.tiro, self.retangulo_tiro)

        for nave_inimiga in self.naves_inimigas:
            nave_inimiga.desenhar()

        for tiro_inimigo in self.tiros_inimigos:
            tiro_inimigo.desenhar(self.tela)

        self.desenhar_vida()
        self.desenhar_pontuacao()

    def executar(self):
        self.mostrar_tela_inicial()
        while self.jogo_rodando:
            if len(self.naves_inimigas) < 15:
                self.criar_nave_inimiga()

            self.jogo_rodando = self.processar_eventos()
            self.mover_chao()
            self.mover_tiro()
            self.mover_naves_inimigas()
            self.mover_tiros_inimigos()
            self.verificar_colisoes()
            self.desenhar()
            self.desenhar_explosoes()

            pygame.display.update()

        pygame.quit()

class NaveInimiga:
    def __init__(self, jogo):
        self.jogo = jogo
        self.rect = self.jogo.imagens_nave_inimiga[0].get_rect(
            midright=(
                self.jogo.LARGURA_TELA + random.randint(100, 400),
                random.randint(50, self.jogo.ALTURA_TELA - self.jogo.ALTURA_CHAO - 105)
            )
        )
        self.ultimo_tempo_tiro = pygame.time.get_ticks()

    def espaco_adequado(self, outras_naves):
        for nave_existente in outras_naves:
            if abs(self.rect.x - nave_existente.rect.x) < self.jogo.ESPACAMENTO_MINIMO:
                return False
        return True

    def mover(self):
        self.rect.x -= self.jogo.VELOCIDADE_NAVE_INIMIGA
        if self.rect.right < 0:
            self.jogo.naves_inimigas.remove(self)
        elif pygame.time.get_ticks() - self.ultimo_tempo_tiro > self.jogo.INTERVALO_TIRO_INIMIGO:
            self.atirar()
            self.ultimo_tempo_tiro = pygame.time.get_ticks()

    def atirar(self):
        tiro = TiroInimigo(self.jogo, self.rect)
        self.jogo.tiros_inimigos.append(tiro)

    def desenhar(self):
        self.jogo.tela.blit(self.jogo.imagens_nave_inimiga[self.jogo.indice_imagem_nave_inimiga_atual], self.rect)

class TiroInimigo:
    def __init__(self, jogo, rect_nave_inimiga):
        self.jogo = jogo
        self.imagem = jogo.carregar_escalar_imagem("assets/img/tiro_2.png", (40, 24))
        self.rect = self.imagem.get_rect(midright=rect_nave_inimiga.midleft)
        self.velocidade = -jogo.VELOCIDADE_TIRO_INIMIGO

    def mover(self):
        self.rect.x += self.velocidade
        if self.rect.right < 0:
            self.jogo.tiros_inimigos.remove(self)

    def desenhar(self, tela):
        tela.blit(self.imagem, self.rect)

if __name__ == "__main__":
    jogo = Jogo()
    jogo.executar()
