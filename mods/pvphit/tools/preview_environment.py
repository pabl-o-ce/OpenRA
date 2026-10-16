"""Create a labeled layout diagram from the actual map binary and actor list."""
import html
from pathlib import Path
from check_environment import read_map, actors
from environment_ground import MOD, IDS


def main():
    _,_,tiles,resources=read_map((MOD/'maps/pressure-station-nine/map.bin').read_bytes())
    scale=7;ox,oy=36,70
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="830" viewBox="0 0 760 830">',
         '<rect width="760" height="830" fill="#1d2223"/>',
         '<g font-family="sans-serif" fill="#e7e3d6">',
         '<text x="36" y="30" font-size="21">Pressure Station Nine — transfer yard</text>',
         '<text x="36" y="51" font-size="12">Actual cells • paving and ash both traversable • walls block movement only</text></g>']
    for (x,y),(tile,index) in tiles.items():
        if not 1<=x<=96 or not 1<=y<=96:continue
        color='#42413d' if tile in [IDS[f'ash-{i}'] for i in range(4)] else '#5d5f59'
        if (x,y) in resources:color='#a18968'
        svg.append(f'<rect x="{ox+(x-1)*scale}" y="{oy+(y-1)*scale}" width="7" height="7" fill="{color}"/>')
    for name,kind,x,y in actors((MOD/'maps/pressure-station-nine/map.yaml').read_text()):
        px,py=ox+(x-1)*scale,oy+(y-1)*scale
        if kind=='mpspawn':svg.append(f'<circle cx="{px+3.5}" cy="{py+3.5}" r="9" fill="#b54839" stroke="#f4dfba"/>')
        elif kind=='fc.facility':svg.append(f'<rect x="{px}" y="{py}" width="14" height="14" fill="#e5d4aa"/>')
        elif '.wall-' in kind:svg.append(f'<rect x="{px}" y="{py}" width="7" height="7" fill="#d9d1b9"/>')
        else:svg.append(f'<circle cx="{px+3.5}" cy="{py+3.5}" r="1.5" fill="#b66747"/>')
    svg.append('<g font-family="sans-serif" font-size="13" fill="#fff3d8" text-anchor="middle" stroke="#1d2223" stroke-width="3" paint-order="stroke">')
    for x,y,label in [(49,9,'NORTH METER'),(49,88,'SOUTH METER'),(14,33,'WEST BASE'),(83,33,'EAST BASE'),
                      (49,49,'TRANSFER APRON'),(23,61,'HOME SLAG'),(74,61,'HOME SLAG'),
                      (48,34,'NORTH EXTRACTION'),(49,64,'SOUTH EXTRACTION'),(75,82,'BROKEN MANIFOLD')]:
        svg.append(f'<text x="{ox+(x-1)*scale}" y="{oy+(y-1)*scale}">{html.escape(label)}</text>')
    svg.append('</g><g font-family="sans-serif" font-size="13" fill="#ddd9cb">'
               '<text x="36" y="772">54,200 nominal resource credits retained; economic rules unchanged.</text>'
               '<text x="36" y="793">Access checks and mirrored opportunities are not evidence of competitive balance.</text></g></svg>')
    (MOD/'docs/environment-layout.svg').write_text('\n'.join(svg)+'\n')


if __name__=='__main__':main()
