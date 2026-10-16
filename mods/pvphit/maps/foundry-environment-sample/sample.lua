-- Native terrain/prop inspection and smoke checks only.
local produced, departed = nil, false
WorldLoaded = function()
    Camera.Position = WPos.New(24*1024,23*1024,0)
    local p = Player.GetPlayer("Tester")
    Trigger.AfterDelay(DateTime.Seconds(3), function() Scout.Capture(Facility) end)
    Trigger.AfterDelay(DateTime.Seconds(5), function()
        p.Build({"fc.siege"}, function(units)
            produced = units[1]
            produced.Move(CPos.New(36,22))
        end)
    end)
    Trigger.AfterDelay(DateTime.Seconds(100), function()
        if not departed or Facility.Owner ~= p or Scout.IsDead or p.Resources == 0 then
            FatalError("ENVIRONMENT YARD FAILED: production/capture/harvest smoke check")
            return
        end
        print("ENVIRONMENT YARD PASSED: sample smoke suite complete")
    end)
end
Tick = function()
    if produced and produced.Location == CPos.New(36,22) then departed = true end
end
