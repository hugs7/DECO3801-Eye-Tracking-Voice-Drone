import pygame

def init():
    pygame.init()
    window = pygame.display.set_mode((400, 400))

def getKey():
    # Returns a key pressed by the user in the terminal
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            return event.key
    return None

def main():
    key = getKey()
    if key:
        print(f"Key pressed: {pygame.key.name(key)}")

if __name__ == '__main__':
    init()
    while True:
        main()
