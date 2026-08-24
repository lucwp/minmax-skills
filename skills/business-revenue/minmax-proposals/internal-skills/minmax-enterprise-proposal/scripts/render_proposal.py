#!/usr/bin/env python3
import argparse,base64,html,json,mimetypes,re
from pathlib import Path
IMAGE_SUFFIXES={".svg",".png",".jpg",".jpeg",".webp"};MAX_ASSET_BYTES=8*1024*1024;SAFE_FONT=re.compile(r"^[A-Za-z0-9 _,'\".-]{1,200}$")
def esc(v):return html.escape(str(v or ""),quote=True)
def within(p,b):
    try:p.resolve().relative_to(b.resolve());return True
    except ValueError:return False
def data_uri(raw,base):
    if not raw:return ""
    b=Path(base).resolve();r=Path(raw);p=r.resolve() if r.is_absolute() else (b/r).resolve()
    if not within(p,b) or not p.exists() or not p.is_file() or p.suffix.lower() not in IMAGE_SUFFIXES or p.stat().st_size>MAX_ASSET_BYTES:return ""
    mime=mimetypes.guess_type(str(p))[0] or "application/octet-stream"
    if not mime.startswith("image/"):return ""
    return f"data:{mime};base64,"+base64.b64encode(p.read_bytes()).decode("ascii")
def safe_font(v,f):v=str(v or "").strip();return v if v and SAFE_FONT.match(v) else f
def list_html(items):return "" if not items else '<ul class="bullets">'+"".join(f"<li>{esc(x)}</li>" for x in items if str(x).strip())+"</ul>"
def body_html(items):return "" if not items else '<div class="body">'+"".join(f"<p>{esc(x)}</p>" for x in items if str(x).strip())+"</div>"
def cards(items):return "" if not items else '<div class="grid">'+"".join(f'<div class="card"><h3>{esc(x.get("title"))}</h3><p>{esc(x.get("body"))}</p></div>' for x in items)+"</div>"
def money(v,c):return f"{c} {float(v):,.2f}" if isinstance(v,(int,float)) and not isinstance(v,bool) else ""
def render(profile,proposal,page,i,provider,client,cover):
    t=page.get("type");meta=proposal.get("meta") or {};mode=meta.get("release_mode") or "consulting"
    if t=="cover":return f'<section class="page cover"><h1>{esc(page.get("title") or meta.get("proposal_title"))}</h1></section>'
    inner=f'<div class="eyebrow">{esc(page.get("section"))}</div><h1>{esc(page.get("title"))}</h1>'+body_html(page.get("body"))+cards(page.get("cards"))+list_html(page.get("bullets"))
    if t=="commercial":
        inv=page.get("investment") or {};calc=inv.get("calculation") or {};currency=calc.get("currency") or "";components="".join(f'<div class="component"><span>{esc(x.get("label"))}</span><strong>{esc(money(x.get("amount_value"),currency) if mode=="autonomous" else x.get("amount"))}</strong></div>' for x in inv.get("components") or []);total=money(calc.get("total_value"),currency) if mode=="autonomous" and calc.get("status")=="fixed" else str(inv.get("total") or "");inner+=f'<div class="investment">{components}<div class="money">{esc(total)}</div></div>'
    if t=="next-step":inner+=f'<div class="callout"><strong>Next step:</strong> {esc(page.get("next_step"))}</div>'
    return f'<section class="page"><div class="page-content">{inner}</div></section>'
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--profile",required=True);ap.add_argument("--proposal",required=True);ap.add_argument("--output",required=True);a=ap.parse_args();pp=Path(a.profile).resolve();jp=Path(a.proposal).resolve();profile=json.loads(pp.read_text(encoding="utf-8"));proposal=json.loads(jp.read_text(encoding="utf-8"));brand=profile.get("brand") or {};base=pp.parent.parent if pp.parent.name=="references" else pp.parent;provider=data_uri(brand.get("logo_path"),base);cover=data_uri(brand.get("cover_image_path"),base);client=data_uri((proposal.get("meta") or {}).get("client_logo_path"),jp.parent);pages="\n".join(render(profile,proposal,p,i+1,provider,client,cover) for i,p in enumerate(proposal.get("pages") or []));template=(Path(__file__).resolve().parent.parent/"assets"/"proposal-template.html").read_text(encoding="utf-8");rep={"{{LANG}}":esc((profile.get("voice") or {}).get("default_language") or "en"),"{{DOCUMENT_TITLE}}":esc((proposal.get("meta") or {}).get("proposal_title") or "Proposal"),"{{PRIMARY}}":brand.get("primary_color") or "#111827","{{ACCENT}}":brand.get("accent_color") or "#2563EB","{{BACKGROUND}}":brand.get("background_color") or "#F8FAFC","{{SURFACE}}":brand.get("surface_color") or "#FFFFFF","{{TEXT}}":brand.get("text_color") or "#111827","{{MUTED}}":brand.get("muted_color") or "#64748B","{{RADIUS}}":str(brand.get("border_radius_px",18)),"{{FONT_DISPLAY}}":safe_font(brand.get("font_display"),"ui-sans-serif, system-ui, sans-serif"),"{{FONT_BODY}}":safe_font(brand.get("font_body"),"ui-sans-serif, system-ui, sans-serif"),"{{PAGES}}":pages}
    for k,v in rep.items():template=template.replace(k,str(v))
    Path(a.output).write_text(template,encoding="utf-8");print(f"WROTE: {a.output}")
if __name__=="__main__":main()
