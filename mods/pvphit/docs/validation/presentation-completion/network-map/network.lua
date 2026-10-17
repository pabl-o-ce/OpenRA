-- Two controlling clients issue real deploy/withdraw orders; resource accounting is asserted on every peer/replay.
WorldLoaded = function()
    local west, east = Player.GetPlayer("Tester"), Player.GetPlayer("Blue")
    local neutral = Player.GetPlayer("Neutral")
    local units, targets = {}, {}
    for i, owner in ipairs({west, east}) do
        local x = i == 1 and 23 or 74
        Actor.Create("fc.generator", true, {Owner=owner, Location=CPos.New(x-5,45)})
        Actor.Create("fc.processor", true, {Owner=owner, Location=CPos.New(x,47)})
        units[i] = Actor.Create("fc.siege", true, {Owner=owner, Location=CPos.New(42+i*4,48)})
        units[i].Stance = "HoldFire"
        targets[i] = Actor.Create("fc.hq", true, {Owner=neutral, Location=CPos.New(41+i*4,42)})
    end
    Camera.Position = Map.CenterOfCell(CPos.New(48,48))
    local function later(seconds, f) Trigger.AfterDelay(DateTime.Seconds(seconds), f) end
    later(2, function() print("NETWORK INPUT deploy") end)
    later(8, function()
        for i=1,2 do units[i].Attack(targets[i],true,true) end
    end)
    later(18, function()
        for i=1,2 do
            if targets[i].Health == targets[i].MaxHealth then FatalError("NETWORK FAILED: player "..i.." did not deploy/fire") end
        end
        print("NETWORK PASSED: both controlling clients deployed and fired")
        for _,p in ipairs({west,east}) do
            Media.PlaySpeechNotification(p,"ConstructionComplete")
            Media.PlaySpeechNotification(p,"BaseAttack")
            Media.PlaySpeechNotification(p,"NewOptions")
        end
        print("NETWORK INPUT local mute")
    end)
    later(25, function() print("NETWORK INPUT withdraw") end)
    later(35, function()
        for i=1,2 do
            if units[i].Location.Y < 51 then FatalError("NETWORK FAILED: player "..i.." did not withdraw/move") end
        end
        print("NETWORK PASSED: both controlling clients withdrew and moved")
    end)
    later(70, function()
        if west.Resources <= 0 or east.Resources <= 0 then FatalError("NETWORK FAILED: resources not delivered on both sides") end
        print("NETWORK RESULT "..west.Resources..","..east.Resources..","..targets[1].Health..","..targets[2].Health..","..units[1].Location.X..","..units[1].Location.Y..","..units[2].Location.X..","..units[2].Location.Y)
        print("NETWORK suite complete")
    end)
end
