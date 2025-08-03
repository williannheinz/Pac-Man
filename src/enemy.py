# Os Vilões: Lógica dos Fantasmas.

import pygame
from settings import *


class Enemy:
    def __init__(self, game, pos, image, cooldown_sec):  # <<<< ADICIONADO: cooldown_sec como parâmetro
        self.game = game
        self.grid_pos = pygame.Vector2(pos[0], pos[1])
        self.pixel_pos = pygame.Vector2(
            self.grid_pos.x * GRID_SIZE + GRID_SIZE // 2,
            self.grid_pos.y * GRID_SIZE + GRID_SIZE // 2
        )
        self.image = image
        self.rect = self.image.get_rect()
        self.starting_pos = pygame.Vector2(pos[0], pos[1]) #resetar
        
        # Carrega a sprite dos fantasmas para o modo invencivel
        img = pygame.image.load(BLUE_GHOST_SPRITE_PATH).convert_alpha()
        self.scared_sprite = pygame.transform.scale(img, (GRID_SIZE, GRID_SIZE))
        self.scared = False


        self.direction = pygame.Vector2(0, 0)
        self.speed = GHOST_SPEED
        self.path = []
        self.target_node = None

        #  Cada fantasma agora tem seu próprio tempo de cooldown
        self.pathfinding_cooldown_duration_sec = cooldown_sec
        self.pathfinding_cooldown = 0  # Começa em 0 para pensar imediatamente

    def update(self):
        """
        Atualiza a lógica de IA (pensar) e o movimento (agir) do fantasma.
        """
        # 1. LÓGICA DE "PENSAR" (acontece a cada X segundos)
        # Primeiro, decrementamos o timer de cooldown.
        if self.pathfinding_cooldown > 0:
            self.pathfinding_cooldown -= 1

        # Se o timer zerar, calculamos um novo caminho e resetamos o timer.
        if self.pathfinding_cooldown == 0:
            self.recalculate_path()
            self.pathfinding_cooldown = int(self.pathfinding_cooldown_duration_sec * FPS)


        # 2. LÓGICA DE "AGIR" (acontece a cada frame)
        # Move o fantasma em direção ao seu alvo atual.
        self.move_towards_target()
        # Determina o estado assustado
        self.scared = self.game.player.invincibility_timer > 0


    def is_on_grid_center(self):
        """ Verifica se o fantasma está próximo o suficiente do centro de uma célula. """
        return (abs(self.pixel_pos.x % GRID_SIZE - GRID_SIZE // 2) < self.speed and
                abs(self.pixel_pos.y % GRID_SIZE - GRID_SIZE // 2) < self.speed)



    def recalculate_path(self):
        """ Pede ao jogo um novo caminho até o jogador. """
        start = (int(self.grid_pos.x), int(self.grid_pos.y))
        target = (int(self.game.player.grid_pos.x), int(self.game.player.grid_pos.y))

        self.path = self.game.find_path(start, target)
        # Define o primeiro passo do caminho como o alvo imediato
        if self.path and len(self.path) > 1:
            self.target_node = pygame.Vector2(self.path[1])
        else:
            self.target_node = None  # Não há caminho, fica parado

    def move_towards_target(self):
        """ Move o fantasma continuamente em direção ao seu 'target_node'. """
        if self.target_node is None:
            return  # Se não há alvo, não faz nada

        # Calcula a posição em pixels do centro do nó alvo
        target_pixel_pos = pygame.Vector2(
            self.target_node.x * GRID_SIZE + GRID_SIZE // 2,
            self.target_node.y * GRID_SIZE + GRID_SIZE // 2
        )

        # Calcula o vetor direção para o alvo
        self.direction = (target_pixel_pos - self.pixel_pos)

        # Se estiver muito perto do alvo, "trava" nele e pega o próximo do caminho
        if self.direction.length() < self.speed:
            self.pixel_pos = target_pixel_pos  # Trava na posição exata

            # Primeiro, removemos o nó que acabamos de alcançar
            if self.path:
                self.path.pop(0)

            # AGORA, verificamos se AINDA há um caminho a seguir
            if self.path and len(self.path) > 1:
                # Se sim, definimos o novo alvo
                self.target_node = pygame.Vector2(self.path[1])
            else:
                # Se não, o caminho acabou. O fantasma espera por um novo cálculo.
                self.target_node = None

            return  # Encerra o movimento para este frame

        # Normaliza o vetor (transforma em um vetor de comprimento 1) e multiplica pela velocidade
        self.direction.normalize_ip()
        self.pixel_pos += self.direction * self.speed

        # Atualiza a posição no grid (para referência)
        # Apenas para fins de cálculo, a posição exata é a de pixels
        if self.is_on_grid_center():
            self.grid_pos = pygame.Vector2(int(self.pixel_pos.x / GRID_SIZE), int(self.pixel_pos.y / GRID_SIZE))

    def draw(self, screen):
        self.rect.center = self.pixel_pos
        if self.scared:
            screen.blit(self.scared_sprite, self.rect)
            
        else:
            screen.blit(self.image, self.rect)



    def reset(self):
        """ Reseta o inimigo para sua posição e estado iniciais. """
        self.grid_pos = pygame.Vector2(self.starting_pos.x, self.starting_pos.y)
        self.pixel_pos = pygame.Vector2(
            self.grid_pos.x * GRID_SIZE + GRID_SIZE // 2,
            self.grid_pos.y * GRID_SIZE + GRID_SIZE // 2
        )
        self.direction = pygame.Vector2(0, 0)
        self.path = []
        self.target_node = None