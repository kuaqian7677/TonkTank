from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle ,Color, Rotate, Ellipse
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.vector import Vector
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.uix.floatlayout import FloatLayout
from kivy.utils import get_color_from_hex
from kivy.uix.label import Label

from kivy.graphics.context_instructions import PopMatrix, PushMatrix, Transform, Rotate

import math
import random
import time 


class allMovingEntity:
    def __init__(self, x,y, speed):
        self.posX = x
        self.posY = y
        self.position = (self.posX, self.posY)
        self.speed = speed
        self.angle = 0


    def get_angle(self, x,y):

        try:
            angle = math.degrees(
                math.atan(
                    (self.center_y - y)
                    / (self.center_x - x)
                )
            )
        except Exception as e:
            return 0

        if angle > 0:
            return angle

        return 180 + angle

    def moveTo(self, x, y, ms):
        diffy = y - self.posY
        diffx = x - self.posX 
        #print(diffx, diffy)
        

        direction = Vector(x,y) - Vector(self.posX, self.posY)
        direction = direction.normalize()
        self.position = Vector(self.position) + direction * self.speed * ms
        self.posX = self.position[0]
        self.posY = self.position[1]
        self.angle = 1#self.get_angle(x,y)
        #print(self.angle)
        #print(self.position)
        return self.position

hpBarsizeX = 100
hpBarOffsetY = 80
heroSize = 50

def clamp(n, min, max): 
    if n < min: 
        return min
    elif n > max: 
        return max
    else: 
        return n






class BackgroundLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(BackgroundLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'
        # Load the background image
        with self.canvas.before:
            self.bg = Image(source='asset/Environment/grass.png').texture
            self.rect = Rectangle(size=self.size, pos=self.pos, texture=self.bg)
            self.bind(size=self._update_rect, pos=self._update_rect)
        
        # Add GameWidget as a child
        self.game_widget = GameWidget()
        self.add_widget(self.game_widget)

        # Add health bar
        self.health_bar_layout = FloatLayout(size_hint=(1, None), height=40)
        self.add_widget(self.health_bar_layout)

        
        # Custom background rectangle
        with self.health_bar_layout.canvas:
            Color(1, 0, 0, 1)  # Red color
            self.health_background = Rectangle(pos= self.game_widget.hero1.position, size=(hpBarsizeX, 20))

        # Custom foreground rectangle
        with self.health_bar_layout.canvas:
            Color(0, 1, 0, 1)  # Green color
            self.health_foreground = Rectangle(pos= self.game_widget.hero1.position, size=(0, 20))
        
        # Label for HP text
        self.hp_label = Label(text=f'HP: {self.game_widget.heroHp}', pos=self.health_background.pos, size=(20, 20),font_size=40)
        self.health_bar_layout.add_widget(self.hp_label)

        self.score_label = Label(text="Score: 0", size_hint=(None, None), size=(100, 40), pos_hint={'center_x': 0.5, 'top': 1},font_size=40)
        self.add_widget(self.score_label)
        
        #self.health_bar = ProgressBar(max=10, size_hint=(None, None), size=(200, 20), pos_hint={'x': 0.5, 'y': 0.05}) 
        #self.health_bar_layout.add_widget(self.health_bar)
        

    def _update_rect(self, instance, value):
        self.rect.size = self.size
        self.rect.pos = self.pos
       

    def update_Player_Stats(self, d10):
        # Update the size of the foreground rectangle based on hero's health
        health_percent = clamp(self.game_widget.heroHp / 10, 0, 10) 
        self.health_background.pos = (self.game_widget.hero1.posX - (hpBarsizeX/2) + (heroSize/2),self.game_widget.hero1.posY + hpBarOffsetY)
        self.health_foreground.pos = (self.game_widget.hero1.posX- (hpBarsizeX/2)  + (heroSize/2),self.game_widget.hero1.posY + hpBarOffsetY)
        
        self.health_foreground.size = (health_percent * hpBarsizeX, 20)
        self.hp_label.text = f'HP: {self.game_widget.heroHp}'
        self.hp_label.pos=(0,0)
        self.score_label.text = f"Score: {self.game_widget.score}"
        window_width, window_height = Window.size
        self.score_label.pos = (window_width/2 -50, window_height - 40)

class Enemy:
    def __init__(self, startPosition, image, size, hp ,firerate, speed, bulletSpeed):
        self.enemyTank = allMovingEntity(startPosition[0],startPosition[1],speed)
        self.enemyRect = Rectangle(source=image, pos=(self.enemyTank.posX, self.enemyTank.posY), size=(size, size))
        self.hp = hp
        self.firerate = firerate
        self.lastShot = time.time() 
        self.score = 10
        self.bulletSpeed = bulletSpeed
        print("Created enemy")

class Explosive:
    def __init__(self, canvas,startPosition, image, size):
        self.timeStart = time.time()
        self.size = size
        with canvas:
            self.explosiveBall = Ellipse(source='asset/Bullets/bulletYellow2.png',pos=(startPosition[0] - size/2,startPosition[1]- size/2), size=(size, size))
            



class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)
        self.pressed_keys = set()
        Clock.schedule_interval(self.move_step, 0)

        self.sound = SoundLoader.load('test.mp3')
        self.sound.play()

        # calculate for middle spawn point
        window_width, window_height = Window.size
        self.screen_Width = window_width
        self.screen_Height = window_height
        hero_width, hero_height = 50, 50
        self.hero_x = (window_width - hero_width) / 2
        self.hero_y = (window_height - hero_height) / 2
        
        self.hero1 = allMovingEntity((window_width - hero_width) / 2,(window_height - hero_height) / 2, 100)
        self.heroHp = 10
        self.score = 0
        self.heroDamage = 5

        with self.canvas:
            self.hero = Rectangle(source='asset/Tanks/tankBlue2.png', pos=(self.hero_x, self.hero_y), size=(heroSize, heroSize))

        self.bullets = []
        self.enemyBullets = []
        self.enemys = []
        self.explosiveEffect = []
        ENEMY_TANK_NUMBER = 0
        for i in range(ENEMY_TANK_NUMBER):
            newEnemy = Enemy(self.randomGeneratePosition("Null"),"image", 50, 10,0.9, 40, 100) # Enemy(startPosition, image, size, health, firerate) --setting new enemy here
            self.canvas.add(newEnemy.enemyRect)
            self.enemys.append(newEnemy)
        Clock.schedule_interval(self.playExplosion, 1/30)

    def randomGeneratePosition(self, g):
        topOrSide = random.randint(1,2)
        x = 0
        y = 0
        window_width, window_height = Window.size
        if topOrSide == 1: #Spawn from TOP&BOTTOM
            x = math.floor(random.randint(0,window_width))
            y = math.floor(random.randint(0,1)*window_height)

            return (x, y)
        elif topOrSide == 2:
            y = math.floor(random.randint(0,window_height))
            x = math.floor(random.randint(0,1)*window_width)

            return (x, y)

    def spawnEnemy(self, dt):
        newpos = self.randomGeneratePosition("Null")
        print(newpos)
        newEnemy = Enemy(newpos,'asset/Tanks/tankRed2.png', 50, 10,0.5, 40, 100) # Enemy(startPosition, image, size, health, firerate, speed, bullet speed) --setting new enemy here
        self.canvas.add(newEnemy.enemyRect)
        self.enemys.append(newEnemy)

    def spawnEnemyRed(self, dt):
        newpos = self.randomGeneratePosition("Null")
        print(newpos)
        newEnemy = Enemy(newpos,'asset/Tanks/tankRed2.png', 50, 10,0.5, 40, 100) # Enemy(startPosition, image, size, health, firerate, speed, bullet speed) --setting new enemy here
        self.canvas.add(newEnemy.enemyRect)
        self.enemys.append(newEnemy)

    def spawnEnemyGreen(self, dt):
        newpos = self.randomGeneratePosition("Null")
        print(newpos)
        newEnemy = Enemy(newpos,'asset/Tanks/tankGreen2.png', 40, 10,1, 10, 300) # Enemy(startPosition, image, size, health, firerate, speed, bullet speed) --setting new enemy here
        self.canvas.add(newEnemy.enemyRect)
        self.enemys.append(newEnemy)

    def playExplosion(self, dt):
        for explosion in self.explosiveEffect:
            print(explosion.size)

            explosion.explosiveBall.size = (0.1,0.1)
            self.explosiveEffect.remove(explosion)

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        print('down', text)
        self.pressed_keys.add(text)

    def _on_key_up(self, keyboard, keycode):
        text = keycode[1]
        print('up', text)
        if text in self.pressed_keys:
            self.pressed_keys.remove(text)

    def move_step(self, dt):
        cur_x, cur_y = self.hero1.position
        #self.heroHp = random.randint(1,10) --Debugging Hp Bar
        step = 1#100 * dt  # //add the speed here
        if 'w' in self.pressed_keys:
            cur_y += step
        if 's' in self.pressed_keys:
            cur_y -= step
        if 'a' in self.pressed_keys:
            cur_x -= step
        if 'd' in self.pressed_keys:
            cur_x += step
        self.hero1.moveTo(cur_x, cur_y,1/60)
        self.hero.pos = self.hero1.position
        #print(self.hero1.position)
        #self.hero.pos = (cur_x, cur_y)

    def on_touch_down(self, touch):
        if touch.button == 'left':
            direction = Vector(touch.pos) - Vector(self.hero1.posX + 20, self.hero1.posY + 20)
            direction = direction.normalize()

            # bullet start pos = hero's current pos
            start_pos = (self.hero1.posX + 20, self.hero1.posY + 20)

            #create bullet
            bullet = Rectangle(source='asset/Bullets/bulletYellow2.png', pos=start_pos, size=(10, 10))
            # Add rotation instruction

            rotation_angle = 0  # Set your desired rotation angle here
            with self.canvas:
                PushMatrix()
                Rotate(angle=rotation_angle, origin=(self.hero1.posX,self.hero1.posY ))
                self.canvas.add(bullet)
                PopMatrix()

            # Append bullet and its direction
            self.bullets.append((bullet, direction))

    def enemyShoot(self,enemyEntity ):
        if (time.time() - enemyEntity.lastShot) <= enemyEntity.firerate:
            return
        else:
            enemyEntity.lastShot = time.time() 
        direction = Vector(self.hero1.posX, self.hero1.posY ) - Vector(enemyEntity.enemyTank.position)
        direction = direction.normalize()
            # bullet start pos = hero's current pos
        start_pos = (enemyEntity.enemyTank.posX + 20, enemyEntity.enemyTank.posY + 20)

            #create bullet
        bullet = Rectangle(source='asset/Bullets/bulletRed2.png', pos=start_pos, size=(10, 10))
            # Add rotation instruction
        bulletSpeed = enemyEntity.bulletSpeed
        rotation_angle = 0  # Set your desired rotation angle here
        with self.canvas:
            PushMatrix()
            Rotate(angle=rotation_angle, origin=(self.hero1.posX,self.hero1.posY ))
            self.canvas.add(bullet)
            PopMatrix()
        # Append bullet and its direction
        
        #Fire rate
        self.enemyBullets.append((bullet, direction, bulletSpeed))
    
    def move_bullets(self, dt):
        for bullet, direction in self.bullets:
            bullet.pos = Vector(*bullet.pos) + direction * 600 * dt  # adjust bullet speed here
            
            # Check for collisions between bullet and enemies
            for enemy in self.enemys:
                if self.detect_collision(bullet, enemy.enemyRect):
                    # Remove bullet from the canvas
                    newExplosion = Explosive(self.canvas, bullet.pos, "Image", 50)
                    self.explosiveEffect.append(newExplosion)


                    self.canvas.remove(bullet)
                    self.bullets.remove((bullet, direction))
                    enemy.hp -= self.heroDamage

                    if enemy.hp <= 0:
                        # Remove enemy from the canvas and enemy list
                        self.score += enemy.score
                        self.canvas.remove(enemy.enemyRect)
                        self.enemys.remove(enemy)
                        break 
        for bullet, direction, bulletSpeed in self.enemyBullets:
            bullet.pos = Vector(*bullet.pos) + direction * bulletSpeed * dt  # adjust bullet speed here
            if self.detect_collision(bullet, self.hero):
                # Remove bullet from the canvas
                self.heroHp -= 1
                if self.heroHp <= 0:
                    print("GAME OVER")
                self.canvas.remove(bullet)
                self.enemyBullets.remove((bullet, direction, bulletSpeed))

    
                

    def detect_collision(self, rect1, rect2):
        x1, y1 = rect1.pos
        w1, h1 = rect1.size
        x2, y2 = rect2.pos
        w2, h2 = rect2.size

        if (x1 < x2 + w2 and x1 + w1 > x2 and
            y1 < y2 + h2 and y1 + h1 > y2):
            return True
        return False

    def move_enemys(self, dt):
        for i, enemy1 in enumerate(self.enemys):
            
            enemy1.enemyTank.moveTo(self.hero1.posX, self.hero1.posY, 1 / 60)
            enemy1.enemyRect.pos = enemy1.enemyTank.position
            self.enemyShoot(enemy1)
            for j, enemy2 in enumerate(self.enemys):
                if i != j and self.detect_collision(enemy1.enemyRect, enemy2.enemyRect):
                    # Collision detected, but do not take any action
                    pass


    def avoid_overlap(self, enemy1, rect1, enemy2, rect2):
        """Adjust the position of enemy1 to avoid overlap with enemy2."""
        direction = Vector(rect2.pos) - Vector(rect1.pos)
        enemy1.position = Vector(enemy1.position) - direction * self.speed * 1/60
        rect1.pos = enemy1.position
            #enemyRect.angle = enemy.angle

            

    def on_motion(self, etype, me):
        # will receive all motion events.
        #print(etype)
        mousePos = [me.spos[0]*Window.size[0], me.spos[1]*Window.size[1]]
        if etype == "update":
            #print(mousePos)
            return mousePos
        elif etype == "begin":
            print("Click at",mousePos)
            
 
    Window.bind(on_motion=on_motion)


class MyApp(App):
    def build(self):
        bgLayout = BackgroundLayout()
        game = bgLayout.game_widget


        Clock.schedule_interval(game.move_bullets, 1/60)  
        Clock.schedule_interval(game.move_enemys, 1/60) 
        Clock.schedule_interval(bgLayout.update_Player_Stats, 1/60)
        Clock.schedule_interval(game.spawnEnemyRed, 1)
        Clock.schedule_interval(game.spawnEnemyGreen, 1.5)
        return bgLayout

if __name__ == '__main__':
    app = MyApp()
    app.run()
