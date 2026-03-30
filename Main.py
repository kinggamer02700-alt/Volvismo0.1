import pygame
import sys
import math
import random

pygame.init()

LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("👷 Volvismo RPG - Estilo 3D (Raycasting)")
relogio = pygame.time.Clock()

fonte = pygame.font.SysFont("arial", 24)
fonte_grande = pygame.font.SysFont("arial", 36)

# Mapa (1 = parede, 0 = livre)
mapa = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 1, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1]
]

# Jogador
pos_x = 3.5
pos_y = 4.5
dir_x = 0.0
dir_y = -1.0
plane_x = 0.66
plane_y = 0.0

hp_jogador = 100

# Inimigos (posição x,y no mapa)
inimigos = {
    (2, 1): {"nome": "Espírito Fordista", "hp": 50, "tipo": "fordismo", "cor": (255, 0, 0)},
    (5, 1): {"nome": "Chefe Taylorista", "hp": 60, "tipo": "taylorismo", "cor": (0, 255, 0)},
    (2, 3): {"nome": "Robô Desqualificado", "hp": 40, "tipo": "maquina", "cor": (0, 0, 255)},
    (1, 5): {"nome": "Gerente Antigo", "hp": 55, "tipo": "fordismo", "cor": (255, 255, 0)}
}

# Perguntas do quiz Volvismo
perguntas = {
    "fordismo": [
        {"q": "Qual empresa criou o Volvismo?", "op": ["A) Ford", "B) Volvo", "C) Toyota", "D) GM"], "r": "B"},
        {"q": "O Volvismo valoriza a autonomia do trabalhador?", "op": ["A) Sim", "B) Não"], "r": "A"},
        {"q": "Em qual década surgiu o Volvismo na Suécia?", "op": ["A) 1920", "B) 1960", "C) 2000", "D) 1980"], "r": "B"}
    ],
    "taylorismo": [
        {"q": "O Volvismo é pós-fordista?", "op": ["A) Sim", "B) Não"], "r": "A"},
        {"q": "No Volvismo os trabalhadores trabalham em:", "op": ["A) Linha única", "B) Equipes autônomas"], "r": "B"}
    ],
    "maquina": [
        {"q": "O Volvismo mistura automação com:", "op": ["A) Trabalho manual qualificado", "B) Trabalho repetitivo"], "r": "A"},
        {"q": "Qual é o principal objetivo do Volvismo?", "op": ["A) Aumentar controle", "B) Aumentar participação"], "r": "B"}
    ]
}

estado = "explore"
inimigo_atual = None
pergunta_atual = None
resposta_certa = None
mensagem = ""

def descricao_local():
    px, py = int(pos_x), int(pos_y)
    if px == 3 and py == 4:
        return "Eu estou no Centro de Equipes Autônomas. O Volvismo pulsa aqui!"
    elif px == 2 and py == 1:
        return "Eu estou na Linha Fordista Antiga... o ar é pesado."
    elif px == 5 and py == 1:
        return "Eu estou na Sala Taylorista. Ordens ecoam por todo lado."
    elif px == 2 and py == 3:
        return "Eu estou na Área dos Robôs Desqualificados."
    elif px == 1 and py == 5:
        return "Eu estou no Escritório do Gerente Antigo."
    return "Eu estou em uma área de montagem flexível da fábrica Volvo."

def inimigo_proximo():
    for (ex, ey), data in inimigos.items():
        if data["hp"] > 0 and math.hypot(ex + 0.5 - pos_x, ey + 0.5 - pos_y) < 1.5:
            return (ex, ey)
    return None

running = True
while running:
    relogio.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and estado == "combat" and pergunta_atual:
            resp = ""
            if event.key == pygame.K_a: resp = "A"
            elif event.key == pygame.K_b: resp = "B"
            elif event.key == pygame.K_c: resp = "C"
            elif event.key == pygame.K_d: resp = "D"

            if resp:
                if resp == resposta_certa:
                    dano = random.randint(15, 25)
                    inimigos[inimigo_atual]["hp"] -= dano
                    mensagem = f"✅ CORRETA! Dano {dano}"
                else:
                    dano = random.randint(10, 20)
                    global hp_jogador
                    hp_jogador -= dano
                    mensagem = f"❌ ERRADA! Você tomou {dano} de dano"

                if inimigos[inimigo_atual]["hp"] <= 0:
                    mensagem = f"🎉 Derrotou {inimigos[inimigo_atual]['nome']}!"
                    del inimigos[inimigo_atual]
                    estado = "explore"
                    inimigo_atual = None
                    pergunta_atual = None
                elif hp_jogador <= 0:
                    estado = "gameover"
                else:
                    # próxima pergunta
                    tipo = inimigos[inimigo_atual]["tipo"]
                    pergunta_atual = random.choice(perguntas.get(tipo, perguntas["fordismo"]))
                    resposta_certa = pergunta_atual["r"]

        if event.type == pygame.KEYDOWN and estado == "explore" and event.key == pygame.K_SPACE:
            prox = inimigo_proximo()
            if prox:
                inimigo_atual = prox
                estado = "combat"
                tipo = inimigos[inimigo_atual]["tipo"]
                pergunta_atual = random.choice(perguntas.get(tipo, perguntas["fordismo"]))
                resposta_certa = pergunta_atual["r"]
                mensagem = ""

    # Movimento (só se estiver explorando)
    if estado == "explore" and hp_jogador > 0 and len(inimigos) > 0:
        keys = pygame.key.get_pressed()
        speed = 0.08
        rot = 0.05

        if keys[pygame.K_w]:
            if mapa[int(pos_y)][int(pos_x + dir_x * speed)] == 0:
                pos_x += dir_x * speed
            if mapa[int(pos_y + dir_y * speed)][int(pos_x)] == 0:
                pos_y += dir_y * speed
        if keys[pygame.K_s]:
            if mapa[int(pos_y)][int(pos_x - dir_x * speed)] == 0:
                pos_x -= dir_x * speed
            if mapa[int(pos_y - dir_y * speed)][int(pos_x)] == 0:
                pos_y -= dir_y * speed
        if keys[pygame.K_a]:  # strafe esquerda
            if mapa[int(pos_y)][int(pos_x - dir_y * speed)] == 0:
                pos_x -= dir_y * speed
            if mapa[int(pos_y + dir_x * speed)][int(pos_x)] == 0:
                pos_y += dir_x * speed
        if keys[pygame.K_d]:  # strafe direita
            if mapa[int(pos_y)][int(pos_x + dir_y * speed)] == 0:
                pos_x += dir_y * speed
            if mapa[int(pos_y - dir_x * speed)][int(pos_x)] == 0:
                pos_y -= dir_x * speed
        if keys[pygame.K_LEFT]:
            old_dir_x = dir_x
            dir_x = dir_x * math.cos(rot) - dir_y * math.sin(rot)
            dir_y = old_dir_x * math.sin(rot) + dir_y * math.cos(rot)
            old_plane_x = plane_x
            plane_x = plane_x * math.cos(rot) - plane_y * math.sin(rot)
            plane_y = old_plane_x * math.sin(rot) + plane_y * math.cos(rot)
        if keys[pygame.K_RIGHT]:
            old_dir_x = dir_x
            dir_x = dir_x * math.cos(-rot) - dir_y * math.sin(-rot)
            dir_y = old_dir_x * math.sin(-rot) + dir_y * math.cos(-rot)
            old_plane_x = plane_x
            plane_x = plane_x * math.cos(-rot) - plane_y * math.sin(-rot)
            plane_y = old_plane_x * math.sin(-rot) + plane_y * math.cos(-rot)

    # ==================== RENDER 3D ====================
    tela.fill((40, 40, 80))                    # teto
    pygame.draw.rect(tela, (90, 90, 40), (0, ALTURA//2, LARGURA, ALTURA//2))  # chão

    z_buffer = [float('inf')] * LARGURA

    # Raycasting paredes
    for x in range(LARGURA):
        camera_x = 2 * x / LARGURA - 1
        ray_dir_x = dir_x + plane_x * camera_x
        ray_dir_y = dir_y + plane_y * camera_x

        map_x = int(pos_x)
        map_y = int(pos_y)

        delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else float('inf')
        delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else float('inf')

        if ray_dir_x < 0:
            step_x = -1
            side_dist_x = (pos_x - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - pos_x) * delta_dist_x
        if ray_dir_y < 0:
            step_y = -1
            side_dist_y = (pos_y - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - pos_y) * delta_dist_y

        hit = False
        side = 0
        while not hit:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
            if not (0 <= map_x < len(mapa[0]) and 0 <= map_y < len(mapa)) or mapa[map_y][map_x] == 1:
                hit = True

        if side == 0:
            perp_dist = (map_x - pos_x + (1 - step_x) / 2) / ray_dir_x
        else:
            perp_dist = (map_y - pos_y + (1 - step_y) / 2) / ray_dir_y
        if perp_dist <= 0: perp_dist = 0.1

        line_height = int(ALTURA / perp_dist)
        draw_start = max(0, -line_height // 2 + ALTURA // 2)
        draw_end = min(ALTURA, line_height // 2 + ALTURA // 2)

        cor = (180, 180, 180) if side == 0 else (120, 120, 120)
        pygame.draw.line(tela, cor, (x, draw_start), (x, draw_end))
        z_buffer[x] = perp_dist

    # Sprites inimigos (pilares 3D)
    sprites = []
    for (ex, ey), data in inimigos.items():
        if data["hp"] > 0:
            sprite_x = ex + 0.5 - pos_x
            sprite_y = ey + 0.5 - pos_y
            inv_det = 1.0 / (plane_x * dir_y - dir_x * plane_y)
            transform_x = inv_det * (dir_y * sprite_x - dir_x * sprite_y)
            transform_y = inv_det * (-plane_y * sprite_x + plane_x * sprite_y)
            if transform_y > 0:
                sx = int((LARGURA / 2) * (1 + transform_x / transform_y))
                sh = int(ALTURA / transform_y * 1.2)
                sw = int(sh * 0.6)
                sprites.append((transform_y, sx, sh, sw, data["cor"]))

    sprites.sort(reverse=True, key=lambda s: s[0])
    for dist, sx, sh, sw, cor in sprites:
        start_y = max(0, -sh // 2 + ALTURA // 2)
        end_y = min(ALTURA, sh // 2 + ALTURA // 2)
        start_x = max(0, sx - sw // 2)
        end_x = min(LARGURA, sx + sw // 2)
        for stripe in range(start_x, end_x):
            if stripe < LARGURA and dist < z_buffer[stripe]:
                pygame.draw.line(tela, cor, (stripe, start_y), (stripe, end_y))

    # Mini-mapa
    scale = 15
    mx = LARGURA - len(mapa[0]) * scale - 20
    my = 20
    for yy in range(len(mapa)):
        for xx in range(len(mapa[0])):
            if mapa[yy][xx] == 1:
                pygame.draw.rect(tela, (100, 100, 100), (mx + xx * scale, my + yy * scale, scale, scale))
    pygame.draw.circle(tela, (0, 255, 0), (mx + int(pos_x * scale), my + int(pos_y * scale)), 6)
    for (ex, ey), data in inimigos.items():
        if data["hp"] > 0:
            pygame.draw.circle(tela, data["cor"], (mx + int((ex + 0.5) * scale), my + int((ey + 0.5) * scale)), 7)

    # HUD
    hp_txt = fonte.render(f"HP: {int(hp_jogador)}", True, (255, 255, 255))
    tela.blit(hp_txt, (20, 20))
    desc_txt = fonte.render(descricao_local(), True, (255, 255, 255))
    tela.blit(desc_txt, (20, ALTURA - 50))

    # Overlay de combate
    if estado == "combat" and pergunta_atual:
        overlay = pygame.Surface((LARGURA, ALTURA))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        tela.blit(overlay, (0, 0))

        q_txt = fonte_grande.render(pergunta_atual["q"], True, (255, 255, 255))
        tela.blit(q_txt, (LARGURA//2 - q_txt.get_width()//2, 120))

        for i, opcao in enumerate(pergunta_atual["op"]):
            op_txt = fonte.render(opcao, True, (255, 255, 255))
            tela.blit(op_txt, (LARGURA//2 - op_txt.get_width()//2, 220 + i * 45))

        msg_txt = fonte.render(mensagem, True, (0, 255, 0) if "CORRETA" in mensagem else (255, 0, 0))
        tela.blit(msg_txt, (LARGURA//2 - msg_txt.get_width()//2, 420))

        instr = fonte.render("A / B / C / D  →  responder", True, (180, 180, 180))
        tela.blit(instr, (LARGURA//2 - instr.get_width()//2, 500))

    elif estado == "explore":
        instr = fonte.render("WASD = andar  |  ← → = girar  |  SPACE = atacar", True, (200, 200, 200))
        tela.blit(instr, (20, ALTURA - 90))

    # Vitória / Derrota
    if len(inimigos) == 0:
        v = fonte_grande.render("🏆 VITÓRIA! A fábrica agora é Volvismo total!", True, (0, 255, 0))
        tela.blit(v, (LARGURA//2 - v.get_width()//2, ALTURA//2 - 50))
    if hp_jogador <= 0 or estado == "gameover":
        go = fonte_grande.render("💀 GAME OVER - O Fordismo venceu...", True, (255, 0, 0))
        tela.blit(go, (LARGURA//2 - go.get_width()//2, ALTURA//2))

    pygame.display.flip()

pygame.quit()
sys.exit()
