from scene import *
from Game import MyScene
import sound
import random
import ui
import math
A = Action

class Character(SpriteNode):
    def __init__(self, txture, object_scale, *args, **kwargs):
        SpriteNode.__init__(self, txture, scale = object_scale)
        
class Button(SpriteNode):
    def __init__(self, txture, title, object_scale, pos, *args, **kwargs):
        SpriteNode.__init__(self, txture, pos, y_scale = 1, x_scale = 1.5)
        self.label = LabelNode(text = title, position = (0, 2), font = ('<System>', 20), color = 'black', x_scale = 0.66666); self.add_child(self.label)
        self.title = title
 
class Menu(Scene):
    def __init__(self, button_title):
        Scene.__init__(self)
        self.bg_tile = ['spc:BackgroundBlack', 'spc:BackgroundBlue', 'spc:BackgroundDarkPurple', 'spc:BackgroundPurple']
        self.index_background = 0
        self.background_txt = self.bg_tile[self.index_background]
        self.index_character = 0
        self.player_texture_list = [
            'spc:PlayerShip1Blue', 'spc:PlayerShip1Green', 'spc:PlayerShip1Orange', 'spc:PlayerShip1Red', 'spc:PlayerShip2Blue', 'spc:PlayerShip2Green', 'spc:PlayerShip2Orange', 'spc:PlayerShip2Red', 'spc:PlayerShip3Blue', 'spc:PlayerShip3Green', 'spc:PlayerShip3Orange', 'spc:PlayerShip3Red'
            ]
        self.player_txt = self.player_texture_list[self.index_character]
        self.os = self.size.h * (1 / 834)
        self.object_element = len(button_title)
        self.button_title = button_title
        self.button_list = []
        self.touch_id_location = {}
        self.background_tile_list = []
        
    def setup(self):
        self.game = MyScene(self.background_txt, self.player_txt)
        bg = Node(parent=self)
        self.main = Node(parent=self)
        os = self.os
        for x in range(math.ceil(self.size.w / 128) + 1):
            for y in range(math.ceil(self.size.h / 128) + 1):
                tile = SpriteNode(Texture(self.background_txt), position = (x * 128, y * 128))
                self.background_tile_list.append(tile)
                bg.add_child(tile)
        self.width, self.height = 1194 * (1 / 3), 160 + (self.object_element * 64)
        menu_shape = ui.Path.rounded_rect(0, 0, self.width, self.height, 8)
        menu_shape.line_width = 5
        menu_bg = ShapeNode(path = menu_shape, stroke_color = '#52bbff', position = (self.size.w / 2, self.size.h / 2), alpha = 0.75)
        self.main.add_child(menu_bg)
        title = LabelNode(text = "SPACE SHOOT'EM!", font = ('Euphemia UCAS', 30), position = (self.size.w / 2, menu_bg.position.y + (menu_bg.size.h / 2) - 80), color = 'black'); self.main.add_child(title)
        for index, title in enumerate(reversed(self.button_title)):
            button = Button('pzl:Button1', title, self.os, self.get_button_pos(index + 1, menu_bg))
            self.button_list.append(button)
            self.main.add_child(button)
        #preview character texture
        self.player = SpriteNode(Texture(self.player_txt), position = (self.size.w / 2, (menu_bg.position.y - menu_bg.size.h * (5 / 6))))
        self.main.add_child(self.player); self.player.run_action(A.sequence(A.repeat_forever(A.rotate_by(1, 3))))
        #adjust position after scaled
        self.main.scale = self.os
        self.main.position = (((self.size.w - (self.size.w * self.os)) / 2), (self.size.h - (self.size.h * self.os)) / 2)
    
    def get_button_pos(self, order, menu_bg):
        os = self.os
        pos_y = (menu_bg.position.y - (menu_bg.size.h / 2) + order * 64 ) 
        return (self.size.w / 2, pos_y)
        
    def did_change_size(self):
        pass
    
    def update(self):
        pass
    
    def touch_began(self, touch):
        touch_loc = self.main.point_from_scene(touch.location)
        self.touch_id_location[touch.touch_id] = touch_loc    
        for button in self.button_list:
            if touch_loc in button.frame:
                sound.play_effect('ui:switch6')
                button.texture = Texture('pzl:Button2')
            
    
    def touch_moved(self, touch):
        pass    
    
    def touch_ended(self, touch):
        for touch_id in self.touch_id_location.keys():
            for button in self.button_list:
                touch_location = self.touch_id_location.get(touch_id)
                if touch_location in button.frame:
                    if button.title == "Play":
                        self.present_modal_scene(self.game)
                    if button.title == "Switch Background":
                        self.change_background()
                    if button.title == "Switch Character":
                        self.change_player()
                    button.texture = Texture('pzl:Button1')
        try:
            self.touch_id_location.pop(touch_id)
        except:
            pass
    def change_background(self):
        if self.index_background == len(self.bg_tile) - 1:
            self.index_background = 0
        else:
            self.index_background += 1
        self.background_txt = self.bg_tile[self.index_background]
        for tile in self.background_tile_list:
            tile.texture = Texture(self.background_txt)
        self.game = MyScene(self.background_txt, self.player_txt)
        
    def change_player(self):
        if self.index_character == len(self.player_texture_list) - 1:
            self.index_character = 0
        else:
            self.index_character += 1
        self.player_txt = self.player_texture_list[self.index_character]
        self.player.texture = Texture(self.player_txt)
        self.game = MyScene(self.background_txt, self.player_txt)
        
if __name__ == '__main__':
    run(Menu(['Play', 'Switch Character', 'Switch Background']), LANDSCAPE, show_fps=False)
