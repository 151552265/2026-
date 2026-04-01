import pygame
import sys
import math
import random

# --- 1. 初始化 Pygame 与常量 ---
pygame.init()

# 窗口设置 (16:9 大尺寸)
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("生命之树 · 抉择")

# 颜色定义
WHITE = (255, 255, 255)
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (0, 100, 0)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GOLD = (255, 215, 0)

# 字体设置
try:
    small_font = pygame.font.SysFont('simhei', 18)
    font = pygame.font.SysFont('simhei', 24)
    large_font = pygame.font.SysFont('simhei', 48)
except:
    small_font = pygame.font.Font(None, 24)
    font = pygame.font.Font(None, 36)
    large_font = pygame.font.Font(None, 72)

# --- 全局游戏变量与参数 ---
wood = 0
TARGET_WOOD = 2000

# 木材银行变量
bank_deposit = 0
bank_interest_timer = 0
BANK_INTERVAL_FRAMES = 600
BANK_INTEREST_RATE = 0.05

# 树木生长与收益参数修饰
GLOBAL_GROWTH_REDUCTION = 0
GLOBAL_MATURE_REDUCTION = 0
MAX_TREES = 10

# 树种数据字典
SPECIES_DATA = {
    "normal": {"name": "普通树", "growth_time": 120, "mature_time": 240, "yields": [1, 3, 6], "color1": GRASS_GREEN, "color2": DARK_GREEN, "cost": 0, "unlocked": True},
    "pine": {"name": "松树", "growth_time": 60, "mature_time": 120, "yields": [1, 2, 4], "color1": (60, 179, 113), "color2": (46, 139, 87), "cost": 40, "unlocked": False},
    "oak": {"name": "橡树", "growth_time": 240, "mature_time": 480, "yields": [2, 6, 15], "color1": (154, 205, 50), "color2": (85, 107, 47), "cost": 80, "unlocked": False}
}
current_species = "normal"

# 科技树数据
tech_tree = {
    "double_harvest": {
        "name": "双倍收获",
        "desc": "砍树时10%几率获得双倍木材",
        "cost": 60,
        "effect": "double_harvest",
        "unlocked": False,
        "deps": []
    },
    "auto_plant": {
        "name": "自动种植",
        "desc": "每隔30秒自动种一棵树（需要先种一棵手动触发）",
        "cost": 100,
        "effect": "auto_plant",
        "unlocked": False,
        "deps": []
    },
    "storm_shield": {
        "name": "风暴防护",
        "desc": "负面事件损失减半",
        "cost": 80,
        "effect": "storm_shield",
        "unlocked": False,
        "deps": []
    },
    "fast_growth_percent": {
        "name": "加速生长",
        "desc": "所有树木生长时间减少20%（可与固定加速叠加，最低30帧）",
        "cost": 120,
        "effect": "fast_growth_percent",
        "unlocked": False,
        "deps": []
    },
    "growth_boost": {
        "name": "快速生长",
        "desc": "树木生长时间-20帧，成熟时间-30帧（可与百分比加速叠加，最低30帧）",
        "cost": 50,
        "effect": "growth_boost",
        "unlocked": False,
        "deps": []
    },
    "expand_land": {
        "name": "扩展林地",
        "desc": "树木上限增加5",
        "cost": 80,
        "effect": "expand_land",
        "unlocked": False,
        "deps": []
    }
}
# 科技树效果变量
DOUBLE_HARVEST_CHANCE = 0.1
AUTO_PLANT_INTERVAL = 30 * 60
auto_plant_timer = 0
storm_shield_active = False
fast_growth_percent_active = False

# 图片加载
IMAGES = {}
try:
    bg_img = pygame.image.load("images/background.png").convert()
    bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
    IMAGES["bg"] = bg_img
    print("背景图片加载成功")
except Exception as e:
    print("背景图片加载失败，使用默认天空草地:", e)

try:
    IMAGES.update({
        "normal_0": pygame.image.load("images/little_tree.png").convert_alpha(),
        "normal_1": pygame.image.load("images/medium_tree.png").convert_alpha(),
        "normal_2": pygame.image.load("images/big_tree.png").convert_alpha(),
        "oak_0": pygame.image.load("images/little_tree2.png").convert_alpha(),
        "oak_1": pygame.image.load("images/medium_tree2.png").convert_alpha(),
        "oak_2": pygame.image.load("images/big_tree2.png").convert_alpha(),
        "pine_0": pygame.image.load("images/little_tree3.png").convert_alpha(),
        "pine_1": pygame.image.load("images/medium_tree3.png").convert_alpha(),
        "pine_2": pygame.image.load("images/big_tree3.png").convert_alpha()
    })
    IMAGES["normal_0"] = pygame.transform.scale(IMAGES["normal_0"], (240, 180))
    IMAGES["normal_1"] = pygame.transform.scale(IMAGES["normal_1"], (240, 180))
    IMAGES["normal_2"] = pygame.transform.scale(IMAGES["normal_2"], (240, 180))
    IMAGES["oak_0"] = pygame.transform.scale(IMAGES["oak_0"], (240, 180))
    IMAGES["oak_1"] = pygame.transform.scale(IMAGES["oak_1"], (240, 180))
    IMAGES["oak_2"] = pygame.transform.scale(IMAGES["oak_2"], (240, 180))
    IMAGES["pine_0"] = pygame.transform.scale(IMAGES["pine_0"], (260, 200))
    IMAGES["pine_1"] = pygame.transform.scale(IMAGES["pine_1"], (260, 200))
    IMAGES["pine_2"] = pygame.transform.scale(IMAGES["pine_2"], (260, 220))
except Exception as e:
    print("树木图片加载失败，将使用简单图形绘制:", e)

# --- 加载技能商城图标 ---
skill_icon = None
try:
    skill_icon = pygame.image.load("images/sign.png").convert_alpha()
    skill_icon = pygame.transform.scale(skill_icon, (60, 60))
except Exception as e:
    print("技能商城图标加载失败，将使用文字按钮:", e)

# --- 2. 类定义 ---

class Particle:
    def __init__(self, x, y, p_type):
        self.x = x
        self.y = y
        self.p_type = p_type
        if self.p_type == "leaf":
            self.vx = random.uniform(-2, 2)
            self.vy = random.uniform(-1, 3)
            self.life = random.randint(30, 60)
            self.color = random.choice([GRASS_GREEN, DARK_GREEN, LIGHT_GREEN])
            self.size = random.randint(3, 6)
        elif self.p_type == "sparkle":
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(-3, -1)
            self.life = random.randint(20, 40)
            self.color = (144, 238, 144)
            self.size = random.randint(2, 4)
        elif self.p_type == "star":
            self.vx = random.uniform(-4, 4)
            self.vy = random.uniform(-4, 4)
            self.life = random.randint(40, 80)
            self.color = GOLD
            self.size = random.randint(3, 7)
        self.max_life = self.life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.p_type == "leaf":
            self.vy += 0.1
        self.life -= 1
        return self.life > 0

    def draw(self, surface):
        if self.p_type == "leaf":
            rect = pygame.Rect(self.x, self.y, self.size, self.size)
            pygame.draw.rect(surface, self.color, rect)
        elif self.p_type in ["sparkle", "star"]:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

class Tree:
    def __init__(self, x, y, species="normal"):
        self.x = x
        self.y = y
        self.age = 0
        self.stage = 0
        self.radius = 20
        self.species = species

    def get_stage_time_with_effects(self, base_time, reduction_key):
        time_with_reduction = max(30, base_time - GLOBAL_GROWTH_REDUCTION if reduction_key == "growth" else base_time - GLOBAL_MATURE_REDUCTION)
        if fast_growth_percent_active:
            time_with_reduction = int(time_with_reduction * 0.8)
        return max(30, time_with_reduction)

    def get_stage_progress(self):
        data = SPECIES_DATA[self.species]
        if self.stage == 0:
            base_time = data["growth_time"]
            target_time = self.get_stage_time_with_effects(base_time, "growth")
        elif self.stage == 1:
            base_time = data["mature_time"]
            target_time = self.get_stage_time_with_effects(base_time, "mature")
        else:
            return 1.0
        remaining_time = max(0, target_time - self.age)
        progress = remaining_time / target_time if target_time > 0 else 1.0
        return min(1.0, max(0.0, progress))

    def get_stage_time_remaining(self):
        data = SPECIES_DATA[self.species]
        if self.stage == 0:
            base_time = data["growth_time"]
            target_time = self.get_stage_time_with_effects(base_time, "growth")
        elif self.stage == 1:
            base_time = data["mature_time"]
            target_time = self.get_stage_time_with_effects(base_time, "mature")
        else:
            return 0
        remaining = max(0, target_time - self.age)
        return remaining / 60

    def update(self):
        self.age += 1
        data = SPECIES_DATA[self.species]
        growth_time = self.get_stage_time_with_effects(data["growth_time"], "growth")
        mature_time = self.get_stage_time_with_effects(data["mature_time"], "mature")
        if self.stage == 0 and self.age >= growth_time:
            self.stage = 1
            self.age = 0
            self.radius = 30
        elif self.stage == 1 and self.age >= mature_time:
            self.stage = 2
            self.radius = 40

    def draw(self, surface):
        if "normal_0" in IMAGES and self.species in ["normal", "pine", "oak"]:
            img = IMAGES[f"{self.species}_{self.stage}"]
            rect = img.get_rect(midbottom=(self.x, self.y + self.radius))
            surface.blit(img, rect)
        else:
            data = SPECIES_DATA[self.species]
            color1 = data["color1"]
            color2 = data["color2"]
            if self.stage == 0:
                pygame.draw.rect(surface, BROWN, (self.x - 4, self.y, 8, 15))
                pygame.draw.circle(surface, LIGHT_GREEN, (self.x, self.y - 5), 10)
            elif self.stage == 1:
                pygame.draw.rect(surface, BROWN, (self.x - 8, self.y - 10, 16, 30))
                pygame.draw.polygon(surface, color1, [
                    (self.x, self.y - 40),
                    (self.x - 20, self.y - 10),
                    (self.x + 20, self.y - 10)
                ])
            elif self.stage == 2:
                pygame.draw.rect(surface, BROWN, (self.x - 12, self.y - 20, 24, 40))
                pygame.draw.polygon(surface, color2, [
                    (self.x, self.y - 70),
                    (self.x - 35, self.y - 20),
                    (self.x + 35, self.y - 20)
                ])
        if self.stage < 2:
            progress = self.get_stage_progress()
            self.draw_progress_bar(surface, progress)

    def draw_progress_bar(self, surface, progress):
        bar_x = self.x
        bar_y = self.y - self.radius - 15
        radius = 12
        thickness = 3
        pygame.draw.circle(surface, GRAY, (bar_x, bar_y), radius, thickness)
        if progress > 0:
            angle = progress * 360
            pygame.draw.arc(surface, GOLD,
                           (bar_x - radius, bar_y - radius, radius * 2, radius * 2),
                           -90 * math.pi / 180,
                           (-90 + angle) * math.pi / 180,
                           thickness)
        remaining_seconds = self.get_stage_time_remaining()
        if remaining_seconds > 0 and progress < 1.0:
            time_text = small_font.render(f"{remaining_seconds:.1f}s", True, BLACK)
            time_rect = time_text.get_rect(center=(bar_x, bar_y))
            surface.blit(time_text, time_rect)

    def get_wood(self, merchant_bonus=False):
        data = SPECIES_DATA[self.species]
        base = data["yields"][self.stage]
        result = base
        if tech_tree["double_harvest"]["unlocked"] and random.random() < DOUBLE_HARVEST_CHANCE:
            result *= 2
        if merchant_bonus:
            result *= 2
        return result

    def collidepoint(self, pos):
        center_y = self.y - 10 if self.stage > 0 else self.y
        hit_radius = self.radius * 1.5
        dist = math.hypot(self.x - pos[0], center_y - pos[1])
        return dist <= hit_radius

class SpeciesButton:
    def __init__(self, rect, species_id):
        self.rect = pygame.Rect(rect)
        self.species_id = species_id

    def draw(self, surface, current_wood, current_selected):
        data = SPECIES_DATA[self.species_id]
        is_selected = (current_selected == self.species_id)
        if is_selected:
            color = (255, 255, 153)
        elif not data["unlocked"]:
            color = LIGHT_GREEN if current_wood >= data["cost"] else GRAY
        else:
            color = WHITE
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        name_text = font.render(data["name"], True, BLACK)
        name_rect = name_text.get_rect(center=(self.rect.centerx, self.rect.centery - 12))
        surface.blit(name_text, name_rect)
        if not data["unlocked"]:
            cost_text = small_font.render(f"解锁: {data['cost']}", True, RED if current_wood < data["cost"] else DARK_GREEN)
        else:
            cost_text = small_font.render("已解锁", True, DARK_GREEN)
        cost_rect = cost_text.get_rect(center=(self.rect.centerx, self.rect.centery + 12))
        surface.blit(cost_text, cost_rect)

    def check_click(self, pos, current_wood):
        if self.rect.collidepoint(pos):
            data = SPECIES_DATA[self.species_id]
            if not data["unlocked"]:
                if current_wood >= data["cost"]:
                    return "buy"
            else:
                return "select"
        return None

class TechButton:
    def __init__(self, rect, tech_id):
        self.rect = pygame.Rect(rect)
        self.tech_id = tech_id

    def draw(self, surface, current_wood):
        data = tech_tree[self.tech_id]
        if data["unlocked"]:
            color = DARK_GREEN
        elif current_wood >= data["cost"] and all(tech_tree[d]["unlocked"] for d in data["deps"]):
            color = LIGHT_GREEN
        else:
            color = GRAY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        name_surf = font.render(data["name"], True, BLACK)
        name_rect = name_surf.get_rect(center=(self.rect.centerx, self.rect.centery - 12))
        surface.blit(name_surf, name_rect)
        cost_surf = small_font.render(f"成本: {data['cost']}", True, BLACK)
        cost_rect = cost_surf.get_rect(center=(self.rect.centerx, self.rect.centery + 12))
        surface.blit(cost_surf, cost_rect)
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            desc_surf = small_font.render(data["desc"], True, WHITE, BLACK)
            desc_rect = desc_surf.get_rect(center=(self.rect.centerx, self.rect.centery + 30))
            surface.blit(desc_surf, desc_rect)

    def check_click(self, pos, current_wood):
        if self.rect.collidepoint(pos):
            data = tech_tree[self.tech_id]
            if not data["unlocked"] and current_wood >= data["cost"] and all(tech_tree[d]["unlocked"] for d in data["deps"]):
                return True
        return False

# --- 3. 游戏重置与主函数 ---
def reset_game():
    global wood, GLOBAL_GROWTH_REDUCTION, GLOBAL_MATURE_REDUCTION, MAX_TREES, current_species
    global tech_tree, storm_shield_active, fast_growth_percent_active, auto_plant_timer
    global bank_deposit, bank_interest_timer
    wood = 0
    GLOBAL_GROWTH_REDUCTION = 0
    GLOBAL_MATURE_REDUCTION = 0
    MAX_TREES = 10
    current_species = "normal"
    bank_deposit = 0
    bank_interest_timer = BANK_INTERVAL_FRAMES
    SPECIES_DATA["pine"]["unlocked"] = False
    SPECIES_DATA["oak"]["unlocked"] = False
    for key in tech_tree:
        tech_tree[key]["unlocked"] = False
    storm_shield_active = False
    fast_growth_percent_active = False
    auto_plant_timer = 0

def main():
    global wood, GLOBAL_GROWTH_REDUCTION, GLOBAL_MATURE_REDUCTION, MAX_TREES, current_species
    global tech_tree, storm_shield_active, fast_growth_percent_active, auto_plant_timer
    global bank_deposit, bank_interest_timer

    clock = pygame.time.Clock()
    trees = []
    particles = []
    game_over = False
    win = False

    EVENT_MIN_FRAMES = 600
    EVENT_MAX_FRAMES = 1200
    event_timer = random.randint(EVENT_MIN_FRAMES, EVENT_MAX_FRAMES)
    current_event_text = ""
    event_text_timer = 0
    EVENT_DISPLAY_FRAMES = 180

    bank_interest_timer = BANK_INTERVAL_FRAMES

    merchant_timer = 0
    MERCHANT_DURATION = 30 * 60
    nest_trees = []
    NEST_DURATION = 60 * 60
    NEST_PRODUCTION_INTERVAL = 10 * 60

    species_buttons = [
        SpeciesButton((WIDTH - 160, 20, 120, 50), "normal"),
        SpeciesButton((WIDTH - 160, 80, 120, 50), "pine"),
        SpeciesButton((WIDTH - 160, 140, 120, 50), "oak")
    ]

    if skill_icon:
        skill_btn_rect = pygame.Rect(WIDTH - 90, 200, 60, 60)
    else:
        skill_btn_rect = pygame.Rect(WIDTH - 160, 200, 120, 40)
    skill_panel_open = False

    bank_btn_rect = pygame.Rect(WIDTH - 160, skill_btn_rect.bottom + 50, 120, 40)
    bank_panel_open = False

    panel_width = 360
    panel_height = 260
    panel_x = WIDTH // 2 - panel_width // 2
    panel_y = HEIGHT // 2 - panel_height // 2

    bank_panel_width = 300
    bank_panel_height = 200
    bank_panel_x = WIDTH // 2 - bank_panel_width // 2
    bank_panel_y = HEIGHT // 2 - bank_panel_height // 2
    tech_keys = list(tech_tree.keys())
    tech_buttons = []
    for i, key in enumerate(tech_keys):
        row = i // 2
        col = i % 2
        btn_rect = pygame.Rect(panel_x + 20 + col * 160, panel_y + 20 + row * 70, 140, 60)
        tech_buttons.append(TechButton(btn_rect, key))

    restart_btn_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if game_over:
                    if restart_btn_rect.collidepoint(pos):
                        reset_game()
                        trees = []
                        game_over = False
                        win = False
                        event_timer = random.randint(EVENT_MIN_FRAMES, EVENT_MAX_FRAMES)
                        current_event_text = ""
                        event_text_timer = 0
                        skill_panel_open = False
                    else:
                        running = False
                    continue

                if skill_panel_open:
                    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
                    if not panel_rect.collidepoint(pos):
                        skill_panel_open = False
                    else:
                        for tb in tech_buttons:
                            if tb.check_click(pos, wood):
                                tech = tech_tree[tb.tech_id]
                                wood -= tech["cost"]
                                tech["unlocked"] = True
                                if tech["effect"] == "storm_shield":
                                    storm_shield_active = True
                                elif tech["effect"] == "fast_growth_percent":
                                    fast_growth_percent_active = True
                                elif tech["effect"] == "auto_plant":
                                    auto_plant_timer = AUTO_PLANT_INTERVAL
                                elif tech["effect"] == "growth_boost":
                                    GLOBAL_GROWTH_REDUCTION += 20
                                    GLOBAL_MATURE_REDUCTION += 30
                                elif tech["effect"] == "expand_land":
                                    MAX_TREES += 5
                                for _ in range(20):
                                    particles.append(Particle(tb.rect.centerx, tb.rect.centery, "star"))
                                break
                    continue

                if skill_btn_rect.collidepoint(pos):
                    skill_panel_open = True
                    bank_panel_open = False
                    continue

                if bank_btn_rect.collidepoint(pos):
                    bank_panel_open = not bank_panel_open
                    skill_panel_open = False
                    continue

                if bank_panel_open:
                    bank_panel_rect = pygame.Rect(bank_panel_x, bank_panel_y, bank_panel_width, bank_panel_height)
                    if not bank_panel_rect.collidepoint(pos):
                        bank_panel_open = False
                        continue

                    quick_btns = [
                        {"label": "+10", "amount": 10, "rect": pygame.Rect(bank_panel_x + 20, bank_panel_y + 100, 50, 30)},
                        {"label": "+50", "amount": 50, "rect": pygame.Rect(bank_panel_x + 80, bank_panel_y + 100, 50, 30)},
                        {"label": "+100", "amount": 100, "rect": pygame.Rect(bank_panel_x + 140, bank_panel_y + 100, 50, 30)},
                        {"label": "全部存入", "amount": "all", "rect": pygame.Rect(bank_panel_x + 20, bank_panel_y + 140, 110, 30)},
                        {"label": "全部取出", "amount": "all", "rect": pygame.Rect(bank_panel_x + 140, bank_panel_y + 140, 110, 30)}
                    ]
                    deposit_btn_rect = pygame.Rect(bank_panel_x + 40, bank_panel_y + 175, 100, 40)
                    withdraw_btn_rect = pygame.Rect(bank_panel_x + 160, bank_panel_y + 175, 100, 40)
                    close_btn_rect = pygame.Rect(bank_panel_x + bank_panel_width - 30, bank_panel_y + 10, 20, 20)

                    if close_btn_rect.collidepoint(pos):
                        bank_panel_open = False
                        continue

                    for btn in quick_btns:
                        if btn["rect"].collidepoint(pos):
                            amount = btn["amount"]
                            if btn["label"] in ["+10", "+50", "+100"]:
                                if wood >= amount:
                                    wood -= amount
                                    bank_deposit += amount
                            elif btn["label"] == "全部存入":
                                if wood > 0:
                                    bank_deposit += wood
                                    wood = 0
                            elif btn["label"] == "全部取出":
                                if bank_deposit > 0:
                                    wood += bank_deposit
                                    bank_deposit = 0
                            break

                    if deposit_btn_rect.collidepoint(pos):
                        if wood >= 10:
                            wood -= 10
                            bank_deposit += 10
                    if withdraw_btn_rect.collidepoint(pos):
                        if bank_deposit >= 10:
                            bank_deposit -= 10
                            wood += 10
                    continue

                # 树种按钮
                clicked_species = False
                for sp_btn in species_buttons:
                    action = sp_btn.check_click(pos, wood)
                    if action == "buy":
                        wood -= SPECIES_DATA[sp_btn.species_id]["cost"]
                        SPECIES_DATA[sp_btn.species_id]["unlocked"] = True
                        current_species = sp_btn.species_id
                        clicked_species = True
                        break
                    elif action == "select":
                        current_species = sp_btn.species_id
                        clicked_species = True
                        break
                if clicked_species:
                    continue

                # 砍树（修复后的逻辑）
                clicked_tree = False
                # 1. 先找出被点击的那棵树
                target_tree = None
                target_index = -1
                for i, tree in enumerate(trees):
                    if tree.collidepoint(pos):
                        target_tree = tree
                        target_index = i
                        break

                # 2. 如果找到了被点击的树
                if target_tree is not None:
                    # 检查这棵树是否被小鸟筑巢
                    is_nested = any(nest[0] == target_tree for nest in nest_trees)
                    if is_nested:
                        current_event_text = "🐦 这棵树有小鸟筑巢，无法砍伐！"
                        event_text_timer = 60
                        clicked_tree = True   # 标记已处理，防止后面种树
                    else:
                        merchant_bonus = merchant_timer > 0
                        wood += target_tree.get_wood(merchant_bonus)
                        for _ in range(15):
                            particles.append(Particle(target_tree.x, target_tree.y - 20, "leaf"))
                        trees.pop(target_index)
                        clicked_tree = True
                        # 移除该树的小鸟筑巢记录
                        nest_trees[:] = [nest for nest in nest_trees if nest[0] != target_tree]

                # 种树
                if not clicked_tree and pos[1] < HEIGHT - 100 and len(trees) < MAX_TREES:
                    if not (pos[0] > WIDTH - 150 and pos[1] < 200):
                        trees.append(Tree(pos[0], pos[1], current_species))
                        for _ in range(10):
                            particles.append(Particle(pos[0], pos[1], "sparkle"))

        # 逻辑更新
        if not game_over:
            for tree in trees:
                tree.update()

            particles = [p for p in particles if p.update()]

            if tech_tree["auto_plant"]["unlocked"] and len(trees) < MAX_TREES:
                if auto_plant_timer > 0:
                    auto_plant_timer -= 1
                if auto_plant_timer <= 0:
                    for _ in range(10):
                        rand_x = random.randint(50, WIDTH-50)
                        rand_y = random.randint(HEIGHT-150, HEIGHT-50)
                        overlap = False
                        for tree in trees:
                            if math.hypot(tree.x - rand_x, tree.y - rand_y) < 40:
                                overlap = True
                                break
                        if not overlap:
                            trees.append(Tree(rand_x, rand_y, current_species))
                            auto_plant_timer = AUTO_PLANT_INTERVAL
                            break
                    else:
                        auto_plant_timer = 30

            if merchant_timer > 0:
                merchant_timer -= 1
                if merchant_timer == 0:
                    current_event_text = "💰 木材商人离开，木材恢复正常价格。"
                    event_text_timer = 60

            bank_interest_timer -= 1
            if bank_interest_timer <= 0:
                if bank_deposit > 0:
                    interest = int(bank_deposit * BANK_INTEREST_RATE)
                    bank_deposit += interest
                    current_event_text = f"💰 利息到账！获得 {interest} 木材！"
                    event_text_timer = 60
                bank_interest_timer = BANK_INTERVAL_FRAMES

            # 小鸟筑巢效果更新（已包含树存在性检查）
            i = 0
            while i < len(nest_trees):
                tree, timer, production_timer = nest_trees[i]
                if tree not in trees:
                    nest_trees.pop(i)
                    continue
                new_timer = timer - 1
                new_production_timer = production_timer + 1
                if new_production_timer >= NEST_PRODUCTION_INTERVAL:
                    wood += 1
                    new_production_timer = 0
                    for _ in range(5):
                        particles.append(Particle(tree.x + random.uniform(-10, 10),
                                                 tree.y - tree.radius, "sparkle"))
                nest_trees[i][1] = new_timer
                nest_trees[i][2] = new_production_timer
                if new_timer <= 0:
                    nest_trees.pop(i)
                else:
                    i += 1

            # 随机事件
            event_timer -= 1
            if event_timer <= 0:
                event_timer = random.randint(EVENT_MIN_FRAMES, EVENT_MAX_FRAMES)
                event_type = random.choice(["storm", "harvest", "pest", "deer", "merchant", "bird"])

                if event_type == "storm":
                    lost = random.randint(10, 30)
                    if storm_shield_active:
                        lost = lost // 2
                    lost = min(wood, lost)
                    wood -= lost
                    current_event_text = f"暴风雨来袭！损失了 {lost} 木材！"

                elif event_type == "harvest":
                    if trees:
                        for tree in trees:
                            if tree.stage < 2:
                                tree.stage += 1
                                tree.age = 0
                                tree.radius = 30 if tree.stage == 1 else 40
                        current_event_text = "丰收季节！所有树木瞬间生长一级！"
                    else:
                        current_event_text = "丰收季节！但你没有种下任何树！"

                elif event_type == "pest":
                    if trees:
                        victim = random.choice(trees)
                        trees.remove(victim)
                        # 修复：同时清除该树的筑巢记录
                        nest_trees[:] = [nest for nest in nest_trees if nest[0] != victim]
                        current_event_text = "遭遇虫害！一棵树木不幸枯萎了！"
                    else:
                        current_event_text = "虫害路过，好在你还没种树！"

                elif event_type == "deer":
                    if trees:
                        lucky_tree = random.choice(trees)
                        lucky_tree.stage = 2
                        lucky_tree.age = 0
                        lucky_tree.radius = 40
                        current_event_text = "🦌 野鹿施肥！一棵树木被神奇地催熟了！"
                    else:
                        current_event_text = "🦌 野鹿施肥！但你还没有种树，错失机会！"

                elif event_type == "merchant":
                    if wood >= 10:
                        merchant_timer = MERCHANT_DURATION
                        current_event_text = "💰 木材商人到访！木材价值翻倍，持续30秒！"
                    else:
                        current_event_text = "💰 木材商人想收购木材，但你库存不足！"
                        event_text_timer = EVENT_DISPLAY_FRAMES // 2

                elif event_type == "bird":
                    if trees:
                        # 修复：避免同一棵树被多次筑巢
                        available_trees = [t for t in trees if not any(nest[0] == t for nest in nest_trees)]
                        if available_trees:
                            host_tree = random.choice(available_trees)
                            nest_trees.append([host_tree, NEST_DURATION, 0])
                            current_event_text = "🐦 小鸟筑巢！一棵树将无法砍伐，但会每10秒产生1木材！"
                        else:
                            current_event_text = "🐦 小鸟想筑巢，但所有树都已经有巢了！"
                    else:
                        current_event_text = "🐦 小鸟想筑巢，但你还没有种树！"

                event_text_timer = EVENT_DISPLAY_FRAMES

            if event_text_timer > 0:
                event_text_timer -= 1

            if wood >= TARGET_WOOD:
                game_over = True
                win = True

        # 绘制
        if "bg" in IMAGES:
            screen.blit(IMAGES["bg"], (0, 0))
        else:
            screen.fill(SKY_BLUE)
            pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT - 100, WIDTH, 100))

        trees.sort(key=lambda t: t.y)
        for tree in trees:
            tree.draw(screen)

        for p in particles:
            p.draw(screen)

        wood_text = font.render(f"木材: {wood} / {TARGET_WOOD}", True, BLACK)
        screen.blit(wood_text, (20, 20))
        tree_count_text = font.render(f"树木: {len(trees)} / {MAX_TREES}", True, BLACK)
        screen.blit(tree_count_text, (20, 60))

        for sp_btn in species_buttons:
            sp_btn.draw(screen, wood, current_species)

        if skill_icon:
            if skill_btn_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, GOLD, skill_btn_rect, 3)
            screen.blit(skill_icon, skill_btn_rect.topleft)
            label_text = small_font.render("技能学习", True, BLACK)
            label_rect = label_text.get_rect(center=(skill_btn_rect.centerx, skill_btn_rect.bottom + 5))
            screen.blit(label_text, label_rect)
        else:
            pygame.draw.rect(screen, GOLD if skill_panel_open else LIGHT_GREEN, skill_btn_rect)
            pygame.draw.rect(screen, BLACK, skill_btn_rect, 2)
            skill_text = font.render("⚙️技能商城", True, BLACK)
            skill_text_rect = skill_text.get_rect(center=skill_btn_rect.center)
            screen.blit(skill_text, skill_text_rect)

        bank_btn_color = GOLD if bank_panel_open else LIGHT_GREEN
        pygame.draw.rect(screen, bank_btn_color, bank_btn_rect)
        pygame.draw.rect(screen, BLACK, bank_btn_rect, 2)
        bank_text = font.render("💰 银行", True, BLACK)
        bank_text_rect = bank_text.get_rect(center=bank_btn_rect.center)
        screen.blit(bank_text, bank_text_rect)

        if bank_btn_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, GOLD, bank_btn_rect, 3)
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

        deposit_text = small_font.render(f"存款: {bank_deposit} 木材", True, BLACK)
        deposit_rect = deposit_text.get_rect(topleft=(bank_btn_rect.left, bank_btn_rect.bottom + 5))
        screen.blit(deposit_text, deposit_rect)

        if not bank_btn_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if skill_panel_open:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            panel_bg = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            pygame.draw.rect(screen, (50, 50, 50), panel_bg)
            pygame.draw.rect(screen, BLACK, panel_bg, 3)
            for tb in tech_buttons:
                tb.draw(screen, wood)

        if bank_panel_open:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            bank_panel_bg = pygame.Rect(bank_panel_x, bank_panel_y, bank_panel_width, bank_panel_height)
            pygame.draw.rect(screen, (50, 50, 50), bank_panel_bg)
            pygame.draw.rect(screen, BLACK, bank_panel_bg, 3)

            title_text = font.render("木材银行", True, WHITE)
            title_rect = title_text.get_rect(center=(bank_panel_x + bank_panel_width // 2, bank_panel_y + 25))
            screen.blit(title_text, title_rect)

            deposit_info_text = small_font.render(f"当前存款: {bank_deposit}", True, WHITE)
            deposit_info_rect = deposit_info_text.get_rect(center=(bank_panel_x + bank_panel_width // 2, bank_panel_y + 55))
            screen.blit(deposit_info_text, deposit_info_rect)

            remaining_seconds = bank_interest_timer / 60
            interest_timer_text = small_font.render(f"下次利息: {remaining_seconds:.1f} 秒", True, WHITE)
            interest_timer_rect = interest_timer_text.get_rect(center=(bank_panel_x + bank_panel_width // 2, bank_panel_y + 75))
            screen.blit(interest_timer_text, interest_timer_rect)

            quick_btns = [
                {"label": "+10", "amount": 10, "rect": pygame.Rect(bank_panel_x + 20, bank_panel_y + 100, 50, 30)},
                {"label": "+50", "amount": 50, "rect": pygame.Rect(bank_panel_x + 80, bank_panel_y + 100, 50, 30)},
                {"label": "+100", "amount": 100, "rect": pygame.Rect(bank_panel_x + 140, bank_panel_y + 100, 50, 30)},
                {"label": "全部存入", "amount": "all", "rect": pygame.Rect(bank_panel_x + 20, bank_panel_y + 140, 110, 30)},
                {"label": "全部取出", "amount": "all", "rect": pygame.Rect(bank_panel_x + 140, bank_panel_y + 140, 110, 30)}
            ]
            deposit_btn_rect = pygame.Rect(bank_panel_x + 40, bank_panel_y + 175, 100, 40)
            withdraw_btn_rect = pygame.Rect(bank_panel_x + 160, bank_panel_y + 175, 100, 40)

            for btn in quick_btns:
                pygame.draw.rect(screen, LIGHT_GREEN, btn["rect"])
                pygame.draw.rect(screen, BLACK, btn["rect"], 2)
                btn_text = small_font.render(btn["label"], True, BLACK)
                btn_text_rect = btn_text.get_rect(center=btn["rect"].center)
                screen.blit(btn_text, btn_text_rect)

            pygame.draw.rect(screen, GOLD, deposit_btn_rect)
            pygame.draw.rect(screen, BLACK, deposit_btn_rect, 2)
            deposit_btn_text = font.render("存入", True, BLACK)
            deposit_btn_text_rect = deposit_btn_text.get_rect(center=deposit_btn_rect.center)
            screen.blit(deposit_btn_text, deposit_btn_text_rect)

            pygame.draw.rect(screen, GOLD, withdraw_btn_rect)
            pygame.draw.rect(screen, BLACK, withdraw_btn_rect, 2)
            withdraw_btn_text = font.render("取出", True, BLACK)
            withdraw_btn_text_rect = withdraw_btn_text.get_rect(center=withdraw_btn_rect.center)
            screen.blit(withdraw_btn_text, withdraw_btn_text_rect)

            close_btn_rect = pygame.Rect(bank_panel_x + bank_panel_width - 30, bank_panel_y + 10, 20, 20)
            pygame.draw.rect(screen, RED, close_btn_rect)
            pygame.draw.rect(screen, BLACK, close_btn_rect, 1)
            close_text = small_font.render("X", True, WHITE)
            close_text_rect = close_text.get_rect(center=close_btn_rect.center)
            screen.blit(close_text, close_text_rect)

        if event_text_timer > 0:
            alpha = min(255, event_text_timer * 2) if event_text_timer < 128 else 255
            event_surface = pygame.Surface((WIDTH, 60), pygame.SRCALPHA)
            event_surface.fill((0, 0, 0, min(128, alpha)))
            screen.blit(event_surface, (0, HEIGHT // 4))
            text_surf = font.render(current_event_text, True, GOLD)
            text_surf.set_alpha(alpha)
            text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 4 + 30))
            screen.blit(text_surf, text_rect)

        if game_over and win:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            win_text = large_font.render("胜利！你收集了足够的木材！", True, WHITE)
            win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(win_text, win_rect)
            pygame.draw.rect(screen, LIGHT_GREEN, restart_btn_rect)
            pygame.draw.rect(screen, BLACK, restart_btn_rect, 2)
            restart_text = font.render("重新开始", True, BLACK)
            restart_text_rect = restart_text.get_rect(center=restart_btn_rect.center)
            screen.blit(restart_text, restart_text_rect)
            tip_text = font.render("点击其他任意位置退出游戏", True, WHITE)
            tip_rect = tip_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
            screen.blit(tip_text, tip_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
