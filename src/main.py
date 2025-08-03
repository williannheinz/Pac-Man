# RODA O JOGO

# src/main.py

# Importa as bibliotecas necessárias
import pygame
import sys

# Importa a classe principal do jogo que contém toda a lógica
from game import Game

class Main:
    """
    Classe principal que inicializa e executa o jogo.
    """
    def __init__(self):
        # Cria uma instância da classe Game
        self.game = Game()

    def run(self):
        # Chama o metodo que contém o loop principal do jogo
        self.game.run()

# O bloco de código que será executado quando você rodar "python src/main.py"
if __name__ == '__main__':
    # Cria uma instância da classe Main
    main = Main()
    # Inicia a execução do jogo
    main.run()

    # Garante que o Pygame seja finalizado corretamente ao sair do loop
    pygame.quit()
    sys.exit()
