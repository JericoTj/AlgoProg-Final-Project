import pygame
import math
import random

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()  # Initialize the mixer module for sound and music

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 700
TILE_SIZE = 128
FPS = 60

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Load and play background music
pygame.mixer.music.load('CastleVein.mp3')  # Load the background music file
pygame.mixer.music.play(loops=0, start=0.0)  # Play the music in a loop (-1 = infinite loop)

# Load assets
player_image = pygame.image.load('player.png').convert_alpha()
bricks_image = pygame.image.load('bricks.jpg').convert()
Enemy_image = pygame.image.load('Enemy.png').convert_alpha()
bricks_image = pygame.transform.scale(bricks_image, (TILE_SIZE, TILE_SIZE))

crosshair_image = pygame.image.load('crosshair.png').convert_alpha()
crosshair_image = pygame.transform.scale(crosshair_image, (32, 32))  # Resize crosshair
pygame.mouse.set_visible(False)  # Hide the system cursor

# Load and play background music
pygame.mixer.music.load('CastleVein.mp3')  # Load the background music file
pygame.mixer.music.play(loops=-1, start=0.0)  # Play the music in a loop (-1 = infinite loop)

# Gun sprite assets
pistol_image = pygame.image.load('pistol.png').convert_alpha()
rifle_image = pygame.image.load('rifle.png').convert_alpha()

# **Gun Class**
class Gun(pygame.sprite.Sprite):
    def __init__(self, name, damage, fire_rate, max_ammo, reload_time, sprite, scale_factor=0.1, spread=0):
        super().__init__()
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate
        self.max_ammo = max_ammo
        self.reload_time = reload_time
        self.current_ammo = max_ammo
        self.last_shot_time = 0
        self.spread = spread  # Bullet spread (degrees)
        self.sprite = sprite

        self.scale_factor = scale_factor
        self.scaled_sprite = pygame.transform.scale(
            self.sprite, 
            (int(self.sprite.get_width() * self.scale_factor),
             int(self.sprite.get_height() * self.scale_factor))
        )
        self.rect = self.scaled_sprite.get_rect()
        self.image = self.scaled_sprite  # Initial image setup



    def rotate(self, player_x, player_y, mouse_x, mouse_y):
        dx = mouse_x - player_x
        dy = mouse_y - player_y
        self.angle = math.atan2(dy, dx) * 180 / math.pi  # Convert radians to degrees

        # Rotate the gun to face the crosshair
        rotated_image = pygame.transform.rotate(self.scaled_sprite, -self.angle)
        self.rect = rotated_image.get_rect(center=(player_x, player_y))  # Gun follows the player's position
        self.image = rotated_image


    def shoot(self, player_x, player_y, mouse_x, mouse_y, current_time, bullets_group):
        if current_time - self.last_shot_time >= self.fire_rate:
            if self.current_ammo > 0:
                self.current_ammo -= 1
                self.last_shot_time = current_time

                dx = mouse_x - player_x
                dy = mouse_y - player_y
                angle = math.atan2(dy, dx)
                angle += random.uniform(-self.spread, self.spread) * math.pi / 180  # Bullet spread

                # Spawn bullet
                dir_x = math.cos(angle)
                dir_y = math.sin(angle)
                bullet = Bullet(player_x, player_y, dir_x, dir_y, self.damage)
                bullets_group.add(bullet)

                return True
            else:
                print(f"{self.name} is out of ammo!")
        return False
    
    def reload(self):
        self.current_ammo = self.max_ammo  # Refill ammo to max when reloading
        print(f"{self.name} reloaded!")

# **Player Class**
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(player_image, (50, 50))
        self.rect = self.image.get_rect()
        self.world_x, self.world_y = TILE_SIZE * 2, TILE_SIZE * 2  # Starting position
        self.speed = 5
        self.hp = 100  # Player's health
        self.max_hp = 100
        self.ammo_font = pygame.font.SysFont('Arial', 24)

        self.guns = [pistol, rifle]
        self.active_gun_index = 0

    def switch_gun(self):
        if len(self.guns) > 1:
            self.active_gun_index = (self.active_gun_index + 1) % len(self.guns)
            print(f"Switched to {self.guns[self.active_gun_index].name}")

    def reload(self):
        current_gun = self.guns[self.active_gun_index]
        current_gun.reload()
        print(f"{current_gun.name} reloaded!")

    def shoot(self, bullets_group):
        current_gun = self.guns[self.active_gun_index]
        now = pygame.time.get_ticks() / 1000  # Current time in seconds

        if current_gun.shoot(self.world_x, self.world_y, *pygame.mouse.get_pos(), now, bullets_group):
            print(f"Shot fired from {current_gun.name}!")

    def move(self, keys, dungeon):
        if keys[pygame.K_w] and dungeon.can_move(self.world_x, self.world_y - self.speed, self.rect.width, self.rect.height):
            self.world_y -= self.speed
        if keys[pygame.K_s] and dungeon.can_move(self.world_x, self.world_y + self.speed, self.rect.width, self.rect.height):
            self.world_y += self.speed
        if keys[pygame.K_a] and dungeon.can_move(self.world_x - self.speed, self.world_y, self.rect.width, self.rect.height):
            self.world_x -= self.speed
        if keys[pygame.K_d] and dungeon.can_move(self.world_x + self.speed, self.world_y, self.rect.width, self.rect.height):
            self.world_x += self.speed

    def update(self, mouse_x, mouse_y):
        # The gun will follow the player's position
        current_gun = self.guns[self.active_gun_index]
        current_gun.position = (self.world_x, self.world_y)  # Directly assign player's position to gun
        current_gun.rotate(self.world_x, self.world_y, mouse_x, mouse_y)

    def draw_ui(self, screen):
        # Draw Ammo count
        current_gun = self.guns[self.active_gun_index]
        ammo_text = self.ammo_font.render(f"Ammo: {current_gun.current_ammo}/{current_gun.max_ammo}", True, (255, 255, 255))
        screen.blit(ammo_text, (10, 10))

        # Draw HP Bar
        hp_bar_width = 200
        hp_percentage = self.hp / self.max_hp
        pygame.draw.rect(screen, (0, 0, 0), (10, 40, hp_bar_width, 20))  # Black background
        pygame.draw.rect(screen, (0, 255, 0), (10, 40, hp_bar_width * hp_percentage, 20))  # Green HP bar

        # Display HP text (Optional, for better understanding of current HP)
        hp_text = self.ammo_font.render(f"{self.hp}/{self.max_hp}", True, (255, 255, 255))
        screen.blit(hp_text, (hp_bar_width + 20, 40))


# **Specific Guns**
pistol = Gun(name="Pistol", damage=10, fire_rate=0.4, max_ammo=12, reload_time=2, sprite=pistol_image, scale_factor=0.1)
rifle = Gun(name="Rifle", damage=15, fire_rate=0.1, max_ammo=30, reload_time=4, sprite=rifle_image, scale_factor=0.6)

# **Bullet Class**
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dir_x, dir_y, damage):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill((255, 255, 0))  # Yellow bullets
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 15
        self.velocity = (dir_x * self.speed, dir_y * self.speed)
        self.damage = damage

    def update(self):
        # Update bullet position
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        # Remove if out of screen bounds
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()

# **Enemy Class**
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, Enemy_image):
        super().__init__()
        self.image = pygame.image.load(Enemy_image).convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.health = 100
        self.visible = False  # Initially set to invisible
        self.speed = 3

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.die()

    def die(self):
        self.kill()  # Remove the enemy from the group

    def spawn(self):
        self.visible = True  # Set to True when you want to show the enemy
        self.image.set_alpha(255)  # Ensure the sprite is fully visible

    def hide(self):
        self.visible = False  # Set to False to hide the enemy
        self.image.set_alpha(0)  # Make the sprite fully transparent

    def update(self, player):
        if self.visible:
            # Calculate direction to the player
            dir_x = player.world_x - self.rect.centerx
            dir_y = player.world_y - self.rect.centery
            length = math.hypot(dir_x, dir_y)
            if length != 0:
                dir_x, dir_y = dir_x / length, dir_y / length

            # Move towards the player
            self.rect.x += dir_x * self.speed
            self.rect.y += dir_y * self.speed

            # Check for collision with the player
            if self.rect.colliderect(player.rect):
                player.take_damage(10)  # Deal damage to the player when colliding
                self.kill()  # Remove the enemy after ramming

# **Dungeon Class**
class Dungeon:
    def __init__(self):
        # Tile map: 0 = floor, 1 = wall
        self.tile_map = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        self.rows = len(self.tile_map)
        self.cols = len(self.tile_map[0])

        # Load tile images
        self.floor_image = pygame.transform.scale(bricks_image, (TILE_SIZE, TILE_SIZE))
        self.wall_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.wall_image.fill((0, 0, 0))  # Black for walls

    def draw(self, surface, camera_offset):
        # Draw the dungeon based on the tile map
        for row in range(self.rows):
            for col in range(self.cols):
                tile = self.tile_map[row][col]
                x = col * TILE_SIZE - camera_offset[0]
                y = row * TILE_SIZE - camera_offset[1]
                if tile == 1:
                    surface.blit(self.wall_image, (x, y))
                else:
                    surface.blit(self.floor_image, (x, y))

    def can_move(self, x, y, width, height):
        # Check if the player can move to the specified position (no collision with walls)
        top_left = (x, y)
        top_right = (x + width, y)
        bottom_left = (x, y + height)
        bottom_right = (x + width, y + height)

        if self.tile_map[top_left[1] // TILE_SIZE][top_left[0] // TILE_SIZE] == 1 or \
           self.tile_map[top_right[1] // TILE_SIZE][top_right[0] // TILE_SIZE] == 1 or \
           self.tile_map[bottom_left[1] // TILE_SIZE][bottom_left[0] // TILE_SIZE] == 1 or \
           self.tile_map[bottom_right[1] // TILE_SIZE][bottom_right[0] // TILE_SIZE] == 1:
            return False
        return True

# **Main Game Loop**
def game_loop():
    running = True
    camera_offset_x, camera_offset_y = 0, 0
    camera_smoothness = 0.1  # Camera smoothing factor
    bullets = pygame.sprite.Group()
    rifle_drops = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    player = Player()
    dungeon = Dungeon()

    # Spawning an enemy
    enemy = Enemy(400, 300, "Enemy.png")
    enemies.add(enemy)
    enemy.hide()

    spawn_time = pygame.time.get_ticks()  # Start time
    spawn_delay = 3000  # Delay in milliseconds (3 seconds)

    while running:
        screen.fill(WHITE)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    player.reload()  # Reload the gun
                if event.key == pygame.K_q:
                    player.switch_gun()  # Switch gun

        # Update game logic
        keys = pygame.key.get_pressed()
        player.move(keys, dungeon)

        # Shooting
        if pygame.mouse.get_pressed()[0]:  # Left click
            player.shoot(bullets)

        # Get the mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Update the player's gun to follow the mouse
        player.update(mouse_x, mouse_y)

        # Draw the dungeon (with camera offset)
        dungeon.draw(screen, (camera_offset_x, camera_offset_y))

        # Draw the player sprite
        screen.blit(player.image, (player.world_x - camera_offset_x, player.world_y - camera_offset_y))

        # Draw the gun
        current_gun = player.guns[player.active_gun_index]
        screen.blit(current_gun.image, current_gun.rect.topleft)  # Draw the gun at its current position

        # Update and draw enemies
        for enemy in enemies:
            enemy.update(player)  # Pass the player to the enemy to calculate movement

        enemies.draw(screen)

        # Update player position and gun
        player.update(mouse_x, mouse_y)
        
        # Draw bullets
        bullets.update()
        bullets.draw(screen)
        
        # Draw UI elements (ammo and HP)
        player.draw_ui(screen)

        # Draw crosshair
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen.blit(crosshair_image, (mouse_x - crosshair_image.get_width() // 2, mouse_y - crosshair_image.get_height() // 2))

        # Update camera position based on player position
        target_camera_x = player.world_x - SCREEN_WIDTH // 2
        target_camera_y = player.world_y - SCREEN_HEIGHT // 2

        # Apply camera collision: prevent it from going out of bounds
        target_camera_x = max(0, min(target_camera_x, TILE_SIZE * dungeon.cols - SCREEN_WIDTH))
        target_camera_y = max(0, min(target_camera_y, TILE_SIZE * dungeon.rows - SCREEN_HEIGHT))

        camera_offset_x += (target_camera_x - camera_offset_x) * camera_smoothness
        camera_offset_y += (target_camera_y - camera_offset_y) * camera_smoothness

        pygame.display.flip()
        clock.tick(FPS)

# Start the game
game_loop()
pygame.quit()