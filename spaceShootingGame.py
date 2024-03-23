import pygame
import random
from pygame.sprite import Group

#=================遊戲初始化==================#
pygame.init()
FPS = 60
WIDTH = 500
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Space Shooting Game')#遊戲名稱
clock = pygame.time.Clock()

#載入圖片 (要先初始化 -> pygame.init() )
background_img = pygame.image.load('resource/img/background.png').convert() #用convert讓pygame讀取變快
player_img = pygame.image.load('resource/img/player.png').convert() 
bullet_img = pygame.image.load('resource/img/bullet.png').convert()

rocks_img = [] 
for i in range(7):
    rocks_img.append(pygame.image.load(f'resource/img/rock{i}.png').convert()) 

#記錄分數
scores = 0
#載入字體
font_name = 'resource/font.ttf' #載入微軟正黑體
# font_name = pygame.font.match_font('arial') #內建arial
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, (255,255,255)) #render把font渲染出來 #中間的True讓字體更圓滑
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect) #在surf上畫text_surface，位置為text_rect

#載入音樂
pygame.mixer.init() #先初始化(音樂)
shoot_sound = pygame.mixer.Sound('resource/sound/shoot.wav')
expl_sound = []
for i in range(2):
    expl_sound.append(pygame.mixer.Sound(f'resource/sound/expl{i}.wav'))
pygame.mixer.music.load('resource/sound/background.ogg') #背景音樂跟其他不一樣(因為要重複播放)
pygame.mixer.music.set_volume(0.5) #調整音量大小(0~1)
pygame.mixer.music.play(-1) #-1表示無限播放

#畫出生命值
def draw_health(surf, hp, x,y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 120
    BAR_HEIGHT = 20
    fill = (hp/100)*BAR_LENGTH
    outline_rect = pygame.Rect(x,y,BAR_LENGTH, BAR_HEIGHT) #畫外框
    fill_rect = pygame.Rect(x,y,fill, BAR_HEIGHT) #畫血條
    pygame.draw.rect(surf, (255,255,255), outline_rect, 5) #2是粗度
    pygame.draw.rect(surf, (255, 0,0), fill_rect)

#爆炸特效
expl_anim = {}
expl_anim['lg'] = [] #大爆炸
expl_anim['sm'] = [] #小爆炸
for i in range(9):
    expl_img = pygame.image.load(f'resource/img/expl{i}.png').convert() 
    expl_img.set_colorkey((0,0,0))
    expl_anim['lg'].append(pygame.transform.scale(expl_img, (75, 75)))
    expl_anim['sm'].append(pygame.transform.scale(expl_img, (30, 30)))


#############
##創建物件
#飛碟（玩家）
class Player(pygame.sprite.Sprite):
    def __init__(self): 
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50,38)) #改變圖片大小 (圖片，想要改成的尺寸)
        self.image.set_colorkey((0,0,0)) #把指定(R,G,B)的顏色變成透明
        
        # self.image = pygame.Surface((50,40)) #物件
        # self.image.fill((0,0,0)) #填滿顏色
        self.rect = self.image.get_rect() #匡起來 匡起來才可執行指令(ex: left, right, top, bottom)
        self.radius = 25
        ### 改用圓來判斷碰撞範圍
        # pygame.draw.circle(self.image, (255,0,0), self.rect.center, self.radius)
        ### 完成後要註解掉
        # self.rect.x = WIDTH/2-25
        # self.rect.y = HEIGHT-40
        # 可用centerx 和 bottom代替
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT
        self.speedx = 8
        self.health = 100
    
    def update(self): #用更新來移動
        key_pressed = pygame.key.get_pressed() #鍵盤上所有按鍵有沒有被按的布林值
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx
            if self.rect.left < 0:
                self.rect.left = 0
    
    def shoot(self): #另外寫一個shoot來射擊
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        shoot_sound.play()

#隕石
class Rock(pygame.sprite.Sprite):
    def __init__(self):  
        pygame.sprite.Sprite.__init__(self)
        self.image = random.choice(rocks_img)
        self.image.set_colorkey((0,0,0))
        # self.image = pygame.Surface((30,30))
        # self.image.fill((255,0,0))
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width)
        # pygame.draw.circle(self.image, (255,0,0), self.rect.center, self.radius)
        self.rect.x = random.randrange(0, WIDTH-self.rect.width)
        self.rect.y = random.randrange(-30, 0)
        self.speedx = random.randrange(-1,1)
        self.speedy = random.randrange(2,6)
    
    def update(self): #創建動作
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if (self.rect.top > HEIGHT) or (self.rect.left > WIDTH) or (self.rect.right < 0):
            self.rect.x = random.randrange(0, WIDTH-self.rect.width)
            self.rect.y = random.randrange(-80, -40)
            self.speedx = random.randrange(-1,1)
            self.speedy = random.randrange(2,6)

#子彈
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y): #多傳入x, y變數，因為要根據飛碟位置決定子彈位置
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey((0,0,0))
        # self.image = pygame.Surface((10,25)) #(寬，高)
        # self.image.fill((255,255,0))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10
    
    def update(self): 
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()
            
#爆炸特效
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks() #回傳從初始化到現在的毫秒數
        self.frame_rate = 50 #毫秒
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center


#把物件放進群組裡，可用於把全部物件顯示在螢幕上
all_sprites = pygame.sprite.Group()
#另外寫players, rocks, bullets群組，用來判斷兩個群組的東西有沒有碰到
rocks = pygame.sprite.Group()
bullets = pygame.sprite.Group()
players = pygame.sprite.Group()

player = Player()
players.add(player)
all_sprites.add(player)
for i in range(10):
    rock = Rock()
    all_sprites.add(rock)
    rocks.add(rock)        
    

#================執行遊戲=================#

running = True
show_init = True
#初始畫面
def draw_init():
    # draw_text(screen, '', 55, WIDTH/2, HEIGHT/4)
    draw_text(screen, '左右鍵:移動 , 空白:發射 , 520分獲勝!', 20, WIDTH/2, HEIGHT/2)
    draw_text(screen, '按任意鍵開始遊戲', 15, WIDTH/2, HEIGHT*3/4)
    pygame.display.update()
    
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
            elif event.type == pygame.KEYUP:
                waiting = False

#遊戲迴圈
while running:
    #畫初始畫面
    if show_init:
        draw_init()
        show_init = False
    
    clock.tick(FPS)
    #取得輸入
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()
    #更新遊戲
    all_sprites.update() #執行所有update函式
    
    hits = pygame.sprite.groupcollide(rocks, bullets, True, True) #(group，group，碰撞到是否刪除，碰撞到是否刪除) #回傳字典{rocks:bullets}
    for hit in hits: #每射掉一個石頭，就補回一個石頭
        random.choice(expl_sound).play()
        scores += int((hit.radius)/10)
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        rock = Rock()
        all_sprites.add(rock)
        rocks.add(rock)
    
    player_hits = pygame.sprite.groupcollide(rocks, players, True, False, pygame.sprite.collide_circle) #最後一個變數：用圓形判斷碰撞範圍
    for hit in player_hits:
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        rock = Rock()
        all_sprites.add(rock)
        rocks.add(rock)
        player.health -= int((hit.radius)/10)
        if player.health <= 0:
            running = False
    #判斷勝利條件
    if scores >= 520:
        draw_text(screen, 'YOU WIN!', 48, WIDTH/2, HEIGHT/4)
        pygame.display.update()
        pygame.time.delay(5000)  #顯示文字5秒鐘
        running = False
    
    #畫面顯示
    screen.fill((255, 255, 255)) #先有畫面
    screen.blit(background_img, (0,0)) #放圖片 (圖片，(x,y))
    all_sprites.draw(screen) #再放物件
    draw_text(screen, f'scores : {str(scores)}', 18, WIDTH/2, 10)
    draw_health(screen, player.health, 40, 10)
    draw_text(screen, 'HP:', 20, 20, 8)
    pygame.display.update()
    
pygame.quit()