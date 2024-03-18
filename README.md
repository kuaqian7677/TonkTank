user kuaqian7677 => Pongsaton SaeFung 6610110188
user LomerAlloys => Sarankorn Chaisuntranon 6610110289
# How to play

W - move up
A - move left
S - move down
D - move right
Mouse Right Click - Fire bullet

# about game
Player will control the hero( tank character ) and player able to fire the bullet when 'MOUSE1' is clicked.

when the bullet hit the enemy, it will decrease the enemy's HP and it when the enemy HP <= 0, the enemy will be removed from the game and player gain the score.

Player can collect a random buff to gain some special ability.

# Function 
- move_step():
        Move player when keys is pressed.
        
- move_bullets():
  Move all bullets in game. 
  when bullets hit the enemy it will decrease the enemy HP and play hitsound.

- restart_game()
reset all the stats and the timer to the start point.

- detect_collision()
the logic function to check if the object collide on other object.

- move_enemys()
the logic of the enemy's movement.

- spawnEnemyRed(), spawnEnemyGreen(),...
the logic about spawning the enemy







