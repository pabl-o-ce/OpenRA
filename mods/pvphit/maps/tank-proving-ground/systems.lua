-- The interactive laboratory reports economy/capture outcomes to lua.log.
WorldLoaded = function()
	local tester = Player.GetPlayer("Tester")
	local produced = false
	Camera.Position = Processor.CenterPosition
	Trigger.AfterDelay(DateTime.Seconds(60), function()
		if tester.Resources <= 0 then
			FatalError("FURNACE CHECK FAILED: hauler did not deliver slag")
		end
		print("FURNACE CHECK PASSED: harvesting and refinery delivery")
		if not tester.Build({ "fc.scout" }, function(units)
			if #units ~= 1 or units[1].Type ~= "fc.scout" then
				FatalError("FURNACE CHECK FAILED: factory output")
			end
			produced = true
			print("FURNACE CHECK PASSED: paid production and factory exit")
		end) then
			FatalError("FURNACE CHECK FAILED: scout production could not start")
		end
	end)
	Trigger.AfterDelay(DateTime.Seconds(100), function()
		if not produced then
			FatalError("FURNACE CHECK FAILED: production did not finish in time")
		end
		print("FURNACE CHECK PASSED: systems suite complete")
	end)
	Trigger.AfterDelay(DateTime.Seconds(3), function()
		-- Harvesting fills Resources; Cash alone proves the station's trickle.
		local cashBefore = tester.Cash
		Scout.Capture(Facility)
		Trigger.AfterDelay(DateTime.Seconds(20), function()
			if Facility.Owner ~= tester then
				FatalError("FURNACE CHECK FAILED: scout did not capture facility")
			end
			if Scout.IsDead then
				FatalError("FURNACE CHECK FAILED: scout was consumed")
			end
			if tester.Cash <= cashBefore then
				FatalError("FURNACE CHECK FAILED: economy did not generate income")
			end
			print("FURNACE CHECK PASSED: capture, surviving scout, and income")
			print("Power: " .. tester.PowerProvided .. " provided / " .. tester.PowerDrained .. " consumed")
		end)
	end)
end
