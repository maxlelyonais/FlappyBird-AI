import pygame
import random
import sys
from pygame.locals import *
import os
import neat
import pickle
import time

WHITE = (250,250,250)
WIDTH = 500
HEIGHT = 700
BIRD_RADIUS = 20
JUMP = -6
Gravity = 0.3
SEPARATION = 100
SPEED = 3
GEN = 0

path = os.getcwd()

# Initialize Pygame
pygame.init()
surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")


filename2 = "BirdAnimation"

Reset_path = os.path.join(path,"OIP.jpg")
Quit_path = os.path.join(path,"QUIT.jpg")
Bird_path = os.path.join(path,"Bird.jpg")

BirdAnimation1 = os.path.join(path,filename2,"bird1.1.png")
BirdAnimation2  = os.path.join(path,filename2,"bird1.2.png")
BirdAnimation3  = os.path.join(path,filename2,"bird1.3.png")
BirdAnimation4  = os.path.join(path,filename2,"bird1.4.png")

Reset_image = pygame.image.load(Reset_path).convert_alpha()
Quit_image = pygame.image.load(Quit_path).convert_alpha()
Bird_image = pygame.image.load(Bird_path).convert_alpha()

FlappyBirdAnimation = [
    pygame.image.load(BirdAnimation1),
    pygame.image.load(BirdAnimation2),
    pygame.image.load(BirdAnimation3),
    pygame.image.load(BirdAnimation4)
]


class Button():

    def __init__(self,x,y,image,screen, scale):

        width = image.get_width()
        height = image.get_height()
        self.screen = screen

        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.clicked = False
        
    def draw(self):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True

            if pygame.mouse.get_pressed()[0] and self.clicked == True:
                self.clicked = False
                action = True

        self.screen.blit(self.image,(self.rect.x,self.rect.y))

        return action

class Bird():
    COLOR = WHITE

    def __init__(self,x,y,radius,Velocity):
        self.x = x
        self.y = y
        self.radius = radius
        self.Velocity = Velocity

    def controller(self,key):
    
        self.key = key

        if self.key == pygame.K_SPACE:
            self.Velocity = JUMP
            
        self.Velocity += Gravity
        self.y += self.Velocity

        if self.y >= HEIGHT:
            self.y = HEIGHT
        
    def draw( self,win,image,scale):

        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x,self.y)
        win.blit(self.image,(self.rect.x,self.rect.y))
        
class obstacles():
    
    def newObstacle(self):
        Posibilities = []
        for i in range(HEIGHT//50):
            Posibilities.append(i)
        self.random_element = random.choice(Posibilities)

        self.upper_height = self.random_element * 50
        self.lower_Point = self.random_element*50 + SEPARATION

    x = 500

    def draw( self,win ):

        if( self.random_element == 13 ):
            pygame.draw.rect( win,(255,255,255),((self.x,0),(40, self.random_element*50-100)) )
            pygame.draw.rect( win,(255,255,255),((self.x,self.random_element*50+SEPARATION),(40,HEIGHT-SEPARATION-self.random_element)) )
        else:
            pygame.draw.rect( win,(255,255,255),((self.x,0),(40, self.random_element*50)) )
            pygame.draw.rect( win,(255,255,255),((self.x,self.random_element*50+SEPARATION),(40,HEIGHT-SEPARATION-self.random_element)) )

    def moving( self,speed ):

        self.speed = speed
        self.x-=self.speed



def Score(surface,score,gen):

    font = pygame.font.SysFont("ccomicsans",20)
    text = str(score)
    text2 = font.render(text,1,(255,255,255))
    text3 = str(gen)
    text4 = font.render(text3,1,(255,255,255))
    surface.blit(text2,(WIDTH//2-text2.get_width()//2,HEIGHT//4 - text2.get_height()//2))
    surface.blit(text4,(WIDTH//2-text4.get_width()//2 - 50, HEIGHT//4 - text4.get_height()//2))

def reset(bird,obstacle):

    bird.x = WIDTH//2
    bird.y = HEIGHT//2
    obstacle.x = 500

    return 0,0,0.3


def DeathWindow(surface,score):
    
    Reset_Button = Button(WIDTH*0.75//4,HEIGHT//2,Reset_image,surface, 0.25)
    Quit_Button = Button(WIDTH*2.5//4,HEIGHT//2,Quit_image,surface, 0.25)
    
    surface.fill( (0,0,0) )
    font = pygame.font.SysFont( "ccomicsans",35 )
    DeathMessage = f"You have Died, your punctuation is {score}"
    text2 = font.render( DeathMessage,1,(255,255,255) )
    
    surface.blit(text2,(WIDTH//2-text2.get_width()//2,HEIGHT//2 - text2.get_height()//2 - 125))

    if Reset_Button.draw() == True:
        return True
   
    if Quit_Button.draw() == True:
        return False
    
    pygame.display.update()

    ## We run the game a certain amount of times in order to make it work.
def train_ai(genomes,config):
    global GEN
    GEN += 1
    nets = [] 
    ge = []
    birds = []
    
    for _, g in genomes:

        ##Set up a neural network for a genome and then link it to a bird.
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(WIDTH//2,HEIGHT//2,BIRD_RADIUS,0))
        g.fitness = 0
        ge.append(g)

    pygame.init()
    run = True
    score = 0
    obstacle = obstacles()
    Hit = False

    pygame.display.set_caption("Flappy Bird")

    frame_index = 0
    frame_rate = 10

    clock= pygame.time.Clock()
    obstacle = obstacles()
    time = 0 
    animation = True
    
    while run:

        clock.tick(60)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        surface.fill((0,0,0)) 

        if len(birds) == 0:
            run = False
            break

        if score > 50:
            break

        if time % 200 == 0:
                obstacle = obstacles()
                obstacle.newObstacle()
                Scored = False
            
        if time % 10 == 0:
            frame_index = ( (frame_index + 1) % len(FlappyBirdAnimation) )

        for x,bird in enumerate(birds):
                ge[x].fitness += 0.1

                ## IT activates the genome and select the best option among all the other ones
                output = nets[x].activate((bird.y, abs(bird.y - obstacle.upper_height), abs(bird.y - obstacle.lower_Point)))

                if output[0] > 0.5:
                    bird.controller(pygame.K_SPACE)
                else:
                    bird.controller(pygame.K_0)
            

            ## We can get the position of the bird the list
        for x,bird in enumerate(birds):
            
            bird.draw(surface,FlappyBirdAnimation[frame_index],1.5)

            if bird.x >= obstacle.x and Scored == False:
                score+=1
                for g in ge:
                    g.fitness +=5
                Scored = True

            if bird.y >= HEIGHT:
                ge[x].fitness -=1
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

            if bird.y <= obstacle.upper_height and bird.x >= obstacle.x and bird.x <= obstacle.x + 50:
                ge[x].fitness -=1
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
        
            if bird.y >= obstacle.lower_Point  and bird.x >= obstacle.x and bird.x <= obstacle.x + 50:
                ge[x].fitness -=1
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
                
        obstacle.draw(surface) 
        obstacle.moving(SPEED)

        time+=1
            
        Score(surface,score,GEN)
        pygame.display.flip()


def test_ai(net):

    pygame.init()
    run = True
    score = 0
    obstacle = obstacles()
    Hit = False
    bird = Bird(WIDTH//2,HEIGHT//2,BIRD_RADIUS,0)

    pygame.display.set_caption("Flappy Bird")

    frame_index = 0
    frame_rate = 10

    clock= pygame.time.Clock()
    obstacle = obstacles()
    time = 0 
    animation = True
    
    while run:

        clock.tick(60)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        if Hit == False:
            surface.fill((0,0,0)) 

            if score > 50:
                break

            if time % 200 == 0:
                    obstacle = obstacles()
                    obstacle.newObstacle()
                    Scored = False
                
            if time % 10 == 0:
                frame_index = ( (frame_index + 1) % len(FlappyBirdAnimation) )

            output = net.activate((bird.y, abs(bird.y - obstacle.upper_height), abs(bird.y - obstacle.lower_Point)))

            if output[0] > 0.5:
                bird.controller(pygame.K_SPACE)
            else:
                bird.controller(pygame.K_0)
                
            bird.draw(surface,FlappyBirdAnimation[frame_index],1.5)

            if bird.x >= obstacle.x and Scored == False:
                score+=1
                Scored = True

            if bird.y >= HEIGHT:
                Hit = True
                    
            if bird.y <= obstacle.upper_height and bird.x >= obstacle.x and bird.x <= obstacle.x + 50:
                Hit = True
            
            if bird.y >= obstacle.lower_Point  and bird.x >= obstacle.x and bird.x <= obstacle.x + 50:
                Hit = True

            obstacle.draw(surface) 
            obstacle.moving(SPEED)

            time+=1
                
            Score(surface,score,GEN)
            pygame.display.flip()

        elif Hit == True:
            DeathWindow(surface,score)


def test_best_network(config):
    config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,neat.DefaultStagnation,config_path)
    with open("best.pickle", "rb") as f:
        winner = pickle.load(f)
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)

    pygame.display.set_caption("FlappyBird")
    test_ai(winner_net)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,neat.DefaultStagnation,config_path)
    p = neat.Population(config)
    ##It gave us all the details
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(train_ai,50)
    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)

if __name__ =="__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    run(config_path)
    ##test_best_network(config_path)