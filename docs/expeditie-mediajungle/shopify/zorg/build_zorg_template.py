"""Bouwt page.expeditie-mediajungle-zorg.json op basis van het onderwijssjabloon (blauwdruk)."""
import json, copy, os
HERE=os.path.dirname(os.path.abspath(__file__))
src=json.load(open(os.path.join(HERE,'..','page.expeditie-mediajungle.json'))); S=src['sections']
DEMO="https://forms.clickup.com/2525734/f/2d2h6-37912/HOJ8H6IC97XNV2IFPT"
PLATFORM="/pages/platform"; CONTACT="/pages/contact"; OPLEIDING="/products/opleiding-aandachtsfunctionaris-mediawijsheid-in-de-zorgpraktijk"
HANDREIKING="https://cdn.shopify.com/s/files/1/0724/1295/4955/files/handreiking-mediawijsheid-lvb-zorg.pdf?v=1790325866"
VJ="https://www.verwey-jonker.nl/publicatie/innoveren-implementeren-en-impact-maken/"
Y="#f5b53c"; BG1="#193539"; BG2="#04202c"
btn=lambda t,h: f'<a class="btn btnbingoOne" href="{h}">{t}</a>'
lnk=lambda t,h,new=False: f'<a href="{h}" style="color:{Y};text-decoration:underline"'+(' target="_blank" rel="noopener"' if new else '')+f'>{t}</a>'
ul=lambda items: "<ul>\n"+"\n".join(f"<li>{i}</li>" for i in items)+"\n</ul>"
T={"sections":{},"order":[]}
def add(key,sec): T['sections'][key]=sec; T['order'].append(key)
def twi(name,title,desc,bg,image="",css=None):
    s={"type":"text-with-image","name":name,"settings":{"section_title":title,"section_title_color":Y,"section_background_color":bg,
       "section_description":desc,"section_description_color":"#ffffff","image":image,"button_title":"","button_link":"","new_window":"current"}}
    if css is not None: s["custom_css"]=css
    return s
IMGCSS=S['text_with_image_FYC4Gm']['custom_css']
# 1 hero
hero=copy.deepcopy(S['bingo_slideshow_t34DFy']); h=hero['blocks']['image_TPJYNd']['settings']
h.update({"title":"Expeditie Mediajungle voor de zorg","subheading":"Samen met je cliënten op ontdekkingstocht door de digitale wereld. Tien missies, in je eigen tempo.",
          "btn_text":"Vraag een vrijblijvende demo aan","btn_link":DEMO,"btn_two_text":"Bekijk het Educatieplatform","btn_two_link":PLATFORM})
add('hero_zorg',hero)
# 2 wat is
add('wat_is_zorg',twi("Wat is Expeditie Mediajungle voor de zorg","Wat is Expeditie Mediajungle voor de zorg?",
 "Een jaarprogramma mediawijsheid voor mensen met een licht verstandelijke beperking (LVB). Begeleider en cliënt gaan samen op pad, met een doorlopend verhaal. "
 "Geen verboden of waarschuwingen, wel samen praten, ontdekken en doen.<br><br>\n"+ul([
 "<b>Tien missies,</b> in je eigen tempo binnen een jaar","<b>Voor kinderen, jongeren en volwassenen</b> met een LVB",
 "Op de woonlocatie, in de dagbesteding of ambulant","Werken aan mediawijsheid, digitale zelfredzaamheid en digitaal welbevinden"]),
 BG1,"shopify://shop_images/logo-expeditie-mj-1600.png",IMGCSS))
# 3 missie
add('missie_zorg',twi("Zo werkt een missie","Zo werkt een missie",ul([
 "<b>Kijk.</b> Een korte animatie introduceert het thema.","<b>Ontdek.</b> Samen praten over eigen ervaringen: wat maak jij online mee?",
 "<b>Doe.</b> Oefenen met vaardigheden voor het dagelijks leven.",
 "<b>Verdien.</b> Samen herhalen wat je hebt geleerd en de missie afronden. Een beloning speelt de volgende missie vrij."])+
 "\n<br>\nThema's zijn onder meer: online winkelen, online pesten, nepnieuws, gezond schermgebruik, AI en romance scams.\n<br>\n<br>\n"+btn("Vraag een vrijblijvende demo aan",DEMO)+"\n<br>\n<br>",BG2,css=[]))
# 4 video, 5 posters (hergebruik)
v=copy.deepcopy(S['section_video_expeditie']); add('video_zorg',v)
p=copy.deepcopy(S['posters_expeditie']); p['settings']['section_title']="Elke missie een poster voor op de groep"; add('posters_zorg',p)
# 6 getoetst
add('getoetst_zorg',twi("Getoetst in de praktijk","Getoetst in de praktijk",
 "De Mediajungle-instrumenten in de missies zijn onderzocht door het Verwey-Jonker Instituut, samen met zorgorganisaties in de LVB-zorg.<br><br>\n"+ul([
 "<b>89%</b> van de cliënten voelde zich goed gehoord","<b>80%</b> voelde zich op zijn gemak in het gesprek",
 "<b>78%</b> vond het leuk om te doen","Begeleiders gaven de instrumenten gemiddeld een <b>7,5</b>"])+
 "\n<br>\n"+lnk("Download de handreiking (pdf)",HANDREIKING,True)+" &nbsp;·&nbsp; "+lnk("Lees het onderzoek bij het Verwey-Jonker Instituut",VJ,True)+
 "\n<br><br>\n<small>Bron: Jonker, Schell-Kiehl &amp; Yohannes (2026), <i>Innoveren, Implementeren en Impact maken</i>, Verwey-Jonker Instituut, gefinancierd door SIDN Fonds. Praktijkstudie met 33 cliënten en 19 zorgprofessionals.</small>",BG1,css=[]))
# 7 begeleider
add('begeleider_zorg',twi("Voor de begeleider","Voor de begeleider",ul([
 "<b>Kant-en-klaar:</b> alles staat klaar in het Mediajungle Educatieplatform",
 "<b>Ook voor jezelf:</b> een e-learning voor begeleiders, achtergrondkennis en handreikingen bij elke missie",
 "<b>Voor wie:</b> woonbegeleiders, ambulant begeleiders, dagbestedingscoaches, gedragswetenschappers en orthopedagogen"]),BG2,css=[]))
# 8 zo start je
add('start_zorg',twi("Zo start je","Zo start je",
 "<ol>\n<li><b>Volg de e-learning</b> voor begeleiders; die zit in de expeditie. Heb je de "+lnk("opleiding Aandachtsfunctionaris Mediawijsheid in de zorgpraktijk",OPLEIDING)+" gevolgd? Dan kun je deze stap overslaan.</li>\n"
 "<li><b>Vraag een demo aan</b> of neem een abonnement op het Educatieplatform.</li>\n<li><b>Start met missie 1</b> met je cliënt of groep.</li>\n</ol>",BG1,css=[]))
# 9 partners (alleen ASVZ)
add('partners_zorg',{"type":"section-partners","name":"Mediajungle is al in gebruik bij","blocks":{"item_asvz":{"type":"item","settings":{"image":"shopify://shop_images/logo-asvz.png"}}},
 "block_order":["item_asvz"],"custom_css":[".container {padding-block: 60px;}",".partnerHodler > .row {display:flex; justify-content:center;}",".partnerHodler .col-xs-6 {float:none;}"],
 "settings":{"section_title":"Mediajungle is al in gebruik bij","section_title_color":Y,"section_color":"none"}})
# 10 CTA
add('cta_zorg',twi("Kom mee op expeditie","Kom mee op expeditie",
 "Wil je zien wat de expeditie voor jouw locatie kan betekenen? Vraag een demo aan.\n<br>\n<br>\n"
 "Expeditie Mediajungle voor de zorg zit in het Mediajungle Educatieplatform; met een abonnement heb je automatisch toegang. "+lnk("Bekijk het Educatieplatform",PLATFORM)+
 ". Liever eerst even bellen? "+lnk("Neem contact op",CONTACT)+".\n<br>\n<br>\n"+btn("Vraag een vrijblijvende demo aan",DEMO)+"\n<br>\n<br>",BG2,css=[]))
add('newsletter_zorg',copy.deepcopy(S['bingo_newsletter_GrhFG3']))
out=os.path.join(HERE,'page.expeditie-mediajungle-zorg.json')
open(out,'w').write(json.dumps(T,ensure_ascii=False,indent=2)+"\n"); print('written',out)
