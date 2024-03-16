from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.vector import Vector
import math
import random


class allMovingEntity:
    def __init__(self, x,y, speed):
        self.posX = x
        self.posY = y
        self.position = (self.posX, self.posY)
        self.speed = speed

    def moveTo(self, x, y, ms):
        diffy = y - self.posY
        diffx = x - self.posX 
        print(diffx, diffy)
        

        direction = Vector(x,y) - Vector(self.posX, self.posY)
        direction = direction.normalize()
        self.position = Vector(self.position) + direction * self.speed * ms
        self.posX = self.position[0]
        self.posY = self.position[1]
        print(self.position)
        return self.position



        


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
        
        with self.canvas:
            self.hero = Rectangle(source='asset/Tanks/tankBlue.png', pos=(self.hero_x, self.hero_y), size=(50, 50))

        self.bullets = []
        self.enemys = []
        ENEMY_TANK_NUMBER = 2
        for i in range(ENEMY_TANK_NUMBER):
            enemyTank = allMovingEntity(random.randint(100,400),random.randint(100,400),50)
            enemyColor = Rectangle(source='asset/Tanks/tankRed.png', pos=(enemyTank.posX, enemyTank.posY), size=(50, 50))
            target = [10,10]
            self.enemys.append((enemyTank, enemyColor,target))
            self.canvas.add(enemyColor)


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

    def move_enemys(self, dt):
         for enemy, enemyRect,targetPos in self.enemys:
            targetPos = [self.hero1.posX,self.hero1.posY]
            enemy.moveTo(targetPos[0], targetPos[1],1/60)
            enemyRect.pos = enemy.position
            

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
        game = GameWidget()
        Clock.schedule_interval(game.move_bullets, 1/60)  
        Clock.schedule_interval(game.move_enemys, 1/60)  
        return game

if __name__ == '__main__':
    app = MyApp()
    app.run()
