WorldLoaded = function()
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
