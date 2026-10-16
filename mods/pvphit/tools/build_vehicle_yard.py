"""Build a separate vehicle review yard; never rewrite the core-building yard."""
from build_maps import MOD, terrain


def main():
    path = MOD/'maps/foundry-vehicle-yard'
    path.mkdir(parents=True,exist_ok=True)
    # The second field supports the late interruption/death tests after the original field depletes.
    terrain(path/'map.bin',112,((7,27,3),(5,43,4)))
    base = (MOD/'maps/foundry-systems-lab/map.yaml').read_text()
    header = base.split('Actors:')[0].replace('Foundry Systems Lab','Vehicle Review Yard')
    header = header.replace('MapSize: 48,48','MapSize: 112,112').replace('Bounds: 1,1,46,46','Bounds: 1,1,110,110')
    rules = 'Rules:'+base.split('Rules:',1)[1]
    rules = rules.replace('pvphit|maps/tank-proving-ground/systems.lua','yard.lua')
    start = rules.index('\t\t\tBriefing:')
    end = rules.index('\n',start)
    rules = rules[:start]+'\t\t\tBriefing: FC6 vehicle animation review. First inspect the working yard, capture and factory exits. Select the mortar and press F; move to withdraw. After 305 seconds the camera tours all 32 directions, deployed carriers, independent scout turrets and wrecks. No victory condition.'+rules[end:]
    # Review husks persist for the complete camera tour; gameplay husks are unchanged.
    rules = rules.replace('\tWorld:', '\tFC.TANK.HUSK:\n\t\t-ChangesHealth:\n\tWorld:')
    # Parked color samples; the working processor still spawns the real hauler.
    rules = rules.replace('\tWorld:',
              '\tFC.HAULER.DISPLAY:\n\t\tInherits: FC.HAULER\n\t\t-Buildable:\n'
              '\t\t-Harvester:\n\t\t-WithHarvestAnimation:\n\t\t-DockClientManager:\n\t\t-WithDockingAnimation:\n\tWorld:')
    actors = []
    def actor(name,kind,x,y,owner='Tester',extra=''):
        actors.append(f'\t{name}: {kind}\n\t\tOwner: {owner}\n\t\tLocation: {x},{y}\n'+extra)
    for y in range(12,39):
        for x in range(9,40):
            kind = 'hazard' if y in (12,38) else 'drain' if x==15 else 'concrete'
            actor(f'Floor{x}_{y}','fc.yard.'+kind,x,y,'Neutral')
    for name,kind,x,y in [('HQ','hq',10,14),('Generator','generator',17,14),
                         ('Processor','processor',10,23),('Factory','factory',33,14)]:
        actor(name,'fc.'+kind,x,y)
    actor('Tank','fc.tank',24,16,extra='\t\tFacing: 640\n\t\tTurretFacing: 640\n')
    actor('Scout','fc.scout',17,23,extra='\t\tFacing: 640\n\t\tTurretFacing: 640\n')
    actor('Facility','fc.facility',23,25,'Neutral')
    actor('Siege','fc.siege',23,33,extra='\t\tFacing: 0\n')
    actor('Target','fc.generator',30,33,'Blue')
    actor('RangeSiege','fc.siege',87,22,extra='\t\tDeployState: Deployed\n')
    actor('NearTarget','fc.generator',86,20,'Blue')
    actor('RangeTarget','fc.generator',94,21,'Blue')
    actor('FarTarget','fc.generator',101,21,'Blue')
    # Primary comparison rows in four player colors.
    for k,kind in enumerate(('hauler','scout','siege')):
        for i,owner in enumerate(('Tester','Blue','Yellow','Purple')):
            actor(f'Hero{k}_{i}','fc.'+kind+('.display' if kind=='hauler' else ''),19+i*5,20+k*4,owner,
                  '\t\tFacing: 640\n'+('\t\tTurretFacing: 640\n' if kind=='scout' else ''))
    # Eight-column grids keep each complete direction set on a native viewport.
    grids = [('Hauler','hauler',49,10,''),('Scout','scout',49,30,''),
             ('Siege','siege',49,50,''),('Braced','siege',49,70,'\t\tDeployState: Deployed\n'),
             ('HaulerWreck','hauler.husk',10,50,''),('ScoutWreck','scout.husk',10,70,''),
             ('SiegeWreck','siege.husk',10,90,'')]
    for label,kind,x0,y0,extra in grids:
        for i in range(32):
            owner = ('Tester','Blue','Yellow','Purple')[i//8]
            actor(f'{label}Facing{i}','fc.'+kind,x0+(i%8)*4,y0+(i//8)*4,owner,
                  f'\t\tFacing: {i*32}\n'+extra+
                  (f'\t\tTurretFacing: {i*32}\n' if kind=='scout' else ''))
    for i in range(32):
        actor(f'Independent{i}','fc.scout',49+(i%8)*4,90+(i//8)*4,
              ('Tester','Blue','Yellow','Purple')[i//8],f'\t\tFacing: {(i//8)*256}\n\t\tTurretFacing: {i*32}\n')
    (path/'map.yaml').write_text(header+'Actors:\n'+''.join(actors)+'\n'+rules)


if __name__=='__main__': main()
