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

using NUnit.Framework;
using OpenRA.Mods.Common.Traits.Sound;
using OpenRA.Mods.Common.Traits;
using OpenRA.Mods.Common.Warheads;

namespace OpenRA.Test
{
	[TestFixture]
	public class ResourceSoundThrottleTest
	{
		[Test]
		public void ExistingSoundFieldsRemainOptIn()
		{
			Assert.That(new ArmamentInfo().SoundsRequireVisibility, Is.False);
			Assert.That(new GrantConditionOnDeployInfo().SoundsRequireVisibility, Is.False);
			Assert.That(new SoundOnDamageTransitionInfo().SoundsRequireVisibility, Is.False);
			Assert.That(new CreateEffectWarhead().ImpactSoundRequiresVisibility, Is.False);
			var resources = new ResourceActivitySoundsInfo();
			Assert.That(resources.SoundsRequireVisibility, Is.False);
			Assert.That(resources.HarvestSounds, Is.Empty);
			Assert.That(resources.TransferSounds, Is.Empty);
		}

		[Test]
		public void CooldownDoesNotQueueHiddenOrRejectedEvents()
		{
			var throttle = new ResourceSoundThrottle();
			var plays = 0;
			bool Play() { plays++; return true; }
			Assert.That(throttle.TryPlay(0, 1000, false, Play), Is.False);
			Assert.That(throttle.TryPlay(0, 1000, true, Play), Is.True);
			Assert.That(throttle.TryPlay(999, 1000, true, Play), Is.False);
			Assert.That(throttle.TryPlay(1000, 1000, false, Play), Is.False);
			Assert.That(throttle.TryPlay(1100, 1000, true, Play), Is.True);
			Assert.That(plays, Is.EqualTo(2));
		}

		[Test]
		public void FailedSourceDoesNotConsumeCooldownAndActorsAreIndependent()
		{
			var first = new ResourceSoundThrottle();
			var second = new ResourceSoundThrottle();
			Assert.That(first.TryPlay(10, 1000, true, () => false), Is.False);
			Assert.That(first.TryPlay(10, 1000, true, () => true), Is.True);
			Assert.That(second.TryPlay(10, 1000, true, () => true), Is.True);
		}
	}
}
