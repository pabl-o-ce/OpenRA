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
using OpenRA.Traits;

namespace OpenRA.Mods.Common.Traits.Sound
{
	[Desc("Short positional sounds for actual harvesting and accepted refinery transfers. No idle or docking sounds.")]
	public class ResourceActivitySoundsInfo : TraitInfo
	{
		public readonly string[] HarvestSounds = Array.Empty<string>();
		public readonly string[] TransferSounds = Array.Empty<string>();

		[Desc("Minimum milliseconds between successful sound starts on this actor. Local presentation time only.")]
		public readonly int Cooldown = 1000;

		public readonly float Volume = 0.5f;

		[Desc("Require both actor and position visibility to the rendering player.")]
		public readonly bool SoundsRequireVisibility = false;

		public override object Create(ActorInitializer init) { return new ResourceActivitySounds(this); }
	}

	// No synchronized state: admission never changes the resource event that triggered it.
	public sealed class ResourceSoundThrottle
	{
		long next;

		public bool TryPlay(long now, int cooldown, bool eligible, Func<bool> play)
		{
			if (!eligible || now < next || !play())
				return false;

			next = now + Math.Max(0, cooldown);
			return true;
		}
	}

	public class ResourceActivitySounds : INotifyHarvestAction, INotifyResourceAccepted
	{
		readonly ResourceActivitySoundsInfo info;
		readonly ResourceSoundThrottle throttle = new();

		public ResourceActivitySounds(ResourceActivitySoundsInfo info) { this.info = info; }

		void Play(Actor self, string[] sounds)
		{
			var visible = !info.SoundsRequireVisibility ||
				(!self.World.FogObscures(self) && !self.World.FogObscures(self.CenterPosition));
			throttle.TryPlay(Game.RunTime, info.Cooldown, visible && sounds.Length > 0,
				() => Game.Sound.Play(SoundType.World, sounds.RandomOrDefault(Game.CosmeticRandom),
					self.CenterPosition, info.Volume) != null);
		}

		void INotifyHarvestAction.Harvested(Actor self, string resourceType) { Play(self, info.HarvestSounds); }
		void INotifyHarvestAction.MovingToResources(Actor self, CPos targetCell) { }
		void INotifyHarvestAction.MovementCancelled(Actor self) { }

		void INotifyResourceAccepted.OnResourceAccepted(Actor self, Actor refinery, string resourceType, int count, int value)
		{
			// Refinery broadcasts to all same-owner listeners, including empty/rejected transfers.
			if (self == refinery && count > 0 && value > 0)
				Play(self, info.TransferSounds);
		}
	}
}
