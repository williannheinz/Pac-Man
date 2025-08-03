#Gerencia os estados e o loop principal.

# src/game.py

import json
import pygame
import sys
import os
from settings import *
from level import Level
from player import Player
from collections import deque
from enemy import Enemy

class Game:
    def __init__(self):
        """
        Construtor da classe Game. Inicializa o Pygame e a tela.
        """
        pygame.init()


        self.score = 0
        self.lives = PLAYER_START_LIVES
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITULO)
        self.clock = pygame.time.Clock()
        self.running = True


        # Construcao do caminho para o arquivo
        caminho_do_mapa = os.path.join(MAPS_FOLDER, 'level_1.txt')
        #  instância do Level
        self.level = Level(caminho_do_mapa)

        #  Bloco que cria o jogador
        # Usa o metodo find_symbol do TAD Mapa para achar a posição inicial
        start_pos_list = self.level.find_symbol('P')
        if start_pos_list:
            # Pega a primeira posição encontrada (formato: (linha, coluna))
            # e converte para (coluna, linha) para o nosso Player
            start_pos = (start_pos_list[0][1], start_pos_list[0][0])
            self.player = Player(self, start_pos)
        else:
            # Posição padrão caso 'P' não seja encontrado no mapa
            self.player = Player(self, (1, 1))

        self.state = 'menu_principal'  # Define o estado inicial do jogo

        # <<<< ALTERADO: Apague as antigas variáveis de pausa e adicione estas >>>>
        self.menu_options = ['Iniciar Jogo', 'Ranking', 'Carregar Jogo Salvo', 'Sair']
        self.selected_menu_option = 0

        self.pause_options = ['Sair e Salvar', 'Sair sem Salvar', 'Cancelar']
        self.selected_pause_option = 0  # O índice da opção selecionada (começa em 0)

        # Atributo para o cooldown do túnel
        self.tunnel_cooldown = 0  # Em frames. 0 significa que os túneis estão ativos.

        #fantasmas
        self.enemies = []
        self.ghost_queue = deque()
        self.ghost_spawn_timer = 0

        self.ghost_sprites = {}  # Dicionário para guardar as imagens dos fantasmas
        self.load_ghost_sprites()  # Carrega as imagens na inicialização
        self.load_enemies()  # Agora usa as imagens carregadas






    # --- MÉTODOS DE ESTADO: MENU ---

    def load_ghost_sprites(self):
        """
        Carrega, redimensiona e armazena todas as imagens dos fantasmas.
        """
        # Pega todos os arquivos .png da pasta e os ordena para garantir a consistência
        filenames = sorted([f for f in os.listdir(GHOSTS_FOLDER) if f.endswith('.png')])

        # Mapeia um nome para cada sprite (pode ajustar se os nomes forem diferentes)
        sprite_keys = ['blinky', 'pinky', 'inky', 'clyde']

        for i, filename in enumerate(filenames):
            # Garante que não tentemos acessar um índice de sprite_keys que não existe
            if i < len(sprite_keys):
                key = sprite_keys[i]
                path = os.path.join(GHOSTS_FOLDER, filename)
                img = pygame.image.load(path).convert_alpha()
                scaled_img = pygame.transform.scale(img, (GRID_SIZE, GRID_SIZE))
                self.ghost_sprites[key] = scaled_img

    #  metodo para resetar o jogo inteiro
    def reset_game(self):
        """  Reseta_todo o estado do jogo para uma nova partida. """

        self.score = 0
        self.lives = PLAYER_START_LIVES

        # Reseta as entidades para suas posições iniciais
        self.player.reset()
        # Limpa a lista de inimigos ativos
        self.enemies = []
        # Recria a fila de fantasmas e a repopula
        self.ghost_queue = deque()
        self.load_enemies()
        # Reseta o timer de spawn dos fantasmas
        self.ghost_spawn_timer = 0

        # Reseta o mapa para restaurar todos os pontinhos
        self.level.reset()

    def menu_principal_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_menu_option = (self.selected_menu_option - 1) % len(self.menu_options)
                if event.key == pygame.K_DOWN:
                    self.selected_menu_option = (self.selected_menu_option + 1) % len(self.menu_options)

                if event.key == pygame.K_RETURN:
                    # Opção 0: Iniciar Jogo
                    if self.selected_menu_option == 0:
                        self.reset_game()
                        self.state = 'jogando'
                    # Opção 1: Ranking
                    elif self.selected_menu_option == 1:
                        self.state = 'exibindo_ranking'
                    # Opção 2: Carregar Jogo Salvo
                    elif self.selected_menu_option == 2:
                        self.carregar_jogo()
                        self.state = 'jogando'
                    # Opção 3: Sair
                    elif self.selected_menu_option == 3:
                        self.running = False


    def menu_principal_draw(self):
        self.screen.fill(BLACK)
        try:
            title_font = pygame.font.Font(MAIN_FONT, 48)
            option_font = pygame.font.Font(MAIN_FONT, 28)
        except:
            title_font = pygame.font.SysFont('arial', 48)
            option_font = pygame.font.SysFont('arial', 28)

        # Desenha o título
        title_text = title_font.render(TITULO, True, YELLOW)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.screen.blit(title_text, title_rect)

        # Desenha as opções
        for index, option in enumerate(self.menu_options):
            color = YELLOW if index == self.selected_menu_option else WHITE
            option_text = option_font.render(option, True, color)
            option_rect = option_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + index * 60))
            self.screen.blit(option_text, option_rect)

        pygame.display.flip()



    def playing_events(self):
        """
        Processa todos os eventos do jogo (teclado, mouse, fechar janela).
        """
        for event in pygame.event.get():
            # Verificação #1: O jogador quer fechar o jogo?
            if event.type == pygame.QUIT:
                self.running = False

            # Verificação #2: O jogador apertou uma tecla?
            # Este 'if' está no mesmo nível do 'if' anterior, fora dele.
            if event.type == pygame.KEYDOWN:

                # Verifica se o jogador quer pausar o jogo
                if event.key == pygame.K_p or event.key == pygame.K_q:
                    self.state = 'pausado'

                # Agora, verificamos qual tecla foi para mover o jogador
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.player.move(pygame.Vector2(-1, 0))
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player.move(pygame.Vector2(1, 0))
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.player.move(pygame.Vector2(0, -1))
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.player.move(pygame.Vector2(0, 1))

    def load_enemies(self):
        """
        Encontra as posições dos fantasmas e os cria com sprites e cooldowns individuais.
        """
        ghost_positions = self.level.find_symbol('G')
        sprite_keys = list(self.ghost_sprites.keys())

        # <<<< ADICIONADO: Lista com os tempos de cooldown em segundos, na ordem
        cooldowns = [2.0, 3.1, 4.0, 4.5, 4.6]

        for i, pos in enumerate(ghost_positions):
            if i < len(sprite_keys):
                sprite_key = sprite_keys[i]
                sprite = self.ghost_sprites[sprite_key]

                # Pega o cooldown correspondente da lista
                # Usamos o módulo (%) para o caso de haver mais fantasmas que cooldowns definidos
                cooldown = cooldowns[i % len(cooldowns)]

                # <<<< ALTERADO: Passa o cooldown individual para o construtor do Enemy
                self.ghost_queue.append(Enemy(self, (pos[1], pos[0]), sprite, cooldown))

    def playing_update(self):
        """
        Atualiza a lógica do jogo.
        """
        if self.tunnel_cooldown > 0:
            self.tunnel_cooldown -= 1
        # Se a fila não estiver vazia, contamos o tempo para liberar o próximo
        if self.ghost_queue:
            self.ghost_spawn_timer += 1
            # Se o tempo passou (convertido para frames), libera um fantasma
            if self.ghost_spawn_timer >= GHOST_SPAWN_TIME * FPS:
                self.ghost_spawn_timer = 0
                self.enemies.append(self.ghost_queue.popleft())  # Tira da fila e põe no jogo


        self.player.update()
        # Atualiza cada inimigo na lista de ativos
        for enemy in self.enemies:
            enemy.update()

        #Chamada para verificar colisões a cada frame
        self.check_collisions()

        if self.level.total_pellets == 0:
            self.state = 'vitoria_fase'



    # --- MÉTODOS DE ESTADO: VITÓRIA ---
    def vitoria_fase_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # Se apertar ENTER, volta para o menu
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.state = 'menu_principal'



    def vitoria_fase_draw(self):
        self.screen.fill(BLACK)
        try:
            font = pygame.font.Font(MAIN_FONT, 48)
            sub_font = pygame.font.Font(MAIN_FONT, UI_FONT_SIZE)
        except FileNotFoundError:
            font = pygame.font.SysFont('arial', 48)
            sub_font = pygame.font.SysFont('arial', UI_FONT_SIZE)

        title_text = font.render("FASE COMPLETA!", True, YELLOW)
        instructions_text = sub_font.render("Pressione ENTER para voltar ao menu", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        instructions_rect = instructions_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

        self.screen.blit(title_text, title_rect)
        self.screen.blit(instructions_text, instructions_rect)
        pygame.display.flip()


    def playing_draw(self):
        """
        Desenha todos os elementos na tela.
        """
        self.screen.fill(BLACK)
        self.level.draw(self.screen)
        # Chama o metodo de desenho do jogador
        self.player.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        self.draw_ui()# Garante que a UI seja desenhada por cima
        pygame.display.flip()

    def draw_ui(self):
        # Área do painel inferior
        panel_rect = pygame.Rect(UI_PANEL_POS[0], UI_PANEL_POS[1], WIDTH, HEIGHT - (GRID_HEIGHT * GRID_SIZE))
        pygame.draw.rect(self.screen, BLACK, panel_rect)  # Fundo preto para o painel

        # Tenta usar a fonte personalizada, se não encontrar, usa uma padrão
        try:
            font = pygame.font.Font(MAIN_FONT, UI_FONT_SIZE)
        except FileNotFoundError:
            font = pygame.font.SysFont('arial', UI_FONT_SIZE)

        # Desenha o Score
        score_text = font.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, HEIGHT - 40))

        # Desenha as Vidas
        lives_text = font.render(f"LIVES: ", True, WHITE)
        self.screen.blit(lives_text, (WIDTH - 180, HEIGHT - 40))

        # Desenha os ícones de vida do Pac-Man
        for i in range(self.lives):
            # Usamos o primeiro sprite da animação 'right' como ícone
            life_icon = self.player.animations['right'][0]
            # Ajusta o tamanho do ícone se necessário
            life_icon_small = pygame.transform.scale(life_icon, (GRID_SIZE - 10, GRID_SIZE - 10))
            self.screen.blit(life_icon_small, (WIDTH - 100 + (i * 35), HEIGHT - 45))

    # Dentro da classe Game

    def pausado_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                # Navega para cima nas opções
                if event.key == pygame.K_UP:
                    # O operador % (módulo) faz a seleção "dar a volta"
                    self.selected_pause_option = (self.selected_pause_option - 1) % len(self.pause_options)

                # Navega para baixo nas opções
                if event.key == pygame.K_DOWN:
                    self.selected_pause_option = (self.selected_pause_option + 1) % len(self.pause_options)

                # Seleciona a opção atual com ENTER
                if event.key == pygame.K_RETURN:
                    # Opção 0: Sair e Salvar
                    if self.selected_pause_option == 0:
                        self.save_score() #salva o score
                        self.salvar_jogo()
                        print("jogo salvo")
                        self.running = False  # Por enquanto, apenas fecha o jogo
                        

                    # Opção 1: Sair sem Salvar
                    elif self.selected_pause_option == 1:
                        self.state = 'menu_principal'  # Volta para o menu principal

                    # Opção 2: Cancelar
                    elif self.selected_pause_option == 2:
                        self.state = 'jogando'  # Volta para o jogo

                # Também permite sair da pausa com 'P' ou 'Q' (atalho para "Cancelar")
                if event.key == pygame.K_p or event.key == pygame.K_q:
                    self.state = 'jogando'

    # Dentro da classe Game

    def pausado_draw(self):

        # Agora, criamos uma camada escura semi-transparente por cima
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)  # SRCALPHA permite transparência
        overlay.fill((0, 0, 0, 170))  # Preto com 170 de alpha (0-255)
        self.screen.blit(overlay, (0, 0))

        # Define as fontes
        try:
            menu_font = pygame.font.Font(MAIN_FONT, 36)
        except FileNotFoundError:
            menu_font = pygame.font.SysFont('arial', 36)

        # Desenha as opções do menu
        for index, option in enumerate(self.pause_options):
            # Se a opção estiver selecionada, usa a cor amarela. Senão, branca.
            color = YELLOW if index == self.selected_pause_option else WHITE

            option_text = menu_font.render(option, True, color)

            # Calcula a posição de cada opção
            option_rect = option_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40 + index * 60))

            self.screen.blit(option_text, option_rect)

        pygame.display.flip()


    #IA fantasmas
    def find_path(self, start_pos, target_pos):
        """
        Encontra o caminho mais curto entre dois pontos usando o algoritmo BFS.

        :param start_pos: Tupla (x, y) da posição inicial no grid.
        :param target_pos: Tupla (x, y) da posição alvo no grid.
        :return: Lista de tuplas representando o caminho, ou None se não houver caminho.
        """
        # O mapa é o nosso grafo. Usaremos os métodos do TAD Mapa para navegar.
        grid = self.level.matrix
        # Fila para o BFS, armazena os caminhos a serem explorados
        queue = deque([[start_pos]])
        # Conjunto para guardar as posições já visitadas e evitar loops
        visited = {start_pos}

        while queue:
            # Pega o primeiro caminho da fila
            path = queue.popleft()
            # Pega o último nó (posição) desse caminho
            node = path[-1]

            # Se chegamos ao alvo, retornamos o caminho encontrado
            if node == target_pos:
                return path

            # Explora os vizinhos (Cima, Baixo, Esquerda, Direita)
            for direction in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                next_node = (node[0] + direction[0], node[1] + direction[1])

                # Verifica se o vizinho está dentro do mapa
                if (0 <= next_node[0] < self.level.width and 0 <= next_node[1] < self.level.height):
                    # Verifica se o vizinho não é uma parede e se ainda não foi visitado
                    if not self.level.is_wall(next_node[1], next_node[0]) and next_node not in visited:
                        new_path = list(path)
                        new_path.append(next_node)
                        queue.append(new_path)
                        visited.add(next_node)

        return None  # Retorna None se não encontrar um caminho

    def reset_entities(self):
        """ Reseta todas as entidades para suas posições iniciais. """
        self.player.reset()
        for enemy in self.enemies:
            enemy.reset()

    def check_collisions(self):
        """ Verifica e trata as colisões entre o jogador e os inimigos. """
        for enemy in self.enemies:
            # Calcula a distância entre o centro do jogador e o do inimigo
            dist = self.player.pixel_pos.distance_to(enemy.pixel_pos)
            # Se a distância for menor que o raio de ambos (meio GRID_SIZE), eles colidiram
            if dist < GRID_SIZE / 2:
                # Caso 1: Jogador está invencível
                if self.player.invincibility_timer > 0:
                    print("Fantasma comido!")
                    self.score += 200  # Adiciona pontos por comer o fantasma
                    enemy.reset()  # Manda o fantasma de volta para a base
                # Caso 2: Jogador está vulnerável
                else:
                    self.lives -= 1
                    print(f"Vida perdida! Vidas restantes: {self.lives}")
                    if self.lives <= 0:
                        self.state = 'game_over'
                    else:
                        # Reseta a posição de todos para continuar a rodada
                        self.reset_entities()

    # --- MÉTODOS DE ESTADO: GAME OVER ---
    def game_over_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # Se apertar ENTER, volta para o menu principal
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.save_score()
                self.state = 'menu_principal'
                # Opcional: Chamar um método de reset geral do jogo aqui, se necessário

    def game_over_draw(self):
        self.screen.fill(BLACK)
        try:
            title_font = pygame.font.Font(MAIN_FONT, 48)
            instructions_font = pygame.font.Font(MAIN_FONT, UI_FONT_SIZE)
        except FileNotFoundError:
            title_font = pygame.font.SysFont('arial', 48)
            instructions_font = pygame.font.SysFont('arial', UI_FONT_SIZE)

        title_text = title_font.render("GAME OVER", True, RED)
        score_text = instructions_font.render(f"PONTUAÇÃO FINAL: {self.score}", True, WHITE)
        instructions_text = instructions_font.render("Pressione ENTER para voltar ao menu", True, WHITE)

        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        instructions_rect = instructions_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))

        self.screen.blit(title_text, title_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(instructions_text, instructions_rect)
        pygame.display.flip()


    def save_score(self):
        """
        Salva a pontuação atual no arquivo de ranking.
        """
        # Usamos 'a' para 'append', que adiciona ao final do arquivo sem apagar o que já existe.
        try:
            with open(RANKING_FILE, 'a') as file:
                # Salva no formato "NOME PONTOS" para facilitar a leitura depois
                file.write(f"JOGADOR {self.score}\n")
            print(f"Pontuação {self.score} salva no ranking.")
        except Exception as e:
            print(f"Não foi possível salvar o score: {e}")


    def load_scores(self):
        """
        Lê o arquivo de ranking, ordena os scores e retorna os melhores.
        """
        if not os.path.exists(RANKING_FILE):
            return []  # Retorna lista vazia se o arquivo não existe

        scores = []
        try:
            with open(RANKING_FILE, 'r') as file:
                for line in file:
                    # Tenta separar a linha em nome e score. Se falhar, ignora a linha.
                    try:
                        name, score = line.strip().split()
                        scores.append((name, int(score)))
                    except ValueError:
                        continue  # Pula para a próxima linha se esta estiver mal formatada
        except Exception as e:
            print(f"Não foi possível carregar os scores: {e}")
            return []

        # A mágica da ordenação: ordena a lista de tuplas pelo segundo elemento (o score),
        # em ordem decrescente (do maior para o menor).
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)

        # Retorna apenas os 10 melhores resultados
        return sorted_scores[:10]

    # --- MÉTODOS DE ESTADO: RANKING ---
    def ranking_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # Se apertar ENTER ou ESC, volta para o menu
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE):
                self.state = 'menu_principal'

    def ranking_draw(self):
        self.screen.fill(BLACK)
        # Carrega os scores ordenados
        high_scores = self.load_scores()

        try:
            title_font = pygame.font.Font(MAIN_FONT, 36)
            score_font = pygame.font.Font(MAIN_FONT, UI_FONT_SIZE)
        except:
            title_font = pygame.font.SysFont('arial', 36)
            score_font = pygame.font.SysFont('arial', UI_FONT_SIZE)

        # Desenha o título
        title_text = title_font.render("RANKING", True, YELLOW)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)

        # Desenha cada score
        for index, (name, score) in enumerate(high_scores):
            score_text_str = f"{index + 1:2}. {name:<10} {score:>6}"
            score_text = score_font.render(score_text_str, True, WHITE)
            score_rect = score_text.get_rect(center=(WIDTH // 2, 180 + index * 40))
            self.screen.blit(score_text, score_rect)

        # Desenha instrução para voltar
        back_text = score_font.render("Pressione ENTER para voltar", True, GREY)
        back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.screen.blit(back_text, back_rect)

        pygame.display.flip()

    def salvar_jogo(self):
        save_data = {
            "score": self.score,
            "vidas": self.lives,
            "player_pos": [self.player.grid_pos.x, self.player.grid_pos.y],
            "invincibility_timer": self.player.invincibility_timer,
            "mapa": self.level.matrix,
            "ghosts_pos": [[enemy.grid_pos.x, enemy.grid_pos.y] for enemy in self.enemies] 
            }    
            
                
        with open("../assets/save.json", "w") as arquivo:
            json.dump(save_data, arquivo)

    def carregar_jogo(self):
        try:
            with open("../assets/save.json", "r") as arquivo:
                save_data = json.load(arquivo)

            self.score = save_data["score"]
            self.lives = save_data["vidas"]
            self.player.grid_pos = pygame.Vector2(save_data["player_pos"])
            self.player.pixel_pos = pygame.Vector2(
                self.player.grid_pos.x * GRID_SIZE + GRID_SIZE // 2,
                self.player.grid_pos.y * GRID_SIZE + GRID_SIZE // 2
            )
            self.player.invincibility_timer = save_data["invincibility_timer"]
            self.level.matrix = save_data["mapa"]
            
            for ghost in save_data["ghosts_pos"]:
                if self.ghost_queue:
                    self.enemies.append(self.ghost_queue.popleft())
            print(self.enemies)
            
            for i, enemy in enumerate(self.enemies):
                enemy.grid_pos.x = save_data["ghosts_pos"][i][0]
                enemy.grid_pos.y = save_data["ghosts_pos"][i][1]
                enemy.pixel_pos = pygame.Vector2(
                    enemy.grid_pos.x * GRID_SIZE + GRID_SIZE // 2,
                    enemy.grid_pos.y * GRID_SIZE + GRID_SIZE // 2
                )

            self.state = "jogando"
            print("Jogo carregado com sucesso.")

        except FileNotFoundError:
            print("Nenhum jogo salvo encontrado.")






#loop principal
    def run(self):
        while self.running:
            if self.state == 'menu_principal':
                self.menu_principal_events()
                self.menu_principal_draw()
            
            elif self.state == 'jogando':
                self.playing_events()
                self.playing_update()
                self.playing_draw()
           
            elif self.state == 'pausado':
                self.pausado_events()
                self.pausado_draw()

            elif self.state == 'game_over':
                self.game_over_events()
                self.game_over_draw()

            elif self.state == 'vitoria_fase':
                 self.vitoria_fase_events()
                 self.vitoria_fase_draw()

            elif self.state == 'exibindo_ranking':
                 self.ranking_events()
                 self.ranking_draw()

            self.clock.tick(FPS)



