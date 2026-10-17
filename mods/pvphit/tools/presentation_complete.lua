-- Private completion review: real resources, orders, deploy input and mixed combat.
WorldLoaded = function()
    local p = Player.GetPlayer("Tester")
    local enemy = Player.GetPlayer("Blue")
    local function later(seconds, f) Trigger.AfterDelay(DateTime.Seconds(seconds), f) end
    local processor = Actor.Create("fc.processor", true, {Owner=p, Location=CPos.New(23,47)})
    local generator = Actor.Create("fc.generator", true, {Owner=p, Location=CPos.New(18,45)})
    Actor.Create("fc.factory", true, {Owner=p, Location=CPos.New(14,51)})
    local siege = Actor.Create("fc.siege", true, {Owner=p, Location=CPos.New(30,49)})
    siege.Stance = "HoldFire"
    local scout = Actor.Create("fc.scout", true, {Owner=p, Location=CPos.New(27,50)})
    scout.Stance = "HoldFire"
    local target = Actor.Create("fc.hq", true, {Owner=enemy, Location=CPos.New(36,48)})
    Camera.Position = siege.CenterPosition
    later(1, function() print("PRESENTATION READY") end)
    later(2, function() print("PRESENTATION INPUT select") end)
    later(4, function() print("PRESENTATION INPUT deploy") end)
    later(8, function() siege.Attack(target, true, true) end)
    later(14, function()
        if target.Health == target.MaxHealth then FatalError("PRESENTATION FAILED: siege did not fire after deploy") end
        print("PRESENTATION PASSED: real deploy input and siege damage")
        generator.Destroy()
    end)
    later(16, function() print("PRESENTATION CAPTURE warning") end)
    later(18, function()
        -- Exercise a real sidebar-ready state without changing production rules.
        p.Build({"fc.generator"})
        p.Build({"fc.scout"}, function(units)
            print("PRESENTATION PASSED: paid scout produced")
        end)
        for _, key in ipairs({"ConstructionComplete", "UnitReady", "InsufficientFunds", "BaseAttack", "NewOptions", "UnitLost"}) do
            Media.PlaySpeechNotification(p, key)
        end
        print("PRESENTATION INPUT mute")
    end)
    later(19, function() print("PRESENTATION INPUT hold") end)
    later(21, function() print("PRESENTATION CAPTURE held") end)
    later(22, function() print("PRESENTATION INPUT unmute") end)
    later(24, function() print("PRESENTATION INPUT resume") end)
    later(26, function()
        -- A fresh warning after unmute; the discarded backlog must not return.
        Media.PlaySpeechNotification(p, "BaseAttack")
        print("PRESENTATION UNMUTED fresh warning")
        Camera.Position = processor.CenterPosition
    end)
    later(50, function()
        if p.Resources <= 0 then FatalError("PRESENTATION FAILED: no accepted resource transfer") end
        print("PRESENTATION PASSED: actual resource transfer " .. p.Resources)
        p.Resources = p.ResourceCapacity
        print("PRESENTATION STORAGE full; rejected transfers must not sound")
    end)
    later(58, function()
        p.Resources = 0
        print("PRESENTATION STORAGE reopened")
        Camera.Position = siege.CenterPosition
        print("PRESENTATION INPUT withdraw")
    end)
    later(65, function()
        p.Cash = 999999
        print("PRESENTATION INPUT chat")
    end)
    later(70, function()
        Media.DisplayMessage("Pressure Station Nine: resource transfer restored. Protect the approach and keep the south-facing processor dock clear.", "Kiln Directorate")
        print("PRESENTATION CAPTURE longtext")
    end)
    later(72, function()
        if p.Resources <= 0 then FatalError("PRESENTATION FAILED: resource transfer did not recover") end
        print("PRESENTATION PASSED: accepted transfers recovered")
        print("PRESENTATION COMPLETE")
    end)
end
