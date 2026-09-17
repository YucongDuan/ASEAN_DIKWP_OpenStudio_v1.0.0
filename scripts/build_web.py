"""Build browser data and an entirely self-contained offline entry point."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def build():
    mapping={'site':'site.json','catalog':'catalog.json','concepts':'concepts.json','lessons':'lessons.json','locales':'locales.json','scenarios':'scenarios.json','sources':'sources.json','research':'research.json','slides':'mesh98_slides.json'}
    data={k:json.loads((ROOT/'data'/v).read_text(encoding='utf-8')) for k,v in mapping.items()}
    data['license']=(ROOT/'LICENSE').read_text();blob='const STUDIO_DATA = '+json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')+';\n'
    (ROOT/'web/data.js').write_text(blob,encoding='utf-8')
    html=(ROOT/'web/index.html').read_text()
    html=html.replace('<link rel="stylesheet" href="style.css">','<style>'+ (ROOT/'web/style.css').read_text()+'</style>')
    for f in ['data.js','core.js','app.js']:
        js=(ROOT/'web'/f).read_text().replace('</script','<\\/script')
        html=html.replace(f'<script src="{f}"></script>','<script>'+js+'</script>')
    (ROOT/'OpenStudio_Offline.html').write_text(html,encoding='utf-8')
    print('Built web assets and offline HTML:',len(html.encode()),'bytes')
if __name__=='__main__':build()
