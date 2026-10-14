-- Visual-only laboratory; no changes to competitive map rules.
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
