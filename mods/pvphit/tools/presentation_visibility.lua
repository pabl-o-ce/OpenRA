-- Same combat event stream across visibility and camera changes; never replay missed sounds.
WorldLoaded = function()
    local p=Player.GetPlayer("Tester")
    local tank=Actor.Create("fc.tank",true,{Owner=Player.GetPlayer("Neutral"),Location=CPos.New(48,48)})
    local target=Actor.Create("fc.hq",true,{Owner=Player.GetPlayer("Blue"),Location=CPos.New(52,47)})
    local watcher
    local function reveal()
        watcher=Actor.Create("fc.scout",true,{Owner=p,Location=CPos.New(48,43)})
        watcher.Stance="HoldFire"
    end
    local function later(t,f) Trigger.AfterDelay(DateTime.Seconds(t),f) end
    Camera.Position=Map.CenterOfCell(CPos.New(48,48))
    reveal()
    later(1,function() print("PRESENTATION READY") end)
    later(3,function() tank.Attack(target,true,true);print("PRESENTATION PHASE visible") end)
    later(12,function() watcher.Destroy();print("PRESENTATION PHASE lostvision") end)
    later(22,function() reveal();print("PRESENTATION PHASE regained") end)
    later(32,function() Camera.Position=Map.CenterOfCell(CPos.New(10,10));print("PRESENTATION PHASE distant") end)
    later(42,function() Camera.Position=Map.CenterOfCell(CPos.New(48,48));print("PRESENTATION PHASE returned") end)
    later(50,function()
        if target.Health==target.MaxHealth then FatalError("PRESENTATION FAILED: visibility control did not fire") end
        print("PRESENTATION COMPLETE")
    end)
end
