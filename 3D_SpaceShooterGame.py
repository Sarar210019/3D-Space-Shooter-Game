from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random

win_width =1000
win_height= 800
lives=5
speed=10
score_inc= 100
spawnRate= 0.0004
bulletSpeed =10
MAX_BULLETS =50

FONT=GLUT_BITMAP_HELVETICA_18
LARGE_FONT=GLUT_BITMAP_TIMES_ROMAN_24

class GameState:
    def __init__(self):
        self.reset()
        self.stars=[]
        self.planets=[]
        self.generate_space_objects()

    def reset(self):

        self.camera_mode="third_person"

        self.player_pos=[0, 0, 0] #start at centre

        self.lives=lives

        self.score=0

        self.game_active=True
        self.enemies =[]

        self.bullets =[]

        self.difficulty_level=1
        self.last_shot_time=0
        self.shoot_cooldown=0.1

    def generate_space_objects(self):
        for i in range(500):
            x = random.uniform(-1000, 1000)
            y = random.uniform(-1000, 1000)
            z = random.uniform(-2000, 2000)

            self.stars.append((x, y, z))
        

        for i in range(5):
            angle=random.uniform(0,2*math.pi)
            distance=random.uniform(500,1500)
            self.planets.append({
                'x':distance*math.cos(angle),
                'y':distance*math.sin(angle),
                'z':random.uniform(-3000,-500),
                'size':random.uniform(30,80),
                'color':(random.uniform(0.3,1), 
                          random.uniform(0.3,1), 
                          random.uniform(0.3,1))})

game_state=GameState()


def draw_space_background():
    glPointSize(2)
    
    glBegin(GL_POINTS)
    glColor3f(1,1,1)
    for star in game_state.stars:
        glVertex3f(*star)
    glEnd()

    # Draw sun
    glPushMatrix()
    glTranslatef(-800, 500, -1500)
    glColor3f(1, 0.8, 0.2)
    glutSolidSphere(100, 20, 20)
    glPopMatrix()

    # Draw planets
    for planet in game_state.planets:
        glPushMatrix()
        glTranslatef(planet['x'], planet['y'], planet['z'])
        glColor3f(*planet['color'])
        glutSolidSphere(planet['size'], 20, 20)
        glPopMatrix()

def draw_text(x, y, text, font=FONT):
    color_sc=(1, 1, 1)
    glColor3f(*color_sc)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, win_width, 0, win_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

###################DRAWING THE SHIP############

def draw_player():
    glPushMatrix()
    glTranslatef(*game_state.player_pos)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    #body
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.8,0.1,0.1,1])  # Red color
    glMaterialf(GL_FRONT, GL_SHININESS, 50)
    glPushMatrix()
    glScalef(1, 0.5, 2)
    glutSolidSphere(15, 20, 20)
    glPopMatrix()

    #Nose
    quad = gluNewQuadric()
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.2,0.6,1, 1])  #Blue color
    glMaterialf(GL_FRONT, GL_SHININESS, 50)
    glPushMatrix()
    glTranslatef(0,0,30)
    glRotatef(-90,1,0,0)
    gluCylinder(quad,0.1,8,15,10,10)
    glPopMatrix()

    #Wings
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.8,0.8,0.1,1])  #Yellow color
    glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(side * 20, -5, 0)
        glScalef(2, 0.2, 0.5)
        glutSolidCube(10)
        glPopMatrix()

    #tail drawing
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.2,0.6,1,1])  # Blue color
    glMaterialf(GL_FRONT,GL_SHININESS,50)
    glPushMatrix()
    glTranslatef(0,5,-25)
    glRotatef(-90,1,0,0)
    gluCylinder(quad,4,1,20,10,10)
    glPopMatrix()

    gluDeleteQuadric(quad)
    glDisable(GL_LIGHTING)
    glPopMatrix()

def draw_enemies():
    quad = gluNewQuadric()
    for enemy in game_state.enemies:
        glPushMatrix()
        glTranslatef(enemy['x'], enemy['y'], enemy['z'])
        glRotatef(enemy['rotation'],1,1,1)   #planet rotation control
        
        #Planet body
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [.839, .682, 0.149, .7]) #orange color
        glutSolidSphere(enemy['size'], 10, 10)
        
        #Planet ring 
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1,0,0,1])
        glRotatef(90, 1, 0, 0)
        glutSolidTorus(enemy['size']/3, enemy['size'],10,10)
        
        glPopMatrix()
    gluDeleteQuadric(quad)

def draw_bullets():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glPointSize(8)
    glBegin(GL_POINTS)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, [1,1,1,1])
    for bullet in game_state.bullets:
        glVertex3f(bullet['x'], bullet['y'], bullet['z'])
    glEnd()

def spawn_enemy():
    if random.random() < spawnRate * game_state.difficulty_level:
        x = random.uniform(-500, 500)
        y = random.uniform(-500, 500)
        z = -1000 
        game_state.enemies.append({
            'x': x,
            'y': y,
            'z': z,
            'speed':random.uniform(.2, .3) * game_state.difficulty_level, #game SPEED CONTROLL
            'size':random.uniform(40,50) ,         #PLANET SIZE CONTROLL
            'rotation':0,
            'health':game_state.difficulty_level
        })

def update_enemies():
    for enemy in game_state.enemies[:]:
        enemy['z']+= enemy['speed']
        
        #enemy stays in hand
        enemy['x'] = max(-400, min(400, enemy['x']))
        enemy['y'] = max(-250, min(250, enemy['y']))
        
        enemy['rotation']=(enemy['rotation']+0.5) % 360    #PLANET ROTATION CONTROLL
        
        dx =game_state.player_pos[0] -enemy['x']
        dy =game_state.player_pos[1] -enemy['y']
        dz =game_state.player_pos[2] -enemy['z']
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist < 30:
            handle_collision()
            game_state.enemies.remove(enemy)

def fire_bullet():
    current_time = glutGet(GLUT_ELAPSED_TIME) / 1000
    if (current_time - game_state.last_shot_time) < game_state.shoot_cooldown:
        return
    
    if len(game_state.bullets) < MAX_BULLETS:
        game_state.bullets.append({
            'x': game_state.player_pos[0],
            'y': game_state.player_pos[1],
            'z': game_state.player_pos[2]-25,
            'dir_x': 0,
            'dir_y': 0,
            'dir_z': -1,
            'speed': bulletSpeed
        })
        game_state.last_shot_time = current_time

def update_bullets():
    for bullet in game_state.bullets[:]:
        bullet['x']+=bullet['dir_x'] *bullet['speed']
        bullet['y']+=bullet['dir_y'] *bullet['speed']
        bullet['z']+=bullet['dir_z'] *bullet['speed']
        
        if bullet['z'] < -1000:
            game_state.bullets.remove(bullet)
            continue
            
        #Check collisions
        for enemy in game_state.enemies[:]:
            dist = math.sqrt((bullet['x']-enemy['x'])**2 + (bullet['y']-enemy['y'])**2 + (bullet['z']-enemy['z'])**2)
            if dist < enemy['size']:
                enemy['health'] -= 3
                if enemy['health'] <= 0:
                    game_state.score += score_inc
                    game_state.enemies.remove(enemy)
                if bullet in game_state.bullets:
                    game_state.bullets.remove(bullet)
                break

def handle_collision():
    game_state.lives -= 1
    if game_state.lives <= 0:
        game_state.game_active = False

def update_difficulty():
    passed = game_state.score//score_inc
    game_state.difficulty_level = 1+passed//5

def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(105, win_width / win_height, 1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    #fpp
    if game_state.camera_mode == "first_person":
        eye_x = game_state.player_pos[0]
        eye_y = game_state.player_pos[1]+5
        eye_z = game_state.player_pos[2]+20 
        
        center_x = game_state.player_pos[0]
        center_y = game_state.player_pos[1]
        center_z = game_state.player_pos[2]-100
        
        gluLookAt(eye_x, eye_y, eye_z,center_x, center_y, center_z,0, 1, 0)
    else:
        #Tpp view
        eye_x = game_state.player_pos[0]
        eye_y = game_state.player_pos[1]+50
        eye_z = game_state.player_pos[2]+100
        
        center_x = game_state.player_pos[0]
        center_y = game_state.player_pos[1]
        center_z = game_state.player_pos[2]
        
        gluLookAt(eye_x, eye_y, eye_z,center_x, center_y, center_z,0,1,0)

def keyboard_listener(key, x, y):
    if not game_state.game_active and key == b'r':
        game_state.reset()
    elif key == b'w':
        if game_state.player_pos[1] < 250:
            game_state.player_pos[1] += 10
    elif key == b's':
        if game_state.player_pos[1] > -250:
            game_state.player_pos[1] -= 10
    elif key == b'a':
        if game_state.player_pos[0] > -400:
            game_state.player_pos[0] -= 10
    elif key == b'd':
        if game_state.player_pos[0] < 400:
            game_state.player_pos[0] += 10
    elif key == b' ':
        fire_bullet()
    elif key == b'p':
        game_state.game_active = not game_state.game_active
    elif key == b'v':
        if game_state.camera_mode == "third_person":
            game_state.camera_mode = "first_person"
        else:
            game_state.camera_mode = "third_person"



def idle():
    if not game_state.game_active:
        return
        
    spawn_enemy()
    update_enemies()
    update_bullets()
    update_difficulty()
    glutPostRedisplay()

def show_screen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, win_width, win_height)
    setup_camera()
    

    glDisable(GL_LIGHTING)
    draw_space_background()
    glEnable(GL_LIGHTING)
    
#scoreboard
    draw_text(10, win_height - 60, f"Lives: {game_state.lives}  Score: {game_state.score}", font=FONT)
    draw_text(10, win_height - 90, f"Level: {game_state.difficulty_level}", font=FONT)
    draw_text(10, win_height - 120, f"View: {'First-Person' if game_state.camera_mode == 'first_person' else 'Third-Person'}", font=FONT)

    if not game_state.game_active:
        draw_text(win_width // 2 - 150, win_height // 2, "GAME OVER - Press R to Restart", font=LARGE_FONT, color=(1, 0, 0))
    else:
        draw_enemies()
        draw_bullets()
        if game_state.camera_mode == "third_person":
            draw_player()

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(win_width, win_height)
    glutCreateWindow(b"Space Shooter 3D")
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glClearColor(0.02, 0.02, 0.05, 1) 
    
    # Configure lighting
    glLightfv(GL_LIGHT0, GL_POSITION, [-800, 500, -500, 1])  # Position light
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.1, 0.1, 0.1, 1])
    
    glutDisplayFunc(show_screen)
    glutKeyboardFunc(keyboard_listener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == '__main__':
    main()