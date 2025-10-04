import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle
from matplotlib.animation import FuncAnimation

# --- Константы и настройки ---
FIG_SIZE = 11
GEAR_ORDER = ['N', '1', '2', '3']
GEAR_SPEEDS = {'N': 0.0, '1': 1.0, '2': 2.0, '3': 3.5}
TURN_DIFFERENCE = 2.5
STEER_ANGLE_MAX = 60
STEER_ANGLE_STEP = 5
AUTO_CENTER_SPEED = 2
PINION_GEAR_RATIO = 5

# --- Глобальные переменные состояния ---
key_states = {'up': False, 'down': False, 'left': False, 'right': False}
artists = {}
angles = {'ring': 0.0, 'pinion': 0.0, 'spider_carrier': 0.0, 'spider_rotation': 0.0, 
          'left_side_gear': 0.0, 'right_side_gear': 0.0, 'steer': 0.0}
current_gear_index = 1

# --- Функции обработки событий клавиатуры ---
def on_press(event):
    if event.key in key_states: key_states[event.key] = True
def on_release(event):
    global current_gear_index
    if event.key in key_states:
        key_states[event.key] = False
        if event.key == 'up': current_gear_index = min(len(GEAR_ORDER) - 1, current_gear_index + 1)
        elif event.key == 'down': current_gear_index = max(0, current_gear_index - 1)

# --- Настройка холста ---
fig = plt.figure(figsize=(FIG_SIZE, FIG_SIZE))
fig.canvas.mpl_connect('key_press_event', on_press)
fig.canvas.mpl_connect('key_release_event', on_release)
fig.patch.set_facecolor('#f0f0f0')

ax_main = fig.add_axes([0.05, 0.3, 0.9, 0.65])
ax_speedo = fig.add_axes([0.05, 0.05, 0.25, 0.25])
ax_steer = fig.add_axes([0.375, 0.05, 0.25, 0.25])
ax_gear = fig.add_axes([0.7, 0.05, 0.25, 0.25])
ax_info = fig.add_axes([0.0, 0.9, 1.0, 0.1])
ax_info.axis('off')

# --- Функция инициализации для анимации ---
def init():
    ax_main.set_xlim(-6, 6); ax_main.set_ylim(-6, 6)
    ax_main.set_aspect('equal'); ax_main.axis('off')
    ax_main.add_patch(Circle((0, 0), 3.5, color='gray', alpha=0.15, zorder=-1))
    
    artists['driveshaft'] = ax_main.add_patch(Rectangle((2.7, -0.2), 3, 0.4, color='darkgray', zorder=4))
    artists['ring_gear'] = ax_main.add_patch(Circle((0, 0), 2.5, color='gainsboro', zorder=0))
    artists['pinion_gear'] = ax_main.add_patch(Circle((2.7, 0), 0.5, color='dimgray', zorder=5))
    artists['axle_left'] = ax_main.plot([-1.2, -3.7], [0, 0], color='silver', lw=12, zorder=3, solid_capstyle='round')[0]
    artists['axle_right'] = ax_main.plot([1.2, 3.7], [0, 0], color='silver', lw=12, zorder=3, solid_capstyle='round')[0]
    artists['wheel_left'] = ax_main.add_patch(Circle((-4.5, 0), 0.8, color='dimgray', zorder=1))
    artists['wheel_right'] = ax_main.add_patch(Circle((4.5, 0), 0.8, color='dimgray', zorder=1))
    artists['side_gear_left'] = ax_main.add_patch(Circle((-1.2, 0), 1.0, color='crimson', zorder=5))
    artists['side_gear_right'] = ax_main.add_patch(Circle((1.2, 0), 1.0, color='crimson', zorder=5))
    artists['spider_gear_1'] = ax_main.add_patch(Circle((0, 1.2), 0.4, color='dodgerblue', zorder=6))
    artists['spider_gear_2'] = ax_main.add_patch(Circle((0, -1.2), 0.4, color='dodgerblue', zorder=6))
    
    artists['wheel_left_marker'] = ax_main.add_patch(Circle((-4.5, 0.6), 0.15, color='white', zorder=2))
    artists['wheel_right_marker'] = ax_main.add_patch(Circle((4.5, 0.6), 0.15, color='white', zorder=2))
    artists['side_gear_left_marker'] = ax_main.add_patch(Circle((-1.2, 0.8), 0.15, color='white', zorder=6))
    artists['side_gear_right_marker'] = ax_main.add_patch(Circle((1.2, 0.8), 0.15, color='white', zorder=6))
    artists['spider_gear_1_marker'] = ax_main.add_patch(Circle((0, 1.5), 0.1, color='white', zorder=7))
    artists['spider_gear_2_marker'] = ax_main.add_patch(Circle((0, 0.9), 0.1, color='white', zorder=7))
    artists['pinion_marker'] = ax_main.add_patch(Circle((2.7, 0.3), 0.1, color='white', zorder=6))
    artists['driveshaft_marker'] = ax_main.add_patch(Circle((4.2, 0.2), 0.1, color='white', zorder=5))

    text_bbox = dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=1, alpha=0.8)
    ax_main.text(4.2, 0.8, "Карданный вал", ha='center', fontsize=10, bbox=text_bbox)
    ax_main.annotate("Ведомая шестерня\n(Корпус)", xy=(2.5, 1), xytext=(3.5, 2.5), arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.2"), bbox=text_bbox)
    ax_main.annotate("Сателлит", xy=(0, 1.6), xytext=(-2.5, 3), arrowprops=dict(arrowstyle="->"), bbox=text_bbox)
    ax_main.annotate("Полуосевая\nшестерня", xy=(-1.2, 1.0), xytext=(-3.5, 1.8), arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.2"), bbox=text_bbox)
    ax_main.annotate("Полуось", xy=(-3, 0), xytext=(-5, -1.5), arrowprops=dict(arrowstyle="->"), bbox=text_bbox)

    for ax, title in [(ax_speedo, "Обороты"), (ax_steer, "Руль"), (ax_gear, "КПП")]:
        ax.set_title(title, fontsize=12, pad=10); ax.set_facecolor('#f0f0f0')

    ax_speedo.set_xlim(-1.5, 1.5); ax_speedo.set_ylim(-1.5, 1.5); ax_speedo.set_aspect('equal'); ax_speedo.axis('off')
    ax_speedo.add_patch(Circle((0, 0), 1.2, color='black')); ax_speedo.add_patch(Circle((0, 0), 1.1, color='white'))
    for i in range(4): ax_speedo.text(np.cos(np.pi/3-i*np.pi/3), np.sin(np.pi/3-i*np.pi/3), f'{i}', ha='center', va='center')
    ax_speedo.text(0, -0.5, "x1000 rpm", fontsize=8)
    artists['speedo_needle'] = ax_speedo.plot([0,0], [0,0.9], 'r-', lw=3)[0]

    ax_steer.set_xlim(-1.5, 1.5); ax_steer.set_ylim(-1.5, 1.5); ax_steer.set_aspect('equal'); ax_steer.axis('off')
    ax_steer.add_patch(Circle((0, 0), 1.0, color='black', fill=False, lw=5))
    artists['steer_spoke_1'] = ax_steer.plot([], [], color='black', lw=4)[0]
    artists['steer_spoke_2'] = ax_steer.plot([], [], color='black', lw=4)[0]
    artists['steer_spoke_3'] = ax_steer.plot([], [], color='black', lw=4)[0]
    
    ax_gear.set_xlim(0, 4); ax_gear.set_ylim(0, 4); ax_gear.set_aspect('equal'); ax_gear.axis('off')
    ax_gear.add_patch(Rectangle((0, 0), 4, 4, color='lightgray', ec='black'))
    ax_gear.plot([1,1,3,3], [3.5,2,2,0.5], 'k-', lw=2)
    for g, (x, y) in {'1':(1,3), '2':(1,1), '3':(3,3), 'N':(2,2)}.items(): ax_gear.text(x, y, g, ha='center', va='center', fontsize=16)
    artists['gear_indicator'] = ax_gear.add_patch(Circle((0,0), 0.5, fc='royalblue', ec='black', lw=2))
    
    ax_info.text(0.01, 0.5, "Управление: \u2191 / \u2193 - Передачи, \u2190 / \u2192 - Руль", ha='left', va='center', fontsize=12)
    artists['info_text'] = ax_info.text(0.99, 0.5, "Состояние: Нажмите на окно...", ha='right', va='center', fontsize=12, color='navy')
    
    return artists.values()

def update(frame):
    # Управление рулем (теперь `angles['steer']` положительный для левого поворота)
    if key_states['left']: angles['steer'] = min(STEER_ANGLE_MAX, angles['steer'] + STEER_ANGLE_STEP)
    elif key_states['right']: angles['steer'] = max(-STEER_ANGLE_MAX, angles['steer'] - STEER_ANGLE_STEP)
    else: # Авто-возврат
        if angles['steer'] > AUTO_CENTER_SPEED: angles['steer'] -= AUTO_CENTER_SPEED
        elif angles['steer'] < -AUTO_CENTER_SPEED: angles['steer'] += AUTO_CENTER_SPEED
        else: angles['steer'] = 0
    
    # --- Расчет скоростей ---
    current_gear = GEAR_ORDER[current_gear_index]
    base_speed = GEAR_SPEEDS[current_gear]
    turn_ratio = angles['steer'] / STEER_ANGLE_MAX
    
    # ИСПРАВЛЕНИЕ: Логика скорости сателлитов и колес
    # spider_rot_speed теперь положительна при левом повороте
    spider_rot_speed = turn_ratio * TURN_DIFFERENCE * (base_speed / 2 if base_speed > 0 else 0)
    left_speed = base_speed - spider_rot_speed
    right_speed = base_speed + spider_rot_speed
    
    # Обновление углов
    angles['ring'] = (angles['ring'] - base_speed) % 360
    angles['pinion'] = (angles['pinion'] + base_speed * PINION_GEAR_RATIO) % 360
    angles['left_side_gear'] = (angles['left_side_gear'] - left_speed) % 360
    angles['right_side_gear'] = (angles['right_side_gear'] - right_speed) % 360
    angles['spider_carrier'] = angles['ring']
    angles['spider_rotation'] = (angles['spider_rotation'] - spider_rot_speed) % 360

    # --- Обновление графики ---
    for name, angle, radius, center_pos in [
        ('side_gear_left_marker', 'left_side_gear', 0.8, (-1.2,0)),
        ('side_gear_right_marker', 'right_side_gear', 0.8, (1.2,0)),
        ('pinion_marker', 'pinion', 0.3, (2.7,0)),
        ('driveshaft_marker', 'pinion', 0.2, (4.2,0)),
        ('wheel_left_marker', 'left_side_gear', 0.6, (-4.5,0)),
        ('wheel_right_marker', 'right_side_gear', 0.6, (4.5,0))
    ]:
        rad = np.radians(angles[angle])
        artists[name].center = (center_pos[0] + radius * np.cos(rad), center_pos[1] + radius * np.sin(rad))

    carrier_rad = np.radians(angles['spider_carrier'])
    spider1_pos = (-1.2 * np.sin(carrier_rad), 1.2 * np.cos(carrier_rad))
    spider2_pos = (1.2 * np.sin(carrier_rad), -1.2 * np.cos(carrier_rad))
    artists['spider_gear_1'].center, artists['spider_gear_2'].center = spider1_pos, spider2_pos
    
    spider_rot_rad_1 = np.radians(-angles['ring'] + angles['spider_rotation'])
    spider_rot_rad_2 = np.radians(-angles['ring'] - angles['spider_rotation'])
    artists['spider_gear_1_marker'].center = (spider1_pos[0] + 0.3*np.cos(spider_rot_rad_1), spider1_pos[1] + 0.3*np.sin(spider_rot_rad_1))
    artists['spider_gear_2_marker'].center = (spider2_pos[0] + 0.3*np.cos(spider_rot_rad_2), spider2_pos[1] + 0.3*np.sin(spider_rot_rad_2))
    
    # ИСПРАВЛЕНИЕ: Убран лишний минус для правильного вращения руля
    steer_rad = np.radians(angles['steer']) 
    for i in range(3):
        spoke_key = f'steer_spoke_{i+1}'
        spoke_angle = steer_rad + i * 2 * np.pi / 3
        artists[spoke_key].set_data([0, 0.9 * np.cos(spoke_angle)], [0, 0.9 * np.sin(spoke_angle)])
    
    speedo_angle = np.pi/3 - (base_speed / max(GEAR_SPEEDS.values(), default=1)) * np.pi/3 * 3
    artists['speedo_needle'].set_data([0, 0.9 * np.cos(speedo_angle)], [0, 0.9 * np.sin(speedo_angle)])

    gear_positions = {'1': (1, 3), '2': (1, 1), '3': (3, 3), 'N': (2, 2)}
    artists['gear_indicator'].center = gear_positions[current_gear]

    info_str = f"Передача: {current_gear} | "
    if turn_ratio > 0.1: info_str += "Поворот налево"
    elif turn_ratio < -0.1: info_str += "Поворот направо"
    else: info_str += "Движение прямо"
    artists['info_text'].set_text(info_str)
    
    return artists.values()

# --- Запуск анимации ---
ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=20, cache_frame_data=False)
plt.show()