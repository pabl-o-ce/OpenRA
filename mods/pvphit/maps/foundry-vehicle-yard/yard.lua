-- Local art regression checks only. Competitive actors and economy are unchanged.
local hauler, sawDock, trips, deliveries, lastResources = nil, false, 0, 0, 0
local produced, exited = {}, {}
local failed = false
local function check(ok, message)
    if not ok then failed = true; FatalError("VEHICLE YARD FAILED: " .. message); return end
    print("VEHICLE YARD PASSED: " .. message)
end

WorldLoaded = function()
    local tester = Player.GetPlayer("Tester")
    Camera.Position = WPos.New(24 * 1024, 25 * 1024, 0)
    Trigger.OnDamaged(Target, function(self, attacker, amount)
        print("VEHICLE SIEGE: target damage " .. amount .. " at tick " .. DateTime.GameTime)
    end)
    Trigger.AfterDelay(DateTime.Seconds(5), function()
        Siege.Attack(Target, false, true)
        RangeSiege.Attack(NearTarget, false, true)
    end)
    Trigger.AfterDelay(DateTime.Seconds(10), function()
        check(Target.Health == Target.MaxHealth, "undeployed siege cannot fire")
        check(NearTarget.Health == NearTarget.MaxHealth, "mortar minimum range enforced")
        Siege.Stop()
        RangeSiege.Stop()
        RangeSiege.Attack(FarTarget, false, true)
    end)
    Trigger.AfterDelay(DateTime.Seconds(15), function()
        check(FarTarget.Health == FarTarget.MaxHealth, "mortar maximum range enforced")
        RangeSiege.Stop()
        RangeSiege.Attack(RangeTarget, false, true)
    end)
    Trigger.AfterDelay(DateTime.Seconds(28), function()
        check(RangeTarget.Health < RangeTarget.MaxHealth, "deployed mortar fires within range")
        RangeSiege.Stop()
    end)
    Trigger.AfterDelay(DateTime.Seconds(3), function()
        for _, unit in ipairs(tester.GetActorsByType("fc.hauler")) do
            if unit.Location.X < 15 and unit.Location.Y < 40 then hauler = unit end
        end
        check(hauler ~= nil, "processor spawned free hauler")
        Scout.Capture(Facility)
    end)
    Trigger.AfterDelay(DateTime.Seconds(24), function()
        check(Facility.Owner == tester and not Scout.IsDead, "scout captured station without consumption")
    end)
    local function produce(index)
        local kinds = { "fc.hauler", "fc.scout", "fc.siege" }
        if index > #kinds then return end
        local kind = kinds[index]
        check(tester.Build({ kind }, function(units)
            check(#units == 1 and units[1].Type == kind, "paid factory produced " .. kind)
            produced[kind] = units[1]
            units[1].Move(CPos.New(37,23 + index * 2))
            -- Production's callback runs before the queue releases its script lock.
            Trigger.AfterDelay(1, function() produce(index + 1) end)
        end), "factory accepted " .. kind)
    end
    Trigger.AfterDelay(DateTime.Seconds(8), function() produce(1) end)
    Trigger.AfterDelay(DateTime.Seconds(195), function()
        check(trips >= 2 and deliveries >= 2, "repeated harvesting, unloading and departure")
        for _,kind in ipairs({ "fc.hauler", "fc.scout", "fc.siege" }) do
            check(exited[kind], kind .. " cleared factory exit")
        end
        if not failed then print("VEHICLE YARD PASSED: systems suite complete") end
    end)
    -- Real facing/turret actors and persistent wrecks, shown without zoom changes.
    local views = {
        { 63, 16, "hauler directions" }, { 63, 36, "scout directions" },
        { 63, 56, "siege directions" }, { 63, 76, "deployed directions" },
        { 63, 96, "independent scout turrets" }, { 24, 56, "hauler wrecks" },
        { 24, 76, "scout wrecks" }, { 24, 96, "siege wrecks" }
    }
    for i,v in ipairs(views) do
        Trigger.AfterDelay(DateTime.Seconds(150 + (i-1)*5), function()
            Camera.Position = WPos.New(v[1]*1024,v[2]*1024,0)
            print("VEHICLE VIEW: " .. v[3])
        end)
    end
    Trigger.AfterDelay(DateTime.Seconds(190), function()
        Camera.Position = WPos.New(24*1024,25*1024,0)
        print("VEHICLE YARD: visual tour complete")
    end)
end

Tick = function()
    local tester = Player.GetPlayer("Tester")
    if tester.Resources > lastResources then deliveries = deliveries + 1 end
    lastResources = tester.Resources
    if hauler and not hauler.IsDead then
        if hauler.Location == CPos.New(11,25) then sawDock = true
        elseif sawDock then trips = trips + 1; sawDock = false; print("VEHICLE YARD: dock departure " .. trips) end
    end
    for kind,unit in pairs(produced) do
        if not unit.IsDead and unit.Location.Y > 18 then exited[kind] = true end
    end
end
