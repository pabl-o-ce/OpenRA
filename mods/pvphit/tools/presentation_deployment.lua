-- Isolated visibility control: only deployment may produce world audio.
WorldLoaded = function()
    local p = Player.GetPlayer("Tester")
    Camera.Position = Map.CenterOfCell(CPos.New(48,48))
    local siege = Actor.Create("fc.siege",true,{Owner=p,Location=CPos.New(48,48)})
    local target = Actor.Create("fc.hq",true,{Owner=p,Location=CPos.New(48,42)})
    siege.Stance="HoldFire"
    if "SCENARIO" == "deployment-visible" then
        local watcher = Actor.Create("fc.scout",true,{Owner=p,Location=CPos.New(48,44)})
        watcher.Stance="HoldFire"
    end
    Trigger.AfterDelay(DateTime.Seconds(1),function() print("PRESENTATION READY") end)
    Trigger.AfterDelay(DateTime.Seconds(8),function() print("PRESENTATION INPUT selectall") end)
    Trigger.AfterDelay(DateTime.Seconds(10),function()
        print("PRESENTATION INPUT deploy")
        Trigger.AfterDelay(DateTime.Seconds(3),function() siege.Attack(target,true,true) end)
        Trigger.AfterDelay(DateTime.Seconds(10),function()
            if target.Health == target.MaxHealth then FatalError("PRESENTATION FAILED: initialized siege did not fire") end
            print("PRESENTATION PASSED: deployed siege damage")
            print("PRESENTATION COMPLETE")
        end)
    end)
end
