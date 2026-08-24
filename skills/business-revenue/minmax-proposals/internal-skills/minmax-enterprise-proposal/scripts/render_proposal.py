#!/usr/bin/env python3
import argparse,base64,html,json,mimetypes,re
from pathlib import Path
IMAGE_SUFFIXES={".svg",".png",".jpg",".jpeg",".webp"};MAX_ASSET_BYTES=8*1024*1024;SAFE_FONT=re.compile(r"^[A-Za-z0-9 _,'\".-]{1,200}$")
def esc(v):return html.escape(str(v or ""),quote=True)
def list_html(items,css="bullets"):
 items=[x for x in (items or []) if str(x).strip()];return f'<ul class="{css}">'+''.join(f'<li>{esc(x)}</li>' for x in items)+'</ul>' if items else ''
def body_html(paras):
 paras=[x for x in (paras or []) if str(x).strip()];return '<div class="body">'+''.join(f'<p>{esc(p)}</p>' for p in paras)+'</div>' if paras else ''
def within(p,b):
 try:p.resolve().relative_to(b.resolve());return True
 except ValueError:return False
def data_uri(path_text,base_dir):
 if not path_text:return ''
 base=Path(base_dir).resolve();raw=Path(path_text);p=raw.resolve() if raw.is_absolute() else (base/raw).resolve()
 if not within(p,base) or not p.exists() or not p.is_file() or p.suffix.lower() not in IMAGE_SUFFIXES or p.stat().st_size>MAX_ASSET_BYTES:return ''
 mime=mimetypes.guess_type(str(p))[0] or 'application/octet-stream'
 if not mime.startswith('image/'):return ''
 return f'data:{mime};base64,'+base64.b64encode(p.read_bytes()).decode('ascii')
def safe_font(v,fallback):
 v=str(v or '').strip();return v if v and SAFE_FONT.match(v) else fallback
def logo_html(uri,cls='logo',alt='logo'):return f'<img class="{cls}" src="{esc(uri)}" alt="{esc(alt)}">' if uri else ''
def cards_html(cards):
 cards=cards or []
 if not cards:return ''
 cls='grid two' if len(cards)==2 else 'grid';chunks=[]
 for c in cards:chunks.append('<div class="card">'+(f'<div class="label">{esc(c.get("label"))}</div>' if c.get('label') else '')+(f'<div class="value">{esc(c.get("value"))}</div>' if c.get('value') else '')+(f'<h3>{esc(c.get("title"))}</h3>' if c.get('title') else '')+(f'<p>{esc(c.get("body"))}</p>' if c.get('body') else '')+'</div>')
 return f'<div class="{cls}">'+''.join(chunks)+'</div>'
def rail(profile,page,provider_logo,client_logo):
 b=profile.get('business') or {};left=logo_html(provider_logo,'logo',b.get('name','Provider')) or f'<span>{esc(b.get("name"))}</span>';right=logo_html(client_logo,'client-logo','Client');return f'<div class="rail"><div class="brand-lockup">{left}</div><div>{esc(page.get("section"))}</div>{right}</div>'
def footer(profile,n):
 brand=profile.get('brand') or {};b=profile.get('business') or {};text=brand.get('footer_text') or b.get('name') or '';conf=brand.get('confidentiality_label') or '';return f'<div class="footer"><span>{esc(text)} · {n:02d}</span><span>{esc(conf)}</span></div>'
def header(page):return (f'<div class="eyebrow">{esc(page.get("section"))}</div>' if page.get('section') else '')+f'<h1>{esc(page.get("title"))}</h1>'+(f'<div class="subtitle">{esc(page.get("subtitle"))}</div>' if page.get('subtitle') else '')
def money(v,c):return f"{c} {float(v):,.2f}" if isinstance(v,(int,float)) and not isinstance(v,bool) else ''
def render_page(profile,proposal,page,index,provider_logo,client_logo,cover_image):
 t=page.get('type');mode=(proposal.get('meta') or {}).get('release_mode') or 'consulting'
 if t=='cover':
  m=proposal.get('meta') or {};top='<div class="cover-top">'+(logo_html(provider_logo,'logo',(profile.get('business') or {}).get('name','Provider')) or f'<strong>{esc((profile.get("business") or {}).get("name"))}</strong>')+logo_html(client_logo,'client-logo',m.get('client_name','Client'))+'</div>';title=f'<div class="cover-title"><div class="eyebrow">{esc(page.get("section") or "Proposal")}</div><h1>{esc(page.get("title") or m.get("proposal_title"))}</h1>'+(f'<div class="subtitle">{esc(page.get("subtitle"))}</div>' if page.get('subtitle') else '')+'</div>';metas=[('Client',m.get('client_name')),('Issue date',m.get('issue_date')),('Valid until',m.get('valid_until'))];meta='<div class="cover-meta">'+''.join(f'<div><strong>{esc(k)}</strong><br>{esc(v)}</div>' for k,v in metas if v)+'</div>';img=f'<img class="cover-image" src="{esc(cover_image)}" alt="">' if cover_image else '';return f'<section class="page cover">{top}{title}{meta}{img}</section>'
 inner=header(page)+body_html(page.get('body'))
 if t in {'executive','decision','comparison','proof'}:inner+=cards_html(page.get('cards'))+list_html(page.get('bullets'))
 elif t=='narrative':inner+=list_html(page.get('bullets'));inner+=(f'<div class="callout">{esc(page.get("next_step"))}</div>' if page.get('next_step') else '')
 elif t=='scope':inner+=list_html(page.get('bullets'))
 elif t=='sequence':inner+='<div class="sequence">'+''.join(f'<div class="step"><h3>{esc(x.get("title"))}</h3><p>{esc(x.get("body"))}</p></div>' for x in (page.get('items') or []))+'</div>'
 elif t=='commercial':
  inv=page.get('investment') or {};calc=inv.get('calculation') or {};currency=calc.get('currency') or '';comps=''.join(f'<div class="component"><span>{esc(c.get("label"))}<br><small>{esc(c.get("note"))}</small></span><strong>{esc(money(c.get("amount_value"),currency) if mode=="autonomous" else c.get("amount"))} {esc(c.get("unit"))}</strong></div>' for c in (inv.get('components') or []));total=money(calc.get('total_value'),currency) if mode=='autonomous' and calc.get('status')=='fixed' else inv.get('total');inner+='<div class="investment"><div class="left"><div class="card"><div class="label">Included scope</div>'+list_html(inv.get('included_scope'))+'</div><div class="card"><div class="label">Commercial assumptions</div>'+list_html(inv.get('assumptions'))+'</div></div><div class="right"><div class="card"><div class="label">Investment</div>'+comps+'</div>'+f'<div class="card"><div class="label">Consolidated total</div><div class="money">{esc(total)}</div></div></div></div>'
 elif t=='next-step':inner+=list_html(page.get('bullets'))+f'<div class="callout"><strong>Next step:</strong> {esc(page.get("next_step"))}</div>'
 else:inner+=list_html(page.get('bullets'))+cards_html(page.get('cards'))
 return f'<section class="page">{rail(profile,page,provider_logo,client_logo)}<div class="page-content">{inner}</div>{footer(profile,index)}</section>'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--profile',required=True);ap.add_argument('--proposal',required=True);ap.add_argument('--output',required=True);a=ap.parse_args();pp=Path(a.profile).resolve();qp=Path(a.proposal).resolve();out=Path(a.output).resolve();profile=json.loads(pp.read_text());proposal=json.loads(qp.read_text());brand=profile.get('brand') or {};meta=proposal.get('meta') or {};pbase=pp.parent.parent if pp.parent.name=='references' else pp.parent;qbase=qp.parent;provider=data_uri(brand.get('logo_path'),pbase);cover=data_uri(brand.get('cover_image_path'),pbase);client=data_uri(meta.get('client_logo_path'),qbase);pages='\n'.join(render_page(profile,proposal,p,i+1,provider,client,cover) for i,p in enumerate(proposal.get('pages') or []));template=(Path(__file__).resolve().parent.parent/'assets'/'proposal-template.html').read_text();repl={'{{LANG}}':esc((profile.get('voice') or {}).get('default_language') or 'en'),'{{DOCUMENT_TITLE}}':esc(f"{meta.get('proposal_title','Proposal')} - {meta.get('client_name','')}"),'{{PRIMARY}}':brand.get('primary_color') or '#111827','{{ACCENT}}':brand.get('accent_color') or '#2563EB','{{BACKGROUND}}':brand.get('background_color') or '#F8FAFC','{{SURFACE}}':brand.get('surface_color') or '#FFFFFF','{{TEXT}}':brand.get('text_color') or '#111827','{{MUTED}}':brand.get('muted_color') or '#64748B','{{RADIUS}}':str(brand.get('border_radius_px',18)),'{{FONT_DISPLAY}}':safe_font(brand.get('font_display'),'ui-sans-serif, system-ui, sans-serif'),'{{FONT_BODY}}':safe_font(brand.get('font_body'),'ui-sans-serif, system-ui, sans-serif'),'{{PAGES}}':pages};rendered=template
 for k,v in repl.items():rendered=rendered.replace(k,str(v))
 out.write_text(rendered);print(f'WROTE: {out}')
if __name__=='__main__':main()
