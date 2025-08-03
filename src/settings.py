
# src/settings.py
import pygame
import os

# =========================================================================================
# 1. CONFIGURAÇÕES GERAIS DA TELA E DO JOGO
# =========================================================================================
TITULO = "Pacman"
FPS = 60  # Taxa de quadros por segundo para um movimento suave

# O requisito é um mapa 20x20. Vamos definir o tamanho de cada "bloco" do grid
# e calcular a largura e altura da tela a partir disso.
GRID_SIZE = 30  # Tamanho de cada célula do grid em pixels
GRID_WIDTH = 22   # Largura do grid conforme o requisito
GRID_HEIGHT = 20  # Altura do grid conforme o requisito

# Largura da tela calculada a partir do grid
WIDTH = GRID_WIDTH * GRID_SIZE
# Altura da tela. Adicionamos um espaço extra na parte inferior para UI (pontos, vidas)
HEIGHT = GRID_HEIGHT * GRID_SIZE + 50


# =========================================================================================
# 2. CORES (PALETA DO JOGO)
# =========================================================================================
# Usar constantes para cores facilita a manutenção e garante consistência.
# Formato: (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE_WALL = (0, 0, 255)  # Cor para as paredes do labirinto
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GREY = (128, 128, 128)


# =========================================================================================
# 3. CAMINHOS DE ARQUIVOS (ASSETS)
# =========================================================================================
# Vamos construir os caminhos de forma que funcionem em qualquer computador.
# Pega o caminho absoluto do diretório onde este arquivo (settings.py) está.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# A pasta raiz do projeto está um nível "acima" da pasta 'src'
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Agora, construímos os caminhos a partir da raiz do projeto
ASSETS_FOLDER = os.path.join(PROJECT_ROOT, 'assets')
MAPS_FOLDER = os.path.join(ASSETS_FOLDER, 'maps')
FONTS_FOLDER = os.path.join(ASSETS_FOLDER, 'fonts')

# Exemplo de arquivo de fonte
MAIN_FONT = os.path.join(FONTS_FOLDER, 'press-start-2p.ttf')
# Arquivo para salvar o ranking
RANKING_FILE = os.path.join(PROJECT_ROOT, 'ranking.txt')


# =========================================================================================
# 4. CONFIGURAÇÕES DO JOGADOR (PAC-MAN)
# =========================================================================================
PLAYER_START_LIVES = 3
# A velocidade deve ser um divisor do GRID_SIZE para um movimento preciso no grid.
# Ex: Com GRID_SIZE=30 e PLAYER_SPEED=2, o Pac-Man levará 15 frames para cruzar uma célula.
PLAYER_SPEED = 2


# =========================================================================================
# 5. CONFIGURAÇÕES DOS INIMIGOS (FANTASMAS)
# =========================================================================================
GHOST_SPEED = 2.1
# Tempo em segundos que os fantasmas ficam assustados após o Pac-Man comer um power-up.
SCARED_TIME = 20
# Tempo em segundos para o próximo fantasma sair da "fila" e entrar no jogo.
# Isso se relaciona diretamente com o requisito do "TAD Cenário".
GHOST_SPAWN_TIME = 5


# =========================================================================================
# 6. CONFIGURAÇÕES DA INTERFACE (UI)
# =========================================================================================
UI_FONT_SIZE = 20
UI_VERTICAL_MARGIN = 10
# Posição do painel da UI (na parte inferior da tela)
UI_PANEL_POS = (0, GRID_HEIGHT * GRID_SIZE)

# =========================================================================================
# 7. CAMINHOS DOS SPRITES (NOVO BLOCO)
# =========================================================================================
ART_FOLDER = os.path.join(ASSETS_FOLDER, 'pacman-art')

# Subpastas para cada direção
PACMAN_UP_FOLDER = os.path.join(ART_FOLDER, 'pacman-up')
PACMAN_DOWN_FOLDER = os.path.join(ART_FOLDER, 'pacman-down')
PACMAN_LEFT_FOLDER = os.path.join(ART_FOLDER, 'pacman-left')
PACMAN_RIGHT_FOLDER = os.path.join(ART_FOLDER, 'pacman-right')

# Caminho para a pasta dos fantasmas
GHOSTS_FOLDER = os.path.join(ART_FOLDER, 'ghosts')
BLUE_GHOST_SPRITE_PATH = os.path.join(ART_FOLDER, 'blue_ghost.png')

# =========================================================================================
# 8. CONFIGURAÇÕES DE JOGABILIDADE (NOVA SEÇÃO)
# =========================================================================================
TUNNEL_COOLDOWN_SEC = 1.5 # Tempo em segundos que os túneis ficam inativos após o uso


#sons
SOUNDS_FOLDER = os.path.join(ASSETS_FOLDER, 'sounds')