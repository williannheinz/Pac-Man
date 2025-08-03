#O Herói: Lógica do Pacman.

# src/player.py

import pygame
import os
from settings import *


class Player:
    def __init__(self, game, pos):
        """
        Construtor da entidade Player (Pac-Man).
        """
        self.game = game
        self.grid_pos = pygame.Vector2(pos[0], pos[1])
        self.pixel_pos = pygame.Vector2(
            self.grid_pos.x * GRID_SIZE + GRID_SIZE // 2,
            self.grid_pos.y * GRID_SIZE + GRID_SIZE // 2
        )
        self.direction = pygame.Vector2(0, 0)  # Começa virado para a direita
        self.stored_direction = None
        self.speed = PLAYER_SPEED
        self.starting_pos = pygame.Vector2(pos[0], pos[1]) #colisões/resetar


        # --- LÓGICA DE ANIMAÇÃO ---
        self.animations = {}  # Dicionário para guardar as listas de sprites
        self.load_animations()

        self.current_frame_index = 0
        self.image = self.animations['right'][self.current_frame_index]  # Imagem atual a ser desenhada
        self.rect = self.image.get_rect()  # Retângulo da imagem, para posicionamento

        self.animation_timer = 0
        self.animation_speed_ms = 80  # Tempo em milissegundos para cada frame da animação


        # Campo do TAD Entidade: tempo restante de invencibilidade
        self.invincibility_timer = 0  # 0 significa que não está invencível


    def load_animations(self):
        """
        Carrega todas as imagens de animação do Pac-Man a partir das pastas.
        """
        # Mapeia a direção para a pasta correspondente e a lista de sprites
        directions = {
            'right': (PACMAN_RIGHT_FOLDER, []),
            'left': (PACMAN_LEFT_FOLDER, []),
            'up': (PACMAN_UP_FOLDER, []),
            'down': (PACMAN_DOWN_FOLDER, [])
        }

        for direction, (folder_path, image_list) in directions.items():
            # Pega todos os arquivos da pasta, ignorando subdiretórios
            filenames = sorted([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])

            for filename in filenames:
                # Carrega a imagem
                img = pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
                # Redimensiona a imagem para o tamanho do nosso grid
                scaled_img = pygame.transform.scale(img, (GRID_SIZE, GRID_SIZE))
                image_list.append(scaled_img)

        self.animations = {direction: data[1] for direction, data in directions.items()}

    # Dentro da classe Player (src/player.py)

    def update(self):
        """
        Atualiza a posição, estado e animação do jogador, com cooldown de túnel.
        """
        # 1. Processa timers, como o de invencibilidade
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1
            if self.invincibility_timer == 0:
                print("Modo invencível ACABOU.")

        # 2. Só permitimos decisões de movimento quando o jogador está alinhado no grid
        if self.is_on_grid_center():
            # <<<< LÓGICA DO TÚNEL ATUALIZADA >>>>
            current_grid_pos_tuple = (int(self.grid_pos.y), int(self.grid_pos.x))
            # VERIFICAÇÃO 1: O jogador está em um portal E o cooldown está zerado?
            if current_grid_pos_tuple in self.game.level.tunnels and self.game.tunnel_cooldown == 0:
                # Se for, teletransporta o jogador
                destination = self.game.level.tunnels[current_grid_pos_tuple]
                self.grid_pos = pygame.Vector2(destination[1], destination[0])
                self.pixel_pos = pygame.Vector2(
                    self.grid_pos.x * GRID_SIZE + GRID_SIZE // 2,
                    self.grid_pos.y * GRID_SIZE + GRID_SIZE // 2
                )

                # VERIFICAÇÃO 2: Ativa o cooldown geral do jogo
                self.game.tunnel_cooldown = int(TUNNEL_COOLDOWN_SEC * FPS)
                return  # Encerra o update deste frame para evitar outros movimentos

            # Se não estiver em um túnel (ou se o túnel estiver em cooldown), processa o input
            if self.stored_direction:
                next_pos_grid = self.grid_pos + self.stored_direction
                if not self.game.level.is_wall(int(next_pos_grid.y), int(next_pos_grid.x)):
                    self.direction = self.stored_direction
            self.stored_direction = None

            # Verifica se a direção atual vai bater numa parede
            next_pos_grid = self.grid_pos + self.direction
            if self.game.level.is_wall(int(next_pos_grid.y), int(next_pos_grid.x)):
                self.direction = pygame.Vector2(0, 0)

        # 3. Move o jogador em pixels
        self.pixel_pos += self.direction * self.speed

        # 4. Atualiza a posição no grid e interage com itens
        new_grid_pos = pygame.Vector2(int(self.pixel_pos.x / GRID_SIZE), int(self.pixel_pos.y / GRID_SIZE))
        if new_grid_pos != self.grid_pos:
            self.grid_pos = new_grid_pos
            self.eat_item()

        # 5. Atualiza a animação
        if self.direction.x != 0 or self.direction.y != 0:
            self.animate()




    def animate(self):
        """ Controla a troca de frames da animação. """
        self.animation_timer += self.game.clock.get_time()  # Adiciona o tempo passado

        if self.animation_timer > self.animation_speed_ms:
            self.animation_timer = 0  # Reseta o timer
            # Avança para o próximo frame, voltando ao início se chegar ao fim
            self.current_frame_index = (self.current_frame_index + 1) % len(
                self.animations[self.get_current_direction_key()])

        # Atualiza a imagem atual com base no frame e na direção
        self.image = self.animations[self.get_current_direction_key()][self.current_frame_index]

    def draw(self, screen):
        """
        Desenha o sprite atual do Pac-Man na tela.
        """
        # Atualiza a posição do retângulo da imagem para o centro da posição em pixels
        self.rect.center = self.pixel_pos
        # Desenha a imagem na tela
        screen.blit(self.image, self.rect)

    def move(self, direction):
        """
        Armazena a próxima direção que o jogador deseja se mover.
        """
        self.stored_direction = direction

    def is_on_grid_center(self):
        """ Verifica se o jogador está próximo o suficiente do centro de uma célula. """
        return (abs(self.pixel_pos.x % GRID_SIZE - GRID_SIZE // 2) < self.speed and
                abs(self.pixel_pos.y % GRID_SIZE - GRID_SIZE // 2) < self.speed)

    def get_current_direction_key(self):
        """ Retorna a chave de string ('up', 'down', etc.) para a direção atual. """
        if self.direction.x == 1: return 'right'
        if self.direction.x == -1: return 'left'
        if self.direction.y == -1: return 'up'
        if self.direction.y == 1: return 'down'

        # Se estiver parado (direction é 0,0), usa a última direção armazenada
        # para que a imagem não mude para 'right' toda vez que ele para.
        if self.stored_direction:
            if self.stored_direction.x == 1: return 'right'
            if self.stored_direction.x == -1: return 'left'
            if self.stored_direction.y == -1: return 'up'
            if self.stored_direction.y == 1: return 'down'

        return 'right'  # Retorna 'right' como um padrão seguro no início do jogo

    # No final da classe Player (src/player.py)

    def eat_item(self):
        """
        Verifica se há um item na posição atual do jogador e o consome.
        """
        # Pega a posição no grid, garantindo que sejam inteiros para usar como índice da matriz
        grid_x = int(self.grid_pos.x)
        grid_y = int(self.grid_pos.y)

        # Usa o TAD Mapa para consultar o que há na célula
        tile = self.game.level.get_tile(grid_y, grid_x)

        item_eaten = False  # Flag para saber se algo foi comido
        if tile == '.':  # Se for um pontinho
            # Usa o TAD Mapa para remover o item (troca por espaço vazio)
            self.game.level.set_tile(grid_y, grid_x, ' ')
            # Aumenta a pontuação no TAD Cenário (a classe Game)
            self.game.score += 10
            item_eaten = True

        elif tile == 'o':  # Se for um power-up
            self.game.level.set_tile(grid_y, grid_x, ' ')
            self.game.score += 50
            self.activate_invincibility()
            item_eaten = True

        # <<<< ADICIONADO: Decrementa o contador se um item foi comido
        if item_eaten:
            self.game.level.total_pellets -= 1


    def activate_invincibility(self):
        """
        Ativa o timer de invencibilidade do jogador.
        """
        # Converte o tempo em segundos (de settings.py) para frames
        # Ex: 7 segundos * 60 FPS = 420 frames de invencibilidade
        self.invincibility_timer = SCARED_TIME * FPS
        print("MODO INVENCÍVEL ATIVADO!")  # Mensagem de teste

    # metodo de resetar o jogador
    def reset(self):
        """ Reseta o jogador para sua posição e estado iniciais. """
        self.grid_pos = pygame.Vector2(self.starting_pos.x, self.starting_pos.y)
        self.pixel_pos = pygame.Vector2(
            self.grid_pos.x * GRID_SIZE + GRID_SIZE // 2,
            self.grid_pos.y * GRID_SIZE + GRID_SIZE // 2
        )
        self.direction = pygame.Vector2(0, 0)
        self.stored_direction = None
