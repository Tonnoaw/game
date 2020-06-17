from scene import *
import sound
import random
import math
A = Action

class Laser(SpriteNode):
    def __init__(self, txture, object, **kwargs):
        SpriteNode.__init__(self, txture, **kwargs)
        self.shooter = object

class Heart(SpriteNode):
    def __init__(self, **kwargs):
        SpriteNode.__init__(self, 'plf:HudHeart_full', **kwargs)

class Enemy(SpriteNode):
    def __init__(self, txture, **kwargs):
        SpriteNode.__init__(self, txture, **kwargs)
        self.time = 0
        allow_move = random.choice(('x', 'y'))
        self.allow_move = allow_move
        
class MyScene (Scene):
    def __init__(self, bg, player_txt):
        Scene.__init__(self)
        self.bg = bg
        self.player_txt = player_txt
        
        
    def setup(self):
        #scale the button according to screen size
        self.screen_scale = (self.size.w * 0.16) / 256; self.object_scale = self.size.h * (1 / 834)
        #position of button according to screen size
        self.joy_pos = (self.size.h * 0.25, self.size.h * 0.25)
        self.move = 'up'; self.player_score = 0; self.touch_id_location = {}; self.touched = False;
        self.laser_on_screen = []; self.enemy_on_screen = []; self.player_health = 100; self.game_playing = True
        self.heart_on_screen = []; self.shown = False
        bg = Node(parent = self)
        for x in range(math.ceil(self.size.x / 128) + 1):
            for y in range(math.ceil(self.size.y / 128) + 1):
                tile = SpriteNode(Texture(self.bg), position = (x * 128, y *128)); bg.add_child(tile)
        self.score = LabelNode(f'Score: {self.player_score}', ('Arial Rounded MT Bold', 30), position = (120, self.size.h - 30)); self.add_child(self.score)
        self.player_health_label = LabelNode(f'Health: {self.player_health}', ('Arial Rounded MT Bold', 30), position = (self.size.w - 120, self.size.h - 30)); self.add_child(self.player_health_label)
        self.player = SpriteNode(Texture(self.player_txt), position = (self.size.w / 2, self.size.h / 2), scale = self.object_scale)
        self.add_child(self.player)
        self.joy_layout = SpriteNode(Texture('iow:ios7_circle_outline_256'), position = self.joy_pos, alpha = 0.25, scale = self.screen_scale)
        self.add_child(self.joy_layout)
        self.shoot_button = SpriteNode(Texture('iow:ios7_circle_filled_256'), position = (self.size.w- self.joy_pos[0], self.joy_pos[1]), scale = 0.5, alpha = 0.25); self.add_child(self.shoot_button)
    
    def update(self):
        if self.game_playing:
            if self.touched:
                touch_location = self.touch_id_location.get(self.touch_in_joy)
                self.move_ship()
            if len(self.laser_on_screen) > 0:
                for laser in self.laser_on_screen:
                    if laser.position.x > self.size.w or laser.position.y > self.size.h or laser.position.x < 0 or laser.position.y < 0 :
                        self.laser_on_screen.remove(laser)
                        laser.remove_from_parent()
            self.spawn_enemy()
            self.check_collision()
            self.score.text = f'Score: {self.player_score}'
            self.player_health_label.text = f'Health: {self.player_health}'
            self.move_enemy()
            self.spawn_heart_pack()
            self.check_player_get_heart()
        if self.player_health <= 0:
            self.game_playing = False
            self.joy_layout.remove_from_parent()
            self.shoot_button.remove_from_parent()
            for enemy in self.enemy_on_screen:
                enemy.remove_from_parent()
            for laser in self.laser_on_screen:
                laser.remove_from_parent()
            for heart in self.heart_on_screen:
                heart.remove_from_parent()
            self.player.remove_from_parent()
            if not self.shown:
                self.lose_scene()
                self.shown = True
    
    def lose_scene(self):
        sound.play_effect('arcade:Explosion_4')
        self.lose_label = LabelNode('LOSE!', ('<System-Bold>', 60), position = (self.size.w /2, self.size.h / 2 + 50)); self.add_child(self.lose_label)
        self.score_label = LabelNode(f'Score: {self.player_score}', ('<System-Bold>', 50), position = (self.size.w /2, self.size.h / 2 - 50)); self.add_child(self.score_label)
    
    def check_player_get_heart(self):
        for heart in self.heart_on_screen:
            if self.player.frame.intersects(heart.frame):
                self.heart_on_screen.remove(heart)
                heart.remove_from_parent()
                sound.play_effect('arcade:Powerup_1')
                self.player_health += 15
                        
    def touch_began(self, touch):
        self.touch_id_location[touch.touch_id] = touch.location
        if touch.location in self.joy_layout.frame and not self.touched:
            self.joy_layout.run_action(A.sequence(A.scale_to(self.screen_scale * 1.25, 0.025)))
            self.joy_layout.position = touch.location
            self.touch_in_joy = touch.touch_id
            self.joy = SpriteNode(Texture('iow:ios7_circle_filled_256'), position = touch.location, alpha = 0.25, scale = 0.25 * self.object_scale)
            self.add_child(self.joy)
            self.test = SpriteNode(Texture('iow:ios7_circle_filled_256'), position = touch.location, scale = 0.25 *self.object_scale)
            self.add_child(self.test)
            self.touched = True
            
        if touch.location in self.shoot_button.frame:
            sound.play_effect('digital:Laser2')
            self.shoot_button.run_action(A.sequence(A.scale_to(0.4, 0.05), A.scale_to(0.5, 0.05)))
            self.shoot_laser(self.player.position, 'spc:LaserBlue9', self.player, self.move)
            
            
    def touch_moved(self, touch):
        self.touch_id_location[touch.touch_id] = touch.location
        try:
            if touch.touch_id == self.touch_in_joy:
                self.joy.position = touch.location
        except AttributeError:
            pass
            
    def touch_ended(self, touch):
        self.touch_id_location.pop(touch.touch_id)
        try:
            if touch.touch_id == self.touch_in_joy:
                self.joy.remove_from_parent()
                self.joy_layout.run_action(A.sequence(A.scale_to(self.screen_scale, 0.025)))
                self.joy_layout.position = (self.joy_pos)
                self.touched = False
                self.test.remove_from_parent()
        except AttributeError:
            pass
            
    def move_ship(self):
        move_attributes = {
            'up': ((0, 6), math.radians(0)),
            'down': ((0, -6), math.radians(180)),
            'left': ((-6, 0), math.radians(90)),
            'right': ((6, 0), math.radians(270))
        }
        touch_position = self.touch_id_location.get(self.touch_in_joy)
        if touch_position not in self.test.frame:
            if self.test.position.x - 64 * self.object_scale < touch_position.x < self.test.position.x + 64 * self.object_scale:
                if touch_position.y > self.test.position.y:
                    self.move = 'up'
                else:
                    self.move = 'down'
            if self.test.position.y - 64 * self.object_scale < touch_position.y < self.test.position.y + 64 * self.object_scale:
                if touch_position.x > self.test.position.x:
                    self.move = 'right'
                else:
                    self.move = 'left'
                    
        m = move_attributes.get(self.move)
        try:
            x = max(0, min(self.size.w, self.player.position.x + m[0][0] * self.object_scale))
            y = max(0, min(self.size.y, self.player.position.y + m[0][1] * self.object_scale))
            self.player.position = (x, y)
            self.player.run_action(A.sequence(A.rotate_to(m[1], 0.025)))
        except TypeError:
            pass
    
    def shoot_laser(self, position, txture, object, orient):
        laser_attributes = {
            'up': ((0, 1), math.radians(0)),
            'down': ((0, -1), math.radians(180)),
            'left': ((-1, 0), math.radians(90)),
            'right': ((1, 0), math.radians(270)),
            }
        unit_tuple, angle = laser_attributes.get(orient)
        unit_vector = Point(*unit_tuple)
        start_x, start_y = unit_vector * (500 * self.object_scale if object == self.player else 250 * self.object_scale)
        delta_x, delta_y = unit_vector * 64 * self.object_scale
        laser = Laser(txture, object); laser.position = (object.position.x + delta_x, object.position.y + delta_y)
        self.laser_on_screen.append(laser);laser.scale = self.object_scale; self.add_child(laser)
        laser.run_action(A.sequence(A.rotate_to(angle, 0.00001), A.repeat_forever(A.move_by(start_x, start_y))))
    
    def spawn_enemy(self):
        self.difficulty = 0.008 + self.player_score * 0.000002
        if random.random() < self.difficulty and len(self.enemy_on_screen) <= 8:
            index = random.choice([1, 0])
            coor = [(random.uniform(200, self.size.w), random.uniform(self.size.h - 200, self.size.h)), (random.uniform(200, self.size.w - 200), random.uniform(0 ,200))]
            x, y = coor[index]
            txture = random.choice(['spc:EnemyGreen4', 'spc:EnemyBlack4', 'spc:EnemyBlue4'])
            enemy = Enemy(txture); enemy.scale = self.object_scale
            if index == 0:
                 enemy.position = (self.size.w / 2, self.size.h + 48)
            else:
                enemy.position = (self.size.w / 2, -48)
            enemy.run_action(A.sequence(A.move_to(x, y, 1)))
            self.add_child(enemy) 
            self.enemy_on_screen.append(enemy)
    
    def spawn_heart_pack(self):
        difficulty = self.difficulty * 0.05
        if random.random() < difficulty:
            posX, posY =  (random.uniform(self.size.w - 300, 300), random.uniform(self.size.h - 300, 300))
            self.heart = Heart(); self.heart.position = (posX, posY); self.heart.scale = 0.8 * self.object_scale
            self.add_child(self.heart); self.heart_on_screen.append(self.heart)
           
    def check_collision(self):
        for enemy in self.enemy_on_screen:
            if self.player.position in enemy.frame:
                self.enemy_on_screen.remove(enemy)
                enemy.remove_from_parent()
                sound.play_effect('arcade:Explosion_3')
                self.explosion_effect(enemy.position)
                self.player_health = max(0, self.player_health - 20)
            for laser in self.laser_on_screen:
                if laser.position in enemy.frame and laser.shooter == self.player:
                    enemy.remove_from_parent()
                    try:
                        self.enemy_on_screen.remove(enemy)
                        self.laser_on_screen.remove(laser)
                    except ValueError:
                        pass
                    laser.remove_from_parent()
                    self.player_score += 80
                    sound.play_effect('arcade:Explosion_1')
                    self.explosion_effect(enemy.position)
                if laser.position in self.player.frame and isinstance(laser.shooter, Enemy):
                    sound.play_effect('game:Error')
                    try:
                        self.laser_on_screen.remove(laser)
                    except ValueError:
                        pass
                    self.player_health = max(0, self.player_health - int(500 * self.difficulty))
                    laser.remove_from_parent()
                    for i in range(6):
                        particle = SpriteNode(Texture('spc:MeteorBrownMed2'), position = self.player.position, scale=random.uniform(0.3, 0.5) * self.object_scale)
                        actions1 = [A.group(A.move_by(random.uniform(-64, 64), random.uniform(-64, 64), random.uniform(0.4, 0.9)), A.rotate_by(random.uniform(1, 3), 0.4)), A.wait(0.4), A.fade_to(0, 0.3)] 
                        self.add_child(particle); particle.run_action(A.sequence(actions1))
                    
                   
    def explosion_effect(self, position):
        index = 0
        time = [0.0, 0.1, 0.2, 0.3, 0.4]
        for i in range(4):
            explosion_texture = random.choice(('shp:Explosion01', 'shp:Explosion04', 'shp:Explosion00'))
            ex_position = (position.x + random.uniform(-24, 24), position.y + random.uniform(-24, 24))
            pa_position = (position.x + random.uniform(-16, 16), position.y + random.uniform(-16, 16))
            actions = [A.wait(time[index]), A.fade_to(1, 0.04), A.wait(0.06), A.remove()]
            exploded = SpriteNode(Texture(explosion_texture), position = ex_position, scale = random.uniform(0.25, 0.5) * self.object_scale, alpha = 0)
            self.add_child(exploded); exploded.run_action(A.sequence(actions))
            index += 1
            particle = SpriteNode(Texture('spc:MeteorBrownMed2'), position = pa_position, scale=random.uniform(0.5, 0.8) * self.object_scale)
            actions1 = [A.group(A.move_by(random.uniform(-64, 64), random.uniform(-64, 64), random.uniform(0.4, 0.9)), A.rotate_by(random.uniform(1, 3), 0.4)), A.wait(0.4), A.fade_to(0, 0.3)] 
            self.add_child(particle); particle.run_action(A.sequence(actions1))

    def move_enemy(self):
        orient = ''
        for enemy in self.enemy_on_screen:
            if not self.can_shoot_laser(enemy):      
                if enemy.position.y > self.player.position.y and enemy.allow_move == "y":
                    orient = 'down'
                    self.enemy_moving(orient, enemy)
                elif enemy.allow_move == 'y':
                    orient = 'up'
                    self.enemy_moving(orient, enemy)
                if enemy.position.x > self.player.position.x and enemy.allow_move == "x":
                    orient = 'left'
                    self.enemy_moving(orient, enemy)
                elif enemy.allow_move == 'x':
                    orient = 'right'
                    self.enemy_moving(orient, enemy)
                    
            
    def enemy_moving(self, orient, enemy):
        move_attributes = {
            'up': ((0, 2.5), math.radians(0)),
            'down': ((0, -2.5), math.radians(180)),
            'left': ((-2.5, 0), math.radians(90)),
            'right': ((2.5, 0), math.radians(270))
        }
        try:
            m = move_attributes.get(orient)
            x = max(0, min(self.size.w, enemy.position.x + m[0][0] * self.object_scale))
            y = max(0, min(self.size.y, enemy.position.y + m[0][1] * self.object_scale))
            enemy.position = (x, y)
            enemy.run_action(A.sequence(A.rotate_to(m[1], 0.025)))
        except (TypeError):
            pass
                 
    def can_shoot_laser(self, enemy):
        aligned = False
        if self.player.position.x - 32 * self.object_scale < enemy.position.x < self.player.position.x + 32 * self.object_scale:
            enemy.time += 1
            aligned = True
            if enemy.position.y > self.player.position.y:
                orient = 'down'
            else:
                orient = 'up'
                
        if self.player.position.y - 32 * self.object_scale < enemy.position.y < self.player.position.y + 32 * self.object_scale:
            enemy.time += 1
            aligned = True
            if enemy.position.x > self.player.position.x:
                orient = 'left'
            else:
                orient = 'right'
    
        if enemy.time > 60:
            enemy.time = 0
            self.shoot_laser(enemy.position, 'spc:LaserRed9', enemy, orient)
            sound.play_effect('arcade:Laser_5')
            if enemy.allow_move == 'x':
                enemy.allow_move = 'y'
            else:
                enemy.allow_move = 'x'
        return aligned
        
if __name__ == '__main__':
    run(MyScene('spc:BackgroundPurple', 'spc:PlayerShip2Green'), show_fps=False)
