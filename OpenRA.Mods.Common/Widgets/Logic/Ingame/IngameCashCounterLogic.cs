#region Copyright & License Information
/*
 * Copyright (c) The OpenRA Developers and Contributors
 * This file is part of OpenRA, which is free software. It is made
 * available to you under the terms of the GNU General Public License
 * as published by the Free Software Foundation, either version 3 of
 * the License, or (at your option) any later version. For more
 * information, see COPYING.
 */
#endregion

using System;
using System.Collections.Generic;
using System.Globalization;
using OpenRA.Mods.Common.Traits;
using OpenRA.Primitives;
using OpenRA.Widgets;

namespace OpenRA.Mods.Common.Widgets.Logic
{
	public class IngameCashCounterLogic : ChromeLogic
	{
		[FluentReference("usage", "capacity")]
		const string SiloUsage = "label-silo-usage";

		const float DisplayFracPerFrame = .07f;
		const int DisplayDeltaPerFrame = 37;

		readonly World world;
		readonly Player player;
		readonly PlayerResources playerResources;
		readonly LabelWithTooltipWidget cashLabel;
		readonly CachedTransform<(int Resources, int Capacity), string> siloUsageTooltipCache;
		readonly bool compactDisplay;

		int nextCashTickTime = 0;
		int displayResources;

		string siloUsageTooltip = "";

		[ObjectCreator.UseCtor]
		public IngameCashCounterLogic(Widget widget, ModData modData, World world, Dictionary<string, MiniYaml> logicArgs)
		{
			this.world = world;
			compactDisplay = logicArgs.TryGetValue("CompactDisplay", out var compact) && FieldLoader.GetValue<bool>("CompactDisplay", compact.Value);
			player = world.LocalPlayer;
			playerResources = player.PlayerActor.Trait<PlayerResources>();
			displayResources = playerResources.GetCashAndResources();

			siloUsageTooltipCache = new CachedTransform<(int Resources, int Capacity), string>(x =>
				FluentProvider.GetMessage(SiloUsage, "usage", x.Resources, "capacity", x.Capacity));
			cashLabel = widget.Get<LabelWithTooltipWidget>("CASH");
			cashLabel.GetTooltipText = () => compactDisplay
				? playerResources.GetCashAndResources().ToString(CultureInfo.CurrentCulture) + "\n" + siloUsageTooltip
				: siloUsageTooltip;
		}

		// Keep fixed-width counters readable; the existing tooltip retains exact amounts.
		public static string CompactValue(int value)
		{
			var magnitude = Math.Abs((long)value);
			if (magnitude < 10000)
				return value.ToString(CultureInfo.CurrentCulture);
			var divisor = magnitude >= 1000000 ? 1000000 : 1000;
			var scaled = (double)value / divisor;
			var compact = Math.Abs(scaled) < 100 ? Math.Truncate(scaled * 10) / 10 : Math.Truncate(scaled);
			return compact.ToString("0.#", CultureInfo.InvariantCulture) + (divisor == 1000 ? "k" : "M");
		}

		public override void Tick()
		{
			if (nextCashTickTime > 0)
				nextCashTickTime--;

			var actual = playerResources.GetCashAndResources();

			var diff = Math.Abs(actual - displayResources);
			var move = Math.Min(Math.Max((int)(diff * DisplayFracPerFrame), DisplayDeltaPerFrame), diff);

			if (displayResources < actual)
			{
				displayResources += move;

				if (Game.Settings.Sound.CashTicks)
					Game.Sound.PlayNotification(world.Map.Rules, player, "Sounds", playerResources.Info.CashTickUpNotification, player.Faction.InternalName);
			}
			else if (displayResources > actual)
			{
				displayResources -= move;

				if (Game.Settings.Sound.CashTicks && nextCashTickTime == 0)
				{
					Game.Sound.PlayNotification(world.Map.Rules, player, "Sounds", playerResources.Info.CashTickDownNotification, player.Faction.InternalName);
					nextCashTickTime = 2;
				}
			}

			siloUsageTooltip = siloUsageTooltipCache.Update((playerResources.Resources, playerResources.ResourceCapacity));
			var displayResourcesText = compactDisplay ? CompactValue(displayResources) : displayResources.ToString(CultureInfo.CurrentCulture);
			cashLabel.GetText = () => displayResourcesText;
		}
	}
}
