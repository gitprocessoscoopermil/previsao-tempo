import requests
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os, math

LAT = -27.8681
LON = -54.4789
LARGURA = 360
ALTURA  = 240

def buscar_previsao():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
        "weathercode,windspeed_10m_max,sunrise,sunset"
        "&hourly=relativehumidity_2m"
        "&timezone=America/Sao_Paulo&forecast_days=4"
    )
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.json()

def fonte(tam, bold=False):
    paths = [
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
        f"/usr/share/fonts/truetype/liberation/LiberationSans-{'Bold' if bold else 'Regular'}.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, tam)
            except: pass
    return ImageFont.load_default()

def desc(wmo):
    if wmo == 0:               return "sol"
    elif wmo in (1,2):         return "sol_nuvem"
    elif wmo == 3:             return "nuvem"
    elif wmo in (45,48):       return "nuvem"
    elif wmo in (51,53,55):    return "garoa"
    elif wmo in (61,63,65):    return "chuva"
    elif wmo in (80,81,82):    return "chuva"
    elif wmo in (71,73,75):    return "neve"
    elif wmo in (95,96,99):    return "tempestade"
    else:                      return "sol_nuvem"

def texto_desc(wmo):
    if wmo == 0:               return "Ceu Limpo"
    elif wmo in (1,2):         return "Parc. Nublado"
    elif wmo == 3:             return "Nublado"
    elif wmo in (45,48):       return "Nevoa"
    elif wmo in (51,53,55):    return "Garoa"
    elif wmo in (61,63,65):    return "Chuva"
    elif wmo in (80,81,82):    return "Pancadas"
    elif wmo in (71,73,75):    return "Neve"
    elif wmo in (95,96,99):    return "Tempestade"
    else:                      return "Variavel"

def nome_dia(date_str, i):
    if i == 0: return "Hoje"
    if i == 1: return "Amanha"
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return ["Seg","Ter","Qua","Qui","Sex","Sab","Dom"][d.weekday()]

# ── ícones desenhados ──────────────────────────────────────────────────────

def draw_sol(d, cx, cy, r=14):
    d.ellipse([(cx-r,cy-r),(cx+r,cy+r)], fill=(255,210,40))
    for i in range(8):
        a = math.radians(i*45)
        x1,y1 = cx+(r+2)*math.cos(a), cy+(r+2)*math.sin(a)
        x2,y2 = cx+(r+7)*math.cos(a), cy+(r+7)*math.sin(a)
        d.line([(x1,y1),(x2,y2)], fill=(255,210,40), width=2)

def draw_nuvem(d, cx, cy, cor=(220,230,245), esc=1.0):
    s = esc
    d.ellipse([(cx-int(14*s),cy-int(6*s)),(cx+int(14*s),cy+int(10*s))], fill=cor)
    d.ellipse([(cx-int(8*s), cy-int(13*s)),(cx+int(8*s), cy+int(1*s))],  fill=cor)
    d.ellipse([(cx-int(18*s),cy-int(2*s)),(cx+int(0*s), cy+int(10*s))],  fill=cor)

def draw_sol_nuvem(d, cx, cy):
    sx,sy = cx+6, cy-5
    r=10
    d.ellipse([(sx-r,sy-r),(sx+r,sy+r)], fill=(255,210,40))
    for i in range(6):
        a=math.radians(i*60)
        d.line([(sx+(r+1)*math.cos(a),sy+(r+1)*math.sin(a)),
                (sx+(r+5)*math.cos(a),sy+(r+5)*math.sin(a))], fill=(255,210,40), width=2)
    draw_nuvem(d, cx-4, cy+5, cor=(220,230,245))

def draw_chuva(d, cx, cy):
    draw_nuvem(d, cx, cy-6, cor=(160,175,200))
    for dx in [-9,0,9]:
        d.line([(cx+dx,cy+6),(cx+dx-3,cy+15)], fill=(80,150,255), width=2)

def draw_garoa(d, cx, cy):
    draw_nuvem(d, cx, cy-6, cor=(180,190,210))
    for dx in [-9,0,9]:
        d.ellipse([(cx+dx-2,cy+8),(cx+dx+2,cy+12)], fill=(80,150,255))

def draw_tempestade(d, cx, cy):
    draw_nuvem(d, cx, cy-8, cor=(120,130,160))
    pts=[(cx+3,cy+4),(cx-5,cy+13),(cx+2,cy+13),(cx-6,cy+22)]
    d.line(pts, fill=(255,230,50), width=3)

def draw_neve(d, cx, cy):
    draw_nuvem(d, cx, cy-6, cor=(200,215,235))
    for i in range(6):
        a=math.radians(i*60)
        d.line([(cx+3*math.cos(a),cy+12+3*math.sin(a)),
                (cx+9*math.cos(a),cy+12+9*math.sin(a))], fill=(200,225,255), width=2)

def icone(d, tipo, cx, cy, pequeno=False):
    fator = 0.65 if pequeno else 1.0
    cx,cy = int(cx), int(cy)
    if tipo=="sol":
        r=int(10*fator) if pequeno else 14
        d.ellipse([(cx-r,cy-r),(cx+r,cy+r)], fill=(255,210,40))
        for i in range(8):
            a=math.radians(i*45)
            d.line([(cx+(r+1)*math.cos(a),cy+(r+1)*math.sin(a)),
                    (cx+(r+5)*math.cos(a),cy+(r+5)*math.sin(a))], fill=(255,210,40), width=2)
    elif tipo=="sol_nuvem":
        if pequeno:
            sx,sy=cx+4,cy-3; r=7
            d.ellipse([(sx-r,sy-r),(sx+r,sy+r)], fill=(255,210,40))
            draw_nuvem(d,cx-2,cy+3,cor=(220,230,245),esc=0.65)
        else: draw_sol_nuvem(d,cx,cy)
    elif tipo=="nuvem":      draw_nuvem(d,cx,cy,esc=fator)
    elif tipo in ("chuva","garoa"):
        if pequeno:
            draw_nuvem(d,cx,cy-4,cor=(160,175,200),esc=0.65)
            for dx in [-5,2]:
                d.line([(cx+dx,cy+4),(cx+dx-2,cy+10)], fill=(80,150,255), width=2)
        else: draw_chuva(d,cx,cy)
    elif tipo=="tempestade": draw_tempestade(d,cx,cy)
    elif tipo=="neve":       draw_neve(d,cx,cy)
    else:
        if pequeno: draw_nuvem(d,cx,cy,esc=0.65)
        else:       draw_sol_nuvem(d,cx,cy)

# ── layout principal ───────────────────────────────────────────────────────

def gerar_imagem(dados):
    img  = Image.new("RGB",(LARGURA,ALTURA),(255,255,255))
    draw = ImageDraw.Draw(img)

    # fundo degradê manual (branco → azul muito claro)
    for y in range(ALTURA):
        t = y/ALTURA
        r = int(255 - t*30)
        g = int(255 - t*20)
        b = int(255 - t*5)
        draw.line([(0,y),(LARGURA,y)], fill=(r,g,b))

    fb14 = fonte(14, bold=True)
    fb11 = fonte(11, bold=True)
    fb10 = fonte(10, bold=True)
    f9   = fonte(9)
    f10  = fonte(10)
    fb28 = fonte(28, bold=True)
    fb13 = fonte(13, bold=True)

    d = dados["daily"]
    wmo0 = d["weathercode"][0]
    tmax0 = d["temperature_2m_max"][0]
    tmin0 = d["temperature_2m_min"][0]
    chuva0 = d["precipitation_sum"][0] or 0
    vento0 = d.get("windspeed_10m_max", [None]*4)[0] or 0

    # umidade da primeira hora do dia
    umid = 0
    if "hourly" in dados:
        umid = dados["hourly"].get("relativehumidity_2m",[0])[0] or 0

    # nascer/pôr do sol (só hora)
    sunrise = d.get("sunrise",[""])[0]
    sunset  = d.get("sunset", [""])[0]
    sr = sunrise[-5:] if len(sunrise)>=5 else "--:--"
    ss = sunset[-5:]  if len(sunset)>=5  else "--:--"

    # ── Painel esquerdo: hoje ─────────────────────────────────────
    # cidade
    draw.text((16,10), "Santa Rosa - RS", font=fb13, fill=(50,50,80))

    # ícone grande
    icone(draw, desc(wmo0), 42, 68)

    # temperatura grande
    txt_temp = f"{tmax0:.0f}°/{tmin0:.0f}°"
    draw.text((90, 45), txt_temp, font=fb28, fill=(30,30,60))

    # descrição
    draw.text((92, 80), texto_desc(wmo0), font=fb11, fill=(80,80,120))

    # grid de infos 2x2
    cy_info = 105
    # chuva
    icone(draw, "chuva", 20, cy_info+6, pequeno=True)
    draw.text((38, cy_info),    f"{chuva0:.0f} mm", font=fb10, fill=(60,100,200))
    draw.text((38, cy_info+12), "Chuva",             font=f9,   fill=(120,130,160))

    # umidade
    draw.text((105, cy_info),    f"{umid:.0f}%",  font=fb10, fill=(60,100,200))
    draw.text((105, cy_info+12), "Umidade",        font=f9,   fill=(120,130,160))

    # vento
    draw.text((38,  cy_info+30), f"{vento0:.0f} km/h", font=fb10, fill=(60,100,200))
    draw.text((38,  cy_info+42), "Vento max",           font=f9,   fill=(120,130,160))

    # nascer/por do sol
    draw.text((105, cy_info+30), f"{sr}  {ss}", font=fb10, fill=(60,100,200))
    draw.text((105, cy_info+42), "Nasc / Por",  font=f9,   fill=(120,130,160))

    # ── Divisor vertical ──────────────────────────────────────────
    draw.line([(195,8),(195,ALTURA-8)], fill=(200,210,230), width=1)

    # ── Painel direito: próximos 3 dias ───────────────────────────
    row_h = (ALTURA - 16) // 3
    for i in range(1, 4):
        ri  = i - 1
        ry  = 8 + ri * row_h
        # linha separadora (exceto primeira)
        if ri > 0:
            draw.line([(200, ry),(LARGURA-8, ry)], fill=(210,220,235), width=1)

        cy_row = ry + row_h//2 - 8

        # nome do dia
        nome = nome_dia(d["time"][i], i)
        draw.text((202, cy_row), nome, font=fb10, fill=(80,80,120))

        # ícone pequeno
        icone(draw, desc(d["weathercode"][i]), 268, cy_row+8, pequeno=True)

        # chuva % (se houver)
        c = d["precipitation_sum"][i] or 0
        if c > 0:
            txt_c = f"{c:.0f}mm"
            draw.text((242, cy_row+2), txt_c, font=f9, fill=(80,140,220))

        # temperaturas
        tx = d["temperature_2m_max"][i]
        tn = d["temperature_2m_min"][i]
        t_txt = f"{tx:.0f}°"
        n_txt = f"{tn:.0f}°"
        tw = draw.textlength(t_txt, font=fb11)
        draw.text((LARGURA-65,          cy_row), t_txt, font=fb11, fill=(220,80,40))
        draw.text((LARGURA-65+tw+4,     cy_row), n_txt, font=fb11, fill=(80,140,220))

    return img

def main():
    print("Buscando dados...")
    dados = buscar_previsao()
    print("Gerando imagem...")
    img = gerar_imagem(dados)
    img.save("previsao.png","PNG",optimize=True)
    print("Salvo: previsao.png")

if __name__ == "__main__":
    main()
