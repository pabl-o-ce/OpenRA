"""Reproduce the small industrial art/production test map; no competitive changes."""
from build_maps import MOD, terrain


def main():
    path = MOD/'maps/foundry-visual-yard'
    path.mkdir(parents=True, exist_ok=True)
    terrain(path/'map.bin',48,((7,18,3),))
    base = (MOD/'maps/foundry-systems-lab/map.yaml').read_text()
    header = base.split('Actors:')[0].replace('Foundry Systems Lab','Industrial Visual Yard')
    rules = 'Rules:'+base.split('Rules:',1)[1]
    rules = rules.replace('pvphit|maps/tank-proving-ground/systems.lua','yard.lua')
    rules = rules.replace('Inspect the 32 facing samples and independent turret row. Select red tanks to move and force-fire. Player colors must affect identification panels only. This laboratory has no victory condition.',
        'Inspect the K-6, Armor Works, player colors, damaged factory, and industrial paving at normal zoom. A scout is produced automatically to exercise the shutter. Move and force-fire the red tanks. Yard props and paving are decorative; this map has no victory condition.')
    actors=[]
    def actor(name,kind,x,y,owner='Neutral',extra=''):
        actors.append(f'\t{name}: {kind}\n\t\tOwner: {owner}\n\t\tLocation: {x},{y}\n'+extra)
    for y in range(12,33):
        for x in range(10,38):
            kind='concrete'
            if x==22:kind='road'
            elif x==17:kind='drain'
            elif y==12 or y==32:kind='hazard'
            actor(f'Floor{x}_{y}','fc.yard.'+kind,x,y)
    for name,kind,x,y in [('HQ','hq',10,13),('Generator','generator',16,13),
                           ('Processor','processor',10,20),('Factory','factory',24,13)]:
        actor(name,'fc.'+kind,x,y,'Tester')
    actor('DamagedFactory','fc.factory',32,13,'Blue','\t\tHealth: 30\n')
    actor('Tank','fc.tank',24,23,'Tester','\t\tFacing: 640\n\t\tTurretFacing: 640\n')
    actor('Target','fc.generator',33,25,'Blue')
    for i in range(8):
        actor(f'Facing{i}','fc.tank',12+i*3,29,['Tester','Blue','Yellow','Purple'][i//2],
              f'\t\tFacing: {i*128}\n\t\tTurretFacing: {i*128}\n')
    for i,(kind,x,y) in enumerate([('pressure-skid',19,14),('pipe',19,18),('pallet',29,18),
                                  ('barrier',28,25),('barrier',30,25),('pallet',36,20)]):
        actor(f'Prop{i}','fc.yard.'+kind,x,y)
    (path/'map.yaml').write_text(header+'Actors:\n'+''.join(actors)+'\n'+rules)
    (path/'yard.lua').write_text('''WorldLoaded = function()
    Camera.Position = Tank.CenterPosition
    local tester = Player.GetPlayer("Tester")
    Trigger.AfterDelay(DateTime.Seconds(10), function()
        if not tester.Build({ "fc.scout" }, function(units)
            if #units ~= 1 then FatalError("VISUAL YARD: unexpected factory output") end
            units[1].Move(CPos.New(24,21))
            print("VISUAL YARD PASSED: refined factory produced a scout")
        end) then FatalError("VISUAL YARD: production could not start") end
    end)
end
''')


if __name__ == '__main__':
    main()
