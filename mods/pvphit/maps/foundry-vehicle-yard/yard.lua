-- Local art regression checks only. Competitive actors and economy are unchanged.
local hauler, sawDock, trips, deliveries, lastResources = nil, false, 0, 0, 0
local produced, exited, destinations = {}, {}, {}
local carriers = {}
local cycle, current, phase, phaseTick = 0, nil, nil, 0
local cycleTarget
local completedCycles = 0
local withdrawalPosition
local deathsStarted, deathCount, firingVictim, harvestVictim, harvestPosition, harvestStill = false, 0, nil, nil, nil, 0
local unloadKilled, dockInterrupted, dockInterruptPending = false, false, false
local deathsStartTick = 0
local failed = false
local function check(ok, message)
    if not ok then failed = true; FatalError("VEHICLE YARD FAILED: " .. message); return end
    print("VEHICLE YARD PASSED: " .. message)
end

local function killCheck(unit, state)
    unit.Kill("ExplosionDeath")
    deathCount = deathCount + 1
    Trigger.AfterDelay(3, function()
        check(unit.IsDead, "death during " .. state)
    end)
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
    cycleTarget = Actor.Create("fc.generator", true, { Owner = Player.GetPlayer("Blue"), Location = CPos.New(43,31) })
    Trigger.OnDamaged(cycleTarget, function(self, attacker, amount)
        if amount <= 0 then return end
        self.Health = self.MaxHealth
        if firingVictim and attacker == firingVictim and not firingVictim.IsDead then killCheck(firingVictim, "tank firing") end
        if attacker == current and phase == "firing" then
            check(amount == 13750, "produced mortar damage preserved")
            phase, phaseTick = "withdrawing", DateTime.GameTime
            withdrawalPosition = current.CenterPosition
            Camera.Position = current.CenterPosition
            print("VEHICLE INPUT: withdraw cycle " .. cycle)
        end
    end)
    local function produce(index)
        local kinds = { "fc.hauler", "fc.scout", "fc.siege", "fc.siege", "fc.siege" }
        if index > #kinds then return end
        local kind = kinds[index]
        check(tester.Build({ kind }, function(units)
            check(#units == 1 and units[1].Type == kind, "paid factory produced " .. kind)
            produced[index] = units[1]
            destinations[index] = CPos.New(37,23 + index * 2)
            units[1].Move(destinations[index])
            if kind == "fc.siege" then table.insert(carriers, units[1]) end
            -- Production's callback runs before the queue releases its script lock.
            Trigger.AfterDelay(1, function() produce(index + 1) end)
        end), "factory accepted " .. kind)
    end
    Trigger.AfterDelay(DateTime.Seconds(8), function() produce(1) end)
    Trigger.AfterDelay(DateTime.Seconds(360), function()
        check(trips >= 2 and deliveries >= 2, "repeated harvesting, unloading and departure")
        for index = 1,5 do
            check(exited[index], "produced vehicle " .. index .. " cleared factory and reached destination")
        end
        check(dockInterrupted, "hauler departed after dock interruption and resumed harvesting")
        check(deathCount == 6, "six animation-state destruction checks completed")
        check(completedCycles == 6, "three produced carriers each deployed, fired and withdrew twice")
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
        Trigger.AfterDelay(DateTime.Seconds(305 + (i-1)*5), function()
            Camera.Position = WPos.New(v[1]*1024,v[2]*1024,0)
            print("VEHICLE VIEW: " .. v[3])
        end)
    end
    Trigger.AfterDelay(DateTime.Seconds(350), function()
        Camera.Position = WPos.New(24*1024,25*1024,0)
        print("VEHICLE YARD: visual tour complete")
    end)
end

Tick = function()
    local tester = Player.GetPlayer("Tester")
    if tester.Resources > lastResources then
        deliveries = deliveries + 1
        print("VEHICLE ECONOMY: " .. DateTime.GameTime .. " resources " .. tester.Resources)
    end
    if deathsStarted and DateTime.GameTime - deathsStartTick > 250 and not unloadKilled
        and not dockInterruptPending and hauler and not hauler.IsDead
        and hauler.Location == CPos.New(11,25) and tester.Resources > lastResources then
        if not dockInterrupted then
            dockInterruptPending = true
            Camera.Position = hauler.CenterPosition
            print("VEHICLE INPUT: dock interruption")
            Trigger.AfterDelay(100, function()
                check(hauler.Location ~= CPos.New(11,25), "hauler accepted movement interrupt at dock")
                dockInterrupted, dockInterruptPending = true, false
                hauler.Stop()
                hauler.FindResources()
            end)
        else
            unloadKilled = true
            killCheck(hauler, "hauler unloading")
        end
    end
    lastResources = tester.Resources
    if harvestVictim and not harvestVictim.IsDead then
        if harvestVictim.CenterPosition == harvestPosition then harvestStill = harvestStill + 1 else harvestStill = 0 end
        harvestPosition = harvestVictim.CenterPosition
        local harvestCell = harvestVictim.Location
        -- A cell can stay unchanged while traversing it. Require exact physical rest.
        if harvestCell.X < 10 and harvestCell.Y >= 25 and harvestCell.Y < 48 and harvestStill == 5 then
            killCheck(harvestVictim, "hauler harvesting")
        end
    end
    if hauler and not hauler.IsDead then
        if hauler.Location == CPos.New(11,25) then sawDock = true
        elseif sawDock then trips = trips + 1; sawDock = false; print("VEHICLE YARD: dock departure " .. trips .. " tick " .. DateTime.GameTime) end
    end
    for index,unit in pairs(produced) do
        if not unit.IsDead and unit.Location == destinations[index] then exited[index] = true end
    end
    -- Real input is required: this fork's Lua Deploy API only supports Transforms.
    if not phase and #carriers == 3 and exited[3] and exited[4] and exited[5] then
        phase = "next"
    end
    if phase == "next" then
        cycle = cycle + 1
        if cycle > 6 then
            phase = "complete"
            tester.Resources = 0 -- Make room for the unloading-death observation only.
            deathsStarted = true
            deathsStartTick = DateTime.GameTime
            local scout = Actor.Create("fc.scout", true, { Owner = tester, Location = CPos.New(36,37) })
            scout.Move(CPos.New(43,37))
            Trigger.AfterDelay(20, function() killCheck(scout, "scout movement") end)
            firingVictim = Actor.Create("fc.tank", true, { Owner = tester, Location = CPos.New(40,34) })
            firingVictim.Attack(cycleTarget, false, true)
            harvestVictim = produced[1]
            harvestVictim.FindResources()
            Camera.Position = carriers[1].CenterPosition
            print("VEHICLE INPUT: deploy cycle 7")
            Trigger.AfterDelay(45, function() killCheck(carriers[1], "siege deployment") end)
            Trigger.AfterDelay(75, function()
                Camera.Position = carriers[2].CenterPosition
                print("VEHICLE INPUT: deploy cycle 8")
            end)
            Trigger.AfterDelay(175, function()
                print("VEHICLE INPUT: withdraw cycle 8")
                Trigger.AfterDelay(25, function() killCheck(carriers[2], "siege withdrawal") end)
            end)
            return
        end
        current = carriers[math.floor((cycle-1)/2)+1]
        Camera.Position = current.CenterPosition
        phase, phaseTick = "deploying", DateTime.GameTime
        print("VEHICLE INPUT: deploy cycle " .. cycle)
    elseif phase == "deploying" and DateTime.GameTime - phaseTick == 100 then
        current.Attack(cycleTarget, false, true)
        phase, phaseTick = "firing", DateTime.GameTime
    elseif phase == "firing" and DateTime.GameTime - phaseTick > 250 then
        check(false, "produced carrier fired after real deploy input, cycle " .. cycle)
    elseif phase == "withdrawing" then
        local elapsed = DateTime.GameTime - phaseTick
        if elapsed == 25 then
            check(current.CenterPosition == withdrawalPosition, "withdrawal completes before translation")
        elseif elapsed == 150 then
            check(current.Location == CPos.New(cycle % 2 == 1 and 35 or 37,29 + 2 * math.floor((cycle-1)/2)), "produced carrier withdrew and moved, cycle " .. cycle)
            completedCycles = completedCycles + 1
            phase = "next"
        end
    end
end
