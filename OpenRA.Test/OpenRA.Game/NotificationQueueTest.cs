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

using System.Collections.Generic;
using NUnit.Framework;
using OpenRA.GameRules;

namespace OpenRA.Test
{
	[TestFixture]
	public class NotificationQueueTest
	{
		sealed class Clip : ISound
		{
			public float Volume { get; set; }
			public float SeekPosition => 0;
			public bool Complete { get; set; }
			public void SetPosition(WPos pos) { }
		}

		[Test]
		public void CoalescesAndInterruptsWithoutResumingStaleSpeech()
		{
			var plays = new List<string>();
			var clip = new Clip();
			var stops = 0;
			var queue = new NotificationQueue(_ => stops++);
			Assert.That(queue.Enqueue("complete", 0, false, 0, () => { plays.Add("complete"); return clip; }), Is.True);
			Assert.That(queue.Enqueue("complete", 0, false, 1, () => { plays.Add("duplicate"); return clip; }), Is.True);
			queue.Enqueue("power", 1, false, 2, () => { plays.Add("power"); return clip; });
			queue.Enqueue("power", 1, false, 3, () => { plays.Add("duplicate"); return clip; });
			queue.Enqueue("attack", 2, true, 4, () => { plays.Add("attack"); return clip; });
			Assert.That(stops, Is.EqualTo(1));
			Assert.That(plays, Is.EqualTo(new[] { "complete", "attack" }));
			clip.Complete = true;
			queue.Tick(5);
			Assert.That(plays, Is.EqualTo(new[] { "complete", "attack", "power" }));
		}

		[Test]
		public void BoundedQueuePrioritizesWarningsAndExpiresPendingEvents()
		{
			var plays = new List<string>();
			var clip = new Clip();
			var queue = new NotificationQueue(_ => { });
			queue.Enqueue("active", 0, false, 0, () => clip);
			foreach (var name in new[] { "a", "b", "c", "d" })
				queue.Enqueue(name, 0, false, 1, () => { plays.Add(name); return clip; });
			queue.Enqueue("warning", 1, false, 2, () => { plays.Add("warning"); return clip; });
			clip.Complete = true;
			queue.Tick(3);
			queue.Tick(4);
			queue.Tick(5);
			queue.Tick(6);
			Assert.That(plays, Is.EqualTo(new[] { "warning", "a", "b" }));
			clip.Complete = false;
			queue.Enqueue("active", 0, false, 10, () => clip);
			queue.Enqueue("expired", 0, false, 11, () => { plays.Add("expired"); return clip; });
			clip.Complete = true;
			queue.Tick(3011);
			Assert.That(plays, Does.Not.Contain("expired"));
		}

		[Test]
		public void ClearStopsActiveAndDiscardsPendingForMuteOrWorldChange()
		{
			var clip = new Clip();
			var stops = 0;
			var queue = new NotificationQueue(_ => stops++);
			queue.Enqueue("active", 0, false, 0, () => clip);
			queue.Enqueue("pending", 1, false, 1, () => { Assert.Fail("Must not replay after clear"); return clip; });
			queue.Clear();
			queue.Tick(2);
			queue.Clear();
			Assert.That(stops, Is.EqualTo(1));
		}

		[Test]
		public void FailedPlaybackDoesNotBlockFollowingNotifications()
		{
			var queue = new NotificationQueue(_ => { });
			Assert.That(queue.Enqueue("missing", 0, false, 0, () => null), Is.False);
			Assert.That(queue.Enqueue("valid", 0, false, 1, () => new Clip()), Is.True);
		}

		[Test]
		public void NotificationOptionsAreOptInAndPreserveLegacySettings()
		{
			const string Yaml = "Notifications:\n\tLegacy: old\n\t\tInterruptType: Overlap\n\t\tVolumeModifier: 0.33\n\tNew: custom.wav\n\t\tGroup: alerts\n\t\tPriority: 2\n\t\tInterruptLowerPriority: true\n\t\tUseFullPath: true\n";
			var info = new SoundInfo(new MiniYaml(null, MiniYaml.FromString(Yaml, "test")));
			var legacy = info.NotificationsPools.Value["Legacy"];
			Assert.That(legacy.Group, Is.Null);
			Assert.That(legacy.UseFullPath, Is.False);
			Assert.That(legacy.Type, Is.EqualTo(SoundPool.InterruptType.Overlap));
			Assert.That(legacy.VolumeModifier, Is.EqualTo(.33f));
			var current = info.NotificationsPools.Value["New"];
			Assert.That(current.Group, Is.EqualTo("alerts"));
			Assert.That(current.Priority, Is.EqualTo(2));
			Assert.That(current.InterruptLowerPriority && current.UseFullPath, Is.True);
		}
	}
}
