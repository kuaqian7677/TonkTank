from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.vector import Vector
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image

from kivy.graphics.context_instructions import PopMatrix, PushMatrix, Transform, Rotate

import math
import random


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
        print(self.angle)
        #print(self.position)
        return self.position

class BackGround(Widget):
    pass

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

    def _update_rect(self, instance, value):
        self.rect.size = self.size
        self.rect.pos = self.pos

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

        with self.canvas:
            self.hero = Rectangle(source='asset/Tanks/tankBlue.png', pos=(self.hero_x, self.hero_y), size=(50, 50))

        self.bullets = []
        self.enemys = []
        ENEMY_TANK_NUMBER = 2
        for i in range(ENEMY_TANK_NUMBER):
            enemyTank = allMovingEntity(random.randint(100,400),random.randint(100,400),50)
            #enemyColor = Rectangle(source='asset/Tanks/tankRed.png', pos=(enemyTank.posX, enemyTank.posY), size=(50, 50), angle=0)
            with self.canvas:
                PushMatrix()
                enemyColor = Rectangle(source='asset/Tanks/tankRed.png', pos=(enemyTank.posX, enemyTank.posY), size=(50, 50))
                Rotate(angle=100)
                PopMatrix()
            target = [10,10]
            self.enemys.append((enemyTank, enemyColor,target))
        


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
            bullet = Rectangle(source='asset/Bullets/bulletSilverSilver_outline.png', pos=start_pos, size=(10, 10))
            self.bullets.append((bullet, direction))  # Store bullet and its direction
            self.canvas.add(bullet)
    
    def move_bullets(self, dt):
        for bullet, direction in self.bullets:
            bullet.pos = Vector(*bullet.pos) + direction * 600 * dt  # adjust bullet speed here
            
            # Check for collisions between bullet and enemies
            for enemy, enemyRect, targetPos in self.enemys:
                if self.detect_collision(bullet, enemyRect):
                    # Remove bullet from the canvas
                    self.canvas.remove(bullet)
                    self.bullets.remove((bullet, direction))
                    
                    # Remove enemy from the canvas and enemy list
                    self.canvas.remove(enemyRect)
                    self.enemys.remove((enemy, enemyRect, targetPos))
                    break 

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
        for i, (enemy1, enemyRect1, targetPos1) in enumerate(self.enemys):
            targetPos1 = [self.hero1.posX, self.hero1.posY]
            enemy1.moveTo(targetPos1[0], targetPos1[1], 1 / 60)
            enemyRect1.pos = enemy1.position
            for j, (enemy2, enemyRect2, targetPos2) in enumerate(self.enemys):
                if i != j and self.detect_collision(enemyRect1, enemyRect2):
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
            print(mousePos)
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
        
        return bgLayout

if __name__ == '__main__':
    app = MyApp()
    app.run()
