"""Reproduce the expanded industrial visual yard for core-building acceptance.

Writes only foundry-visual-yard. Run this after build_visual_yard.py if rebuilding
both generations; this pass intentionally owns the expanded yard layout.
"""
from build_maps import MOD, terrain


def main():
    path = MOD/'maps/foundry-visual-yard'
    path.mkdir(parents=True,exist_ok=True)
    terrain(path/'map.bin',48,((6,27,3),))
    base = (MOD/'maps/foundry-systems-lab/map.yaml').read_text()
    header = base.split('Actors:')[0].replace('Foundry Systems Lab','Industrial Visual Yard')
    rules = 'Rules:'+base.split('Rules:',1)[1]
    rules = rules.replace('pvphit|maps/tank-proving-ground/systems.lua','yard.lua')
    start = rules.index('\t\t\tBriefing:')
    end = rules.index('\n',start)
    rules = rules[:start]+('\t\t\tBriefing: Core building review: HQ, generator and processor rows show red, blue, yellow, purple and damaged red. Below: heavy factory and tank references. At 30 seconds purple buildings take damage; at 45 seconds they recover. At 50 seconds new buildings assemble on the lower apron. Keep the lab running for two minutes to check repeated deliveries and factory production.')+rules[end:]
    actors = []
    def actor(name,kind,x,y,owner='Neutral',extra=''):
        actors.append(f'\t{name}: {kind}\n\t\tOwner: {owner}\n\t\tLocation: {x},{y}\n'+extra)
    for y in range(12,41):
        for x in range(9,39):
            kind = 'hazard' if y in (12,40) else 'drain' if x==15 else 'concrete'
            actor(f'Floor{x}_{y}','fc.yard.'+kind,x,y)
    for label,kind,y in [('HQ','hq',14),('Generator','generator',20),('Processor','processor',26)]:
        for i,owner in enumerate(('Tester','Blue','Yellow','Purple','Tester')):
            name = label if i==0 else 'Damaged'+label if i==4 else label+str(i)
            actor(name,'fc.'+kind,10+6*i,y,owner,'\t\tHealth: 30\n' if i==4 else '')
    actor('Factory','fc.factory',10,33,'Tester')
    actor('DamagedFactory','fc.factory',17,33,'Blue','\t\tHealth: 30\n')
    actor('Tank','fc.tank',24,33,'Tester','\t\tFacing: 640\n\t\tTurretFacing: 640\n')
    for i in range(8):
        actor(f'Facing{i}','fc.tank',11+i*3,38,('Tester','Blue','Yellow','Purple')[i//2],
              f'\t\tFacing: {i*128}\n\t\tTurretFacing: {i*128}\n')
    (path/'map.yaml').write_text(header+'Actors:\n'+''.join(actors)+'\n'+rules)
    (path/'yard.lua').write_text('''-- Visual-only laboratory; no changes to competitive map rules.
local deliveries = 0
local lastResources = 0
local hauler = nil
local sawDock = false
local completedTrips = 0
local produced = false

WorldLoaded = function()
    Camera.Position = WPos.New(24 * 1024, 26 * 1024, 0)
    local tester = Player.GetPlayer("Tester")
    Trigger.AfterDelay(DateTime.Seconds(5), function()
        local haulers = tester.GetActorsByType("fc.hauler")
        -- Choose the free hauler spawned beside the leftmost processor.
        for _, unit in ipairs(haulers) do
            if unit.Location.X < 20 then hauler = unit end
        end
        if not hauler then FatalError("CORE YARD FAILED: free hauler missing") end
    end)
    Trigger.AfterDelay(DateTime.Seconds(10), function()
        if not tester.Build({ "fc.scout" }, function(units)
            if #units ~= 1 then FatalError("CORE YARD FAILED: factory output") end
            units[1].Move(CPos.New(20,36))
            produced = true
            print("CORE YARD PASSED: heavy factory produced a scout")
        end) then FatalError("CORE YARD FAILED: production could not start") end
    end)
    Trigger.AfterDelay(DateTime.Seconds(30), function()
        HQ3.Health = math.floor(HQ3.MaxHealth * 0.3)
        Generator3.Health = math.floor(Generator3.MaxHealth * 0.3)
        Processor3.Health = math.floor(Processor3.MaxHealth * 0.3)
        print("CORE YARD: purple buildings damaged")
    end)
    Trigger.AfterDelay(DateTime.Seconds(45), function()
        HQ3.Health = HQ3.MaxHealth
        Generator3.Health = Generator3.MaxHealth
        Processor3.Health = Processor3.MaxHealth
        print("CORE YARD: purple buildings restored")
    end)
    Trigger.AfterDelay(DateTime.Seconds(50), function()
        Actor.Create("fc.generator", true, { Owner = tester, Location = CPos.New(28,33) })
        Actor.Create("fc.processor", true, { Owner = tester, Location = CPos.New(34,33) })
        print("CORE YARD: construction animations started")
    end)
    Trigger.AfterDelay(DateTime.Seconds(120), function()
        if not produced or deliveries < 2 or completedTrips < 2 then
            FatalError("CORE YARD FAILED: production/delivery checks: " .. deliveries .. " income increments, " .. completedTrips .. " dock departures")
        end
        print("CORE YARD PASSED: repeated unloading and departure; suite complete")
    end)
end

Tick = function()
    local tester = Player.GetPlayer("Tester")
    if tester.Resources > lastResources then deliveries = deliveries + 1 end
    lastResources = tester.Resources
    if hauler and not hauler.IsDead then
        local dock = CPos.New(11,28)
        if hauler.Location == dock then
            sawDock = true
        elseif sawDock then
            completedTrips = completedTrips + 1
            sawDock = false
            print("CORE YARD: dock departure " .. completedTrips)
        end
    end
end
''')


if __name__ == '__main__':
    main()
