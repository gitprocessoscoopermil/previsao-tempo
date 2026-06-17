import requests, cairosvg, io, urllib.request, numpy as np
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os

LAT = -27.8681
LON = -54.4789
LARGURA = 360
ALTURA  = 240

ICON_BASE = "https://raw.githubusercontent.com/erikflowers/weather-icons/master/svg/wi-{}.svg"

ICON_MAP = {
    0:  ("day-sunny",      (245,158,11)),
    1:  ("day-cloudy",     (148,163,184)),
    2:  ("day-cloudy",     (148,163,184)),
    3:  ("cloudy",         (100,116,139)),
    45: ("fog",            (148,163,184)),
    48: ("fog",            (148,163,184)),
    51: ("sprinkle",       (96,165,250)),
    53: ("sprinkle",       (96,165,250)),
    55: ("sprinkle",       (96,165,250)),
    61: ("rain",           (59,130,246)),
    63: ("rain",           (59,130,246)),
    65: ("rain",           (37,99,235)),
    71: ("snow",           (147,197,253)),
    73: ("snow",           (147,197,253)),
    75: ("snow",           (147,197,253)),
    80: ("showers",        (59,130,246)),
    81: ("showers",        (59,130,246)),
    82: ("showers",        (37,99,235)),
    95: ("storm-showers",  (99,102,241)),
    96: ("storm-showers",  (99,102,241)),
    99: ("thunderstorm",   (79,70,229)),
}

DESC_MAP = {
    0:  "Céu Limpo",
    1:  "Parc. Nublado",
    2:  "Parc. Nublado",
    3:  "Nublado",
    45: "Névoa",
    48: "Névoa",
    51: "Garoa",
    53: "Garoa",
    55: "Garoa",
    61: "Chuva",
    63: "Chuva",
    65: "Chuva Forte",
    71: "Neve",
    73: "Neve",
    75: "Neve Forte",
    80: "Pancadas",
    81: "Pancadas",
    82: "Pancadas",
    95: "Tempestade",
    96: "Tempestade",
    99: "Tempestade",
}

def wmo_icone(wmo): return ICON_MAP.get(wmo, ("day-cloudy", (148,163,184)))
def wmo_desc(wmo):  return DESC_MAP.get(wmo, "Variável")

def cache_icone(nome, cor, tamanho=52):
    cor_str = f"{cor[0]}-{cor[1]}-{cor[2]}"
    path = f"/tmp/wef_{nome}_{cor_str}_{tamanho}.png"
    if os.path.exists(path):
        return Image.open(path).convert("RGBA")
    try:
        url = ICON_BASE.format(nome)
        with urllib.request.urlopen(url) as r:
            svg = r.read()
        png = cairosvg.svg2png(bytestring=svg, output_width=tamanho, output_height=tamanho)
        img = Image.open(io.BytesIO(png)).convert("RGBA")
        _, _, _, a = img.split()
        tinted = Image.merge("RGBA", [
            Image.new("L", img.size, cor[0]),
            Image.new("L", img.size, cor[1]),
            Image.new("L", img.size, cor[2]),
            a
        ])
        tinted.save(path)
        return tinted
    except Exception as e:
        print(f"Erro icone {nome}: {e}")
        return None

def colar_icone(img, ic, cx, cy):
    if ic is None: return
    iw, ih = ic.size
    img.paste(ic, (cx - iw//2, cy - ih//2), ic)

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

def nome_dia(date_str, i):
    if i == 0: return "Hoje"
    if i == 1: return "Amanhã"
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"][d.weekday()]

def gerar_imagem(dados):
    img  = Image.new("RGB", (LARGURA, ALTURA), (255,255,255))
    draw = ImageDraw.Draw(img)

    for y in range(ALTURA):
        t = y / ALTURA
        draw.line([(0,y),(LARGURA,y)], fill=(
            int(240 - t*25), int(248 - t*20), int(255 - t*10)
        ))

    fb28 = fonte(28, bold=True)
    fb13 = fonte(13, bold=True)
    fb11 = fonte(11, bold=True)
    fb10 = fonte(10, bold=True)
    f9   = fonte(9)

    d      = dados["daily"]
    wmo0   = d["weathercode"][0]
    tmax0  = d["temperature_2m_max"][0]
    tmin0  = d["temperature_2m_min"][0]
    chuva0 = d["precipitation_sum"][0] or 0
    vento0 = d.get("windspeed_10m_max", [0]*4)[0] or 0

    umid = 0
    if "hourly" in dados:
        umid = dados["hourly"].get("relativehumidity_2m", [0])[0] or 0

    sunrise = d.get("sunrise", [""])[0]
    sunset  = d.get("sunset",  [""])[0]
    sr = sunrise[-5:] if len(sunrise) >= 5 else "--:--"
    ss = sunset[-5:]  if len(sunset)  >= 5 else "--:--"

    draw.text((14, 10), "Santa Rosa - RS", font=fb13, fill=(40,40,80))

    nome_ic, cor_ic = wmo_icone(wmo0)
    ic_hoje = cache_icone(nome_ic, cor_ic, tamanho=54)
    colar_icone(img, ic_hoje, 42, 65)

    draw.text((88, 40), f"{tmax0:.0f}°/{tmin0:.0f}°", font=fb28, fill=(25,25,60))
    draw.text((90, 78), wmo_desc(wmo0), font=fb11, fill=(80,80,130))

    cy_info = 106
    nome_ic2, cor_ic2 = wmo_icone(61)
    ic_chuva = cache_icone(nome_ic2, cor_ic2, tamanho=18)
    colar_icone(img, ic_chuva, 20, cy_info+6)
    draw.text((32, cy_info),    f"{chuva0:.0f} mm", font=fb10, fill=(50,90,200))
    draw.text((32, cy_info+13), "Chuva",             font=f9,   fill=(110,120,160))

    draw.text((105, cy_info),    f"{umid:.0f}%", font=fb10, fill=(50,90,200))
    draw.text((105, cy_info+13), "Umidade",       font=f9,   fill=(110,120,160))

    draw.text((32,  cy_info+30), f"{vento0:.0f} km/h", font=fb10, fill=(50,90,200))
    draw.text((32,  cy_info+43), "Vento máx.",          font=f9,   fill=(110,120,160))

    draw.text((105, cy_info+30), f"{sr}  {ss}", font=fb10, fill=(50,90,200))
    draw.text((105, cy_info+43), "Nasc / Pôr",  font=f9,   fill=(110,120,160))

    draw.line([(193,8),(193,ALTURA-8)], fill=(195,210,230), width=1)

    row_h = (ALTURA - 16) // 3
    for i in range(1, 4):
        ri = i - 1
        ry = 8 + ri * row_h
        if ri > 0:
            draw.line([(197, ry),(LARGURA-6, ry)], fill=(205,218,235), width=1)

        cy_row = ry + row_h//2 - 12

        draw.text((200, cy_row),    nome_dia(d["time"][i], i),     font=fb10, fill=(70,70,120))
        draw.text((200, cy_row+14), wmo_desc(d["weathercode"][i]), font=f9,   fill=(110,120,165))

        nome_ic3, cor_ic3 = wmo_icone(d["weathercode"][i])
        ic = cache_icone(nome_ic3, cor_ic3, tamanho=30)
        colar_icone(img, ic, 282, cy_row+10)

        c = d["precipitation_sum"][i] or 0
        if c > 0:
            txt_mm = f"{c:.0f}mm"
            tw_mm = draw.textlength(txt_mm, font=f9)
            draw.text((282 - tw_mm//2, cy_row+26), txt_mm, font=f9, fill=(70,130,210))

        tx = d["temperature_2m_max"][i]
        tn = d["temperature_2m_min"][i]
        t_txt = f"{tx:.0f}°"
        n_txt = f"{tn:.0f}°"
        tw = draw.textlength(t_txt, font=fb11)
        draw.text((LARGURA-58,      cy_row), t_txt, font=fb11, fill=(210,70,30))
        draw.text((LARGURA-58+tw+3, cy_row), n_txt, font=fb11, fill=(60,130,210))

    # ── Logo Coopermil ───────────────────────────────────────────
    try:
        logo_url = "https://raw.githubusercontent.com/gitprocessoscoopermil/previsao-tempo/main/logotipo-coopermil-jpg.jpg"
        with urllib.request.urlopen(logo_url) as r:
            logo_data = r.read()
        logo = Image.open(io.BytesIO(logo_data)).convert("RGBA")
        data = np.array(logo)
        r2, g2, b2 = data[:,:,0], data[:,:,1], data[:,:,2]
        mask = (r2 > 220) & (g2 > 220) & (b2 > 220)
        data[:,:,3] = np.where(mask, 0, 255)
        logo = Image.fromarray(data)
        ratio = 22 / logo.height
        logo = logo.resize((int(logo.width * ratio), 22), Image.LANCZOS)
        img.paste(logo, (6, ALTURA - 28), logo)
    except Exception as e:
        print(f"Logo erro: {e}")

    return img

def main():
    print("Buscando dados...")
    dados = buscar_previsao()
    print("Gerando imagem...")
    img = gerar_imagem(dados)
    img.save("previsao.png", "PNG", optimize=True)
    print("Salvo: previsao.png")

if __name__ == "__main__":
    main()
