SCREEN_WIDTH = 1000
SCREEN_HEIGHT =  1000

FPS = 100



# --- Particle/explosion constants ---
PARTICLE_COUNT       = 30
PARTICLE_SPEED_MIN   = 50
PARTICLE_SPEED_MAX   = 200
PARTICLE_RADIUS      = 3
PARTICLE_LIFETIME    = 0.6
EXPLOSION_DURATION   = 0.5

# --- Smoke constants ---
SMOKE_COUNT          = 10
SMOKE_SPEED_MIN      = 10
SMOKE_SPEED_MAX      = 30
SMOKE_RADIUS         = 6
SMOKE_LIFETIME       = 0.5
SMOKE_COLOR          = (238, 75, 43)

# --- Game constants ---
ROTATION_SPEED       = 50
AIM_LINE_LENGTH      = 700
AIM_LINE_COLOR       = (128, 128, 128)
AIM_LINE_WIDTH       = 4
DOT_SPACING          = 10
PROJECTILE_RADIUS    = 12
PROJECTILE_COLOR     = (255, 100, 100)
PROJECTILE_SPEED     = 500
RELOAD_TIME          = 1.0
BOMBER_SPAWN_TIME    = 3.0  # base spawn interval
BOMBER_SPEED         = 200  # bomber movement speed

# --- Bomb physics constants ---
BOMB_RADIUS          = 15
BOMB_INITIAL_SPEED   = 70    # constant base falling speed
BOMB_SPEED_FACTOR    = 0.1   # slight speed increase per score point
# --- Bomb drop timing constants ---
BOMB_DROP_TIME_MIN   = 1.0   # min time before bomber can drop once in range
BOMB_DROP_TIME_MAX   = 3.0   # max time before bomber can drop once in range

# --- Health bar constants ---
HEALTH_BAR_WIDTH     = 200
HEALTH_BAR_HEIGHT    = 20
HEALTH_COLOR_BG      = (50, 50, 50)
HEALTH_COLOR_FILL    = (0, 200, 0)
