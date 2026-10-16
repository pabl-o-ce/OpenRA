-- Private review fixture. The runner copies this beside an isolated map.
WorldLoaded = function()
    local p = Player.GetPlayer("Tester")
    local enemy = Player.GetPlayer("Blue")
    Camera.Position = Map.CenterOfCell(CPos.New(48,48))
    local scenario = "SCENARIO"
    local function later(seconds, f) Trigger.AfterDelay(DateTime.Seconds(seconds), f) end
    if scenario == "sample" or scenario == "muted" then
        local generator = Actor.Create("fc.generator", true, {Owner=p, Location=CPos.New(43,44)})
        Actor.Create("fc.factory", true, {Owner=p, Location=CPos.New(45,41)})
        Actor.Create("fc.processor", true, {Owner=p, Location=CPos.New(43,51)})
        local tank = Actor.Create("fc.tank", true, {Owner=p, Location=CPos.New(48,48)})
        tank.Stance = "HoldFire"
        local target = Actor.Create("fc.hq", true, {Owner=enemy, Location=CPos.New(52,47)})
        later(2, function() print("PRESENTATION INPUT select") end)
        later(5, function() print("PRESENTATION INPUT move") end)
        later(8, function() print("PRESENTATION INPUT attack") end)
        later(15, function()
            if target.Health >= target.MaxHealth then FatalError("PRESENTATION FAILED: real attack input did not damage target") end
            print("PRESENTATION PASSED: real attack input damaged target")
        end)
        later(16, function()
            generator.Destroy()
            print("PRESENTATION LOW POWER: actual generator removal")
        end)
        later(18, function() print("PRESENTATION CAPTURE warning") end)
        later(27, function()
            print("PRESENTATION CROWDED: twelve additional K6 tanks")
            for i=1,12 do
                local t=Actor.Create("fc.tank", true, {Owner=p, Location=CPos.New(48+(i%3),51+math.floor(i/3))})
                t.Attack(target, true, true)
            end
            Media.PlaySpeechNotification(p, "ConstructionComplete")
            Media.PlaySpeechNotification(p, "UnitReady")
            Media.PlaySpeechNotification(p, "InsufficientFunds")
            Media.PlaySpeechNotification(p, "BaseAttack")
        end)
        later(36, function() print("PRESENTATION COMPLETE") end)
    else
        -- Camera is identical for hidden and visible runs: attenuation cannot explain silence.
        -- The neutral attacker and Blue target do not grant Tester vision.
        local t = Actor.Create("fc.tank", true, {Owner=Player.GetPlayer("Neutral"), Location=CPos.New(48,48)})
        t.Stance = "HoldFire"
        local target = Actor.Create("fc.hq", true, {Owner=enemy, Location=CPos.New(52,47)})
        if scenario == "visible" then
            local observer = Actor.Create("fc.scout", true, {Owner=p, Location=CPos.New(48,43)})
            observer.Stance = "HoldFire"
        end
        later(7, function() t.Attack(target, false, true); print("PRESENTATION VISIBILITY: attack started") end)
        later(20, function() target.Kill(); print("PRESENTATION VISIBILITY: target destroyed") end)
        later(23, function() print("PRESENTATION COMPLETE") end)
    end
    later(1, function() print("PRESENTATION READY") end)
end
