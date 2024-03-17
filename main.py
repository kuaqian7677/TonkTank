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
        direction = Vector(x,y) - Vector(self.posX, self.posY)
        direction = direction.normalize()
        self.position = Vector(self.position) + direction * self.speed * ms
        self.posX = self.position[0]
        self.posY = self.position[1]
        self.angle = 1
        return self.position

def clamp(n, min, max): 
    if n < min: 
        return min
    elif n > max: 
        return max
    else: 
        return n
    
hpBarsizeX = 100
hpBarOffsetY = 80
heroSize = 50

class Coin:
    def __init__(self, position):
        self.position = position
        self.size = (30, 30)  # Adjust size as needed
        self.collected = False
        self.rect = None  # Placeholder for the Rectangle object

    def spawn(self, canvas):
        # Method to spawn the coin on the canvas
        self.canvas = canvas
        with self.canvas:
            self.rect = Rectangle(source='asset/Bullets/coin.png', pos=self.position, size=self.size)

    def collect(self):
        # Method to collect the coin
        if not self.collected:
            self.collected = True
            self.canvas.remove(self.rect)
            return True
        return False

class BackgroundLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(BackgroundLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'
        super(BackgroundLayout, self).__init__(**kwargs)
        self.timer_label = Label(text="Timer: 0", size_hint=(None, None), size=(100, 40), font_size=20)
        self.add_widget(self.timer_label)
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

        with self.health_bar_layout.canvas:
            Color(1, 1, 1, 0.6)
            self.force_field = Rectangle(source="asset/Bullets/forceField.png", pos=(0,0), size=(1, 1))
        
        # Label for HP text
        self.hp_label = Label(text=f'HP: {self.game_widget.heroHp} / {self.game_widget.maxHp}', pos=self.health_background.pos, size=(20, 20),font_size=40)
        self.health_bar_layout.add_widget(self.hp_label)

        self.score_label = Label(text="Score: 0", size_hint=(None, None), size=(100, 40), pos_hint={'center_x': 0.5, 'top': 1},font_size=40)
        self.add_widget(self.score_label)
        
        self.shield_label = Label(text="", size_hint=(None, None), size=(100, 40), pos_hint={'center_x': 0.5, 'top': 1},font_size=40)
        self.add_widget(self.shield_label)

        
        #self.health_bar = ProgressBar(max=10, size_hint=(None, None), size=(200, 20), pos_hint={'x': 0.5, 'y': 0.05}) 
        #self.health_bar_layout.add_widget(self.health_bar)
        

    def _update_rect(self, instance, value):
        self.rect.size = self.size
        self.rect.pos = self.pos
       

    def update_Player_Stats(self, d10):
        # Update the size of the foreground rectangle based on hero's health
        health_percent = clamp(self.game_widget.heroHp / self.game_widget.maxHp, 0, self.game_widget.maxHp) 
        print(health_percent)
        self.health_background.pos = (self.game_widget.hero1.posX - (hpBarsizeX/2) + (heroSize/2),self.game_widget.hero1.posY + hpBarOffsetY)
        self.health_foreground.pos = (self.game_widget.hero1.posX- (hpBarsizeX/2)  + (heroSize/2),self.game_widget.hero1.posY + hpBarOffsetY)
        
        self.health_foreground.size = (health_percent * hpBarsizeX, 20)
        self.hp_label.text = f'HP: {self.game_widget.heroHp} / {self.game_widget.maxHp}'
        self.hp_label.pos=(0,0)
        self.score_label.text = f"Score: {self.game_widget.score}"
        window_width, window_height = Window.size
        self.score_label.pos = (window_width/2 -50, window_height - 40)

        shieldText = ""
        self.force_field.size=(1, 1)
        if self.game_widget.heroShield > 0:
            self.force_field.size=(80, 80)
            shieldText = f"Shield: {self.game_widget.heroShield:.1f}"
        self.shield_label.text = shieldText
        self.shield_label.pos = (window_width/2 -50,  40)

        self.force_field.pos = (self.game_widget.hero1.posX - 20, self.game_widget.hero1.posY - 20)

class Enemy:
    def __init__(self, startPosition, image, size, hp ,firerate, speed, bulletSpeed, damage, bs):
        self.enemyTank = allMovingEntity(startPosition[0],startPosition[1],speed)
        self.enemyRect = Rectangle(source=image, pos=(self.enemyTank.posX, self.enemyTank.posY), size=(size, size))
        self.hp = hp
        self.firerate = firerate
        self.lastShot = time.time() 
        self.score = 10
        self.bulletSpeed = bulletSpeed
        self.damage = damage
        self.bulletSize = bs
        print("Created enemy")

class Explosive:
    def __init__(self, canvas,startPosition, image, size):
        self.timeStart = time.time()
        self.size = size
        with canvas:
            self.explosiveBall = Ellipse(source='asset/Bullets/bulletYellow2.png',pos=(startPosition[0] - size/2,startPosition[1]- size/2), size=(size, size))

class RandomBuff:
    def __init__(self, startPosition):
        buffId = random.randint(1,3)
        self.buffId = buffId
        if buffId == 1:
            self.buffRect = Rectangle(source="asset/Bullets/shield.png", pos=(startPosition[0],startPosition[1]), size=(40,40))
        elif buffId == 2:
            self.buffRect = Rectangle(source="asset/Bullets/wrenchRepair.png", pos=(startPosition[0],startPosition[1]), size=(40,40))
        else:
            self.buffRect = Rectangle(source="", pos=(startPosition[0],startPosition[1]), size=(1,1))
        print("Created buff")

class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)
        self.pressed_keys = set()
        self.hero_speed = 200  # Set the default hero speed
        self.initial_hero_speed = self.hero_speed  # Store initial hero speed
        self.move_clock_event = None  # Initialize move clock event
        self.start_move_clock()
        self.hitsound = SoundLoader.load('sound/osu-hit-sound.mp3')
        
        

        Clock.schedule_interval(self.spawn_coin, 2)  # Spawn a coin every 2 seconds
        self.coins = []

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
        self.maxHp = 10
        self.score = 0
        self.heroDamage = 5
        self.heroShield = 0

        with self.canvas:
            self.hero = Rectangle(source='asset/Tanks/tankBlue2.png', pos=(self.hero_x, self.hero_y), size=(heroSize, heroSize))

        self.bullets = []
        self.enemyBullets = []
        self.enemys = []
        self.explosiveEffect = []
        self.randomBuff = []
        ENEMY_TANK_NUMBER = 0
        for i in range(ENEMY_TANK_NUMBER):
            newEnemy = Enemy(self.randomGeneratePosition("Null"),"image", 50, 10,0.9, 40, 100) # Enemy(startPosition, image, size, health, firerate) --setting new enemy here
            self.canvas.add(newEnemy.enemyRect)
            self.enemys.append(newEnemy)
        Clock.schedule_interval(self.playExplosion, 1/30)

    def spawn_coin(self, dt):
            # Method to spawn a new coin
            window_width, window_height = Window.size
            coin_pos = (random.randint(0, window_width - 30), random.randint(0, window_height - 30))
            coin = Coin(coin_pos)
            coin.spawn(self.canvas)  # Pass the canvas object when spawning
            self.coins.append(coin)

    def collect_coins(self):
            # Method to check for collisions between hero and coins and collect them
            player_rect = self.hero  # Assuming hero is the player's Rectangle
            for coin in self.coins:
                if not coin.collected and self.detect_collision(player_rect, coin.rect):
                    if coin.collect():
                        self.score += 100  # Increase player's score by 100

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

    def randomPosition(self, g):
        window_width, window_height = Window.size
        x = random.randint(100,window_width-100)
        y = random.randint(100,window_height-100)
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
        newEnemy = Enemy(newpos,'asset/Tanks/tankRed2.png', 50, 10,1, 40, 100,1, 10) # Enemy(startPosition, image, size, health, firerate, speed, bullet speed, damage) --setting new enemy here
        self.canvas.add(newEnemy.enemyRect)
        self.enemys.append(newEnemy)

    def spawnEnemyGreen(self, dt):
        newpos = self.randomGeneratePosition("Null")
        print(newpos)
        newEnemy = Enemy(newpos,'asset/Tanks/tankGreen2.png', 70, 40,3, 10, 50,2, 15) # Enemy(startPosition, image, size, health, firerate, speed, bullet speed) --setting new enemy here
        self.canvas.add(newEnemy.enemyRect)
        self.enemys.append(newEnemy)
    
    def generateRandomBuff(self, dt):
        newpos = self.randomPosition("Null")
        print(newpos)
        newBuff = RandomBuff(newpos) # Enemy(startPosition, image, size, health, firerate, speed, bullet speed) --setting new enemy here
        self.canvas.add(newBuff.buffRect)
        self.randomBuff.append(newBuff)

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
        step = self.hero_speed * dt #100 * dt  # //add the speed here
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

        self.collect_coins()
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
        bullet = Rectangle(source='asset/Bullets/bulletRed2.png', pos=start_pos, size=(enemyEntity.bulletSize, enemyEntity.bulletSize))
            # Add rotation instruction
        bulletSpeed = enemyEntity.bulletSpeed
        rotation_angle = 0  # Set your desired rotation angle here
        with self.canvas:
            PushMatrix()
            Rotate(angle=rotation_angle, origin=(self.hero1.posX,self.hero1.posY ))
            self.canvas.add(bullet)
            PopMatrix()
        # Append bullet and its direction
        damage = enemyEntity.damage
        self.enemyBullets.append((bullet, direction, bulletSpeed, damage))
    
    def move_bullets(self, dt):
        for bullet, direction in self.bullets:
            bullet.pos = Vector(*bullet.pos) + direction * 600 * dt  # adjust bullet speed hereaaa
            # Check for collisions between bullet and enemies
            for enemy in self.enemys:
                if self.detect_collision(bullet, enemy.enemyRect):
                    if self.hitsound:
                        self.hitsound.volume = 0.25
                        self.hitsound.play()
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
        for bullet, direction, bulletSpeed, damage in self.enemyBullets:
            bullet.pos = Vector(*bullet.pos) + direction * bulletSpeed * dt  # adjust bullet speed here
            if self.detect_collision(bullet, self.hero):
                # Remove bullet from the canvas
                if self.heroShield > 0:
                    self.heroShield -= damage
                else:
                    self.heroHp -= damage
                self.canvas.remove(bullet)
                self.enemyBullets.remove((bullet, direction, bulletSpeed, damage))

                if self.heroHp <= 0:
                    print("GAME OVER")
                    self.restart_game()  # Call method to restart the game
                    return

        for buff in self.randomBuff:
            if self.detect_collision(buff.buffRect, self.hero):
                # Remove bullet from the canvas
                if buff.buffId == 1:
                    self.heroShield += 10
                    
                elif buff.buffId == 2:
                    self.maxHp += 0.5
                    hp = clamp(self.heroHp + 5, 0, self.maxHp) 
                    self.heroHp = hp
                self.canvas.remove(buff.buffRect)
                self.randomBuff.remove(buff)  
        shield = clamp(self.heroShield - 1/120, 0, 999) 
        
        self.heroShield = shield

    def restart_game(self):

        app = App.get_running_app()
        app.elapsed_time = 0
        
        # Reset hero attributes
        self.heroHp = 10
        self.maxHp = 10
        self.heroDamage = 5
        self.heroShield = 0
        self.hero_speed = self.initial_hero_speed 
        
        # Clear lists of bullets, enemy bullets, enemies, explosive effects, and random buffs
        self.bullets = []
        self.enemyBullets = []
        self.enemys = []
        self.explosiveEffect = []
        self.randomBuff = []

        # Clear canvas of all remaining elements
        self.canvas.clear()
        if self.move_clock_event:
            self.move_clock_event.cancel()

        # Call any necessary methods to initialize the game again
        self.__init__()

    def start_move_clock(self):
        # Start the clock event for hero movement
        self.move_clock_event = Clock.schedule_interval(self.move_step, 1/60)

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
        self.bg_music = SoundLoader.load('sound/Demo Song.mp3')
        if self.bg_music:
            self.bg_music.volume = 0.25
            self.bg_music.loop = True  # Loop the background music
            self.bg_music.play()
        bgLayout = BackgroundLayout()
        game = bgLayout.game_widget
        self.elapsed_time = 0

        Clock.schedule_interval(self.update_timer, 1)
        Clock.schedule_interval(game.move_bullets, 1/60)  
        Clock.schedule_interval(game.move_enemys, 1/60) 
        Clock.schedule_interval(bgLayout.update_Player_Stats, 1/60)
        Clock.schedule_interval(game.generateRandomBuff, 10)
        Clock.schedule_interval(game.spawnEnemyRed, 2)
        Clock.schedule_interval(game.spawnEnemyGreen, 3)
        return bgLayout
    
    def update_timer(self, dt):
        # Update elapsed time
        self.elapsed_time += 1

        # Update timer label
        bgLayout = self.root
        bgLayout.timer_label.text = f"Timer: {self.elapsed_time}"

if __name__ == '__main__':
    app = MyApp()
    app.run()