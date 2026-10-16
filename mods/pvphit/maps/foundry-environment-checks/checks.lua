-- Candidate-specific laboratory. No gameplay overrides are applied to the lobby map.
local failed = false
local players, haulers, trips, docked, produced, exited = {}, {}, {}, {}, {}, {}
local lastResources = {0,0}
local trial, trialStart, runners, arrivals = 0, 0, {}, {}
local phase = "travel"
local kinds = {"fc.scout", "fc.tank", "fc.siege"}
local destinations = {
    {"home", {19,53}, {78,53}},
    {"north-expansion", {44,32}, {52,32}},
    {"south-expansion", {45,65}, {53,65}},
    {"north-station", {47,19}, {50,19}},
    {"south-station", {47,79}, {50,79}}
}
local groups, groupGoals, groupBack, groupArrived, groupStart = {}, {}, {}, {}, 0
local carrier, victim, flank, withdrawalPosition, siegePhase, siegeTick
local captureScout, captureStart

local function check(ok, message)
    if not ok then failed = true; FatalError("ENVIRONMENT YARD FAILED: " .. message); return false end
    print("ENVIRONMENT YARD PASSED: " .. message)
    return true
end

local function travelNext()
    trial = trial + 1
    if trial > #destinations * #kinds then phase = "groups"; return end
    local d = destinations[(trial-1)%#destinations+1]
    local kind = kinds[math.floor((trial-1)/#destinations)+1]
    runners, arrivals = {}, {}
    trialStart = DateTime.GameTime
    for side=1,2 do
        local x = side == 1 and 14 or 83
        local unit = Actor.Create(kind, true, {Owner=players[side],Location=CPos.New(x,51),Facing=Angle.New(512)})
        runners[side] = unit
        unit.Move(CPos.New(d[side+1][1],d[side+1][2]))
    end
    print("ENVIRONMENT YARD: trial " .. trial .. " " .. kind .. " " .. d[1])
end

local function produce(side,index)
    local queue={"fc.hauler","fc.scout","fc.tank","fc.siege","fc.siege"}
    if index>#queue then return end
    check(players[side].Build({queue[index]},function(units)
        local unit=units[1]
        produced[side][index]=unit
        unit.Move(CPos.New(side==1 and 17 or 80,59+index))
        Trigger.AfterDelay(1,function() produce(side,index+1) end)
    end),"side " .. side .. " accepted paid " .. queue[index])
end

local function startGroups()
    groupStart=DateTime.GameTime
    for side=1,2 do
        Actor.Create("fc.generator",true,{Owner=players[side],Location=CPos.New(side==1 and 17 or 79,45)})
        Actor.Create("fc.processor",true,{Owner=players[side],Location=CPos.New(side==1 and 20 or 75,42)})
        Actor.Create("fc.factory",true,{Owner=players[side],Location=CPos.New(side==1 and 13 or 82,51)})
    end
    Trigger.AfterDelay(DateTime.Seconds(3),function()
        for side=1,2 do
            haulers[side][1]=players[side].GetActorsByType("fc.hauler")[1]
            trips[side][1]=0
            check(haulers[side][1]~=nil,"side " .. side .. " opening processor supplied hauler")
            produce(side,1)
        end
    end)
    for lane=1,3 do
        local sy=lane==1 and 38 or lane==2 and 47 or 58
        for i=0,11 do
            local dx,dy=i%4,math.floor(i/4)
            local unit=Actor.Create("fc.tank",true,{Owner=players[1],Location=CPos.New(25+dx*2,sy+dy*2)})
            local index=#groups+1;groups[index]=unit
            local fy=lane==1 and 17 or lane==2 and 47 or 75
            if lane~=2 then
                unit.Move(CPos.New(32+dx,fy+dy));unit.Move(CPos.New(62+dx,fy+dy))
            end
            -- Leave a cell between parked tanks so exact goals cannot be sealed by neighbors.
            groupGoals[index]=CPos.New(66+dx*2,sy+dy*2)
            groupBack[index]=CPos.New(25+dx*2,sy+dy*2)
            unit.Move(groupGoals[index])
        end
    end
    phase="groups-out"
end

local function siegeStart()
    phase="siege"
    carrier=Actor.Create("fc.siege",true,{Owner=players[1],Location=CPos.New(44,35),Facing=Angle.New(0)})
    victim=Actor.Create("fc.generator",true,{Owner=players[2],Location=CPos.New(50,34)})
    flank=Actor.Create("fc.scout",true,{Owner=players[2],Location=CPos.New(34,40)})
    flank.Move(CPos.New(44,34))
    siegePhase="deploy";siegeTick=DateTime.GameTime
    Camera.Position=carrier.CenterPosition
    Trigger.OnDamaged(victim,function(self,attacker,amount)
        if attacker~=carrier or amount<=0 or siegePhase~="fire" then return end
        check(amount==13750,"candidate siege damage unchanged")
        carrier.Stop();siegePhase="withdraw";siegeTick=DateTime.GameTime
        withdrawalPosition=carrier.CenterPosition
        Camera.Position=carrier.CenterPosition
        print("VEHICLE INPUT: withdraw cycle 1")
    end)
    print("VEHICLE INPUT: deploy cycle 1")
end

WorldLoaded=function()
    players={Player.GetPlayer("Tester"),Player.GetPlayer("Blue")}
    Camera.Position=WPos.New(24*1024,48*1024,0)
    for side=1,2 do
        haulers[side]={};trips[side]={};docked[side]={};produced[side]={};exited[side]={}
    end
    Trigger.AfterDelay(DateTime.Seconds(3),function()
        travelNext()
    end)
    Trigger.AfterDelay(DateTime.Seconds(850),function()
        if phase~="complete" then check(false,"overall timeout in phase " .. phase) end
    end)
    for _,view in ipairs({{105,48,48},{145,48,22},{175,48,76},{295,77,48},{330,48,48}}) do
        Trigger.AfterDelay(DateTime.Seconds(view[1]),function()
            Camera.Position=WPos.New(view[2]*1024,view[3]*1024,0)
        end)
    end
end

Tick=function()
    if failed or phase=="complete" or #players==0 then return end
    for side=1,2 do
        for i,unit in pairs(produced[side]) do
            if not exited[side][i] and unit.Location==CPos.New(side==1 and 17 or 80,59+i) then
                exited[side][i]=true
                print("ENVIRONMENT YARD: side " .. side .. " output " .. i .. " reached destination")
                if i==1 then
                    haulers[side][2]=unit;trips[side][2]=0;unit.FindResources()
                else unit.Destroy() end
            end
        end
        for i,unit in pairs(haulers[side]) do
            local atDock=unit.Location==CPos.New(side==1 and 21 or 76,44)
            if atDock and players[side].Resources>lastResources[side] then docked[side][i]=true
            elseif not atDock and docked[side][i] then
                trips[side][i]=trips[side][i]+1;docked[side][i]=false
                print("ENVIRONMENT YARD: side " .. side .. " hauler " .. i .. " trips " .. trips[side][i])
            end
        end
        -- Laboratory-only: keep storage available for repeated delivery observation.
        if players[side].Resources>2000 then players[side].Resources=1000 end
        lastResources[side]=players[side].Resources
    end
    if phase=="travel" and trial>0 then
        local d=destinations[(trial-1)%#destinations+1]
        for side,unit in ipairs(runners) do
            if not arrivals[side] and unit.Location==CPos.New(d[side+1][1],d[side+1][2]) and unit.IsIdle then
                arrivals[side]=DateTime.GameTime-trialStart
            end
        end
        if arrivals[1] and arrivals[2] then
            print("ENVIRONMENT YARD: arrival ticks trial " .. trial .. " west " .. arrivals[1] .. " east " .. arrivals[2])
            check(math.abs(arrivals[1]-arrivals[2])/math.min(arrivals[1],arrivals[2])<=.05,"paired travel within five percent: " .. trial)
            for _,unit in ipairs(runners) do unit.Destroy() end
            Trigger.AfterDelay(1,travelNext);phase="travel-next"
        elseif DateTime.GameTime-trialStart>DateTime.Seconds(75) then check(false,"travel timeout " .. trial) end
    elseif phase=="travel-next" then phase="travel"
    elseif phase=="groups" then startGroups()
    elseif phase=="groups-out" or phase=="groups-back" then
        local all=true
        for i,unit in ipairs(groups) do
            local goal=phase=="groups-out" and groupGoals[i] or groupBack[i]
            if unit.Location==goal and unit.IsIdle then groupArrived[i]=true end
            if not groupArrived[i] then all=false end
        end
        if all then
            check(true,"three twelve-tank groups completed " .. phase)
            if phase=="groups-out" then
                for i,unit in ipairs(groups) do
                    local lane=math.floor((i-1)/12)+1;local dx=(i-1)%4;local dy=math.floor(((i-1)%12)/4)
                    local fy=lane==1 and 17 or 75
                    if lane~=2 then unit.Move(CPos.New(62+dx,fy+dy));unit.Move(CPos.New(32+dx,fy+dy)) end
                    unit.Move(groupBack[i])
                end
                phase="groups-back";groupArrived={};groupStart=DateTime.GameTime
            else
                for _,unit in ipairs(groups) do unit.Destroy() end
                siegeStart()
            end
        elseif DateTime.GameTime-groupStart>DateTime.Seconds(100) then
            for i,unit in ipairs(groups) do
                if not groupArrived[i] then print("ENVIRONMENT YARD: stranded tank " .. i .. " at " .. tostring(unit.Location)) end
            end
            check(false,"tank group timeout " .. phase)
        end
    elseif phase=="siege" then
        if siegePhase=="deploy" and DateTime.GameTime-siegeTick>DateTime.Seconds(4) then
            carrier.Attack(victim,false,true);siegePhase="fire";siegeTick=DateTime.GameTime
        elseif siegePhase=="withdraw" and carrier.CenterPosition~=withdrawalPosition then
            check(DateTime.GameTime-siegeTick>=DateTime.Seconds(2),"withdrawal completed before translation")
            check(flank.Location==CPos.New(44,34),"scout reached siege position around wall")
            carrier.Destroy();victim.Destroy();flank.Destroy()
            captureScout=Actor.Create("fc.scout",true,{Owner=players[1],Location=CPos.New(40,20)})
            captureScout.Capture(NorthFacility);captureStart=DateTime.GameTime;phase="capture"
            Camera.Position=NorthFacility.CenterPosition
        elseif DateTime.GameTime-siegeTick>DateTime.Seconds(30) then check(false,"real-input siege timeout " .. siegePhase) end
    elseif phase=="capture" then
        if NorthFacility.Owner==players[1] then
            check(not captureScout.IsDead,"candidate station capture preserves scout")
            phase="economy"
        elseif DateTime.GameTime-captureStart>DateTime.Seconds(30) then check(false,"capture timeout") end
    elseif phase=="economy" then
        local ready=true
        for side=1,2 do
            for i=1,5 do if not exited[side][i] then ready=false end end
            if #haulers[side]~=2 or trips[side][1]<1 or (trips[side][2] or 0)<1 or trips[side][1]+(trips[side][2] or 0)<10 then ready=false end
        end
        if ready then
            for side=1,2 do
                for i=1,5 do check(exited[side][i],"side " .. side .. " production exit " .. i) end
                check(#haulers[side]==2 and trips[side][1]>=1 and trips[side][2]>=1 and trips[side][1]+trips[side][2]>=10,
                    "side " .. side .. " two haulers completed at least ten aggregate deliveries")
            end
            if not failed then phase="complete";print("ENVIRONMENT YARD PASSED: candidate systems suite complete") end
        end
    end
end
