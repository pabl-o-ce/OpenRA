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

namespace OpenRA
{
	/// <summary>A local presentation queue. Admission is acknowledged even when coalesced or dropped.</summary>
	public sealed class NotificationQueue
	{
		sealed class Entry
		{
			public string Key;
			public int Priority;
			public long Expires;
			public Func<ISound> Play;
		}

		const int Capacity = 3;
		const int Lifetime = 3000;
		readonly List<Entry> pending = new();
		readonly Action<ISound> stop;
		Entry active;
		ISound sound;

		public NotificationQueue(Action<ISound> stop) { this.stop = stop; }

		public bool Enqueue(string key, int priority, bool interruptLowerPriority, long now, Func<ISound> play)
		{
			Tick(now);
			if (active?.Key == key || pending.Exists(e => e.Key == key))
				return true;

			var entry = new Entry { Key = key, Priority = priority, Expires = now + Lifetime, Play = play };
			if (sound != null && interruptLowerPriority && priority > active.Priority)
			{
				stop(sound);
				sound = null;
				active = null;
			}

			if (sound == null)
				return Start(entry);

			// Higher priorities go first; insertion order breaks ties.
			var index = pending.FindIndex(e => e.Priority < priority);
			pending.Insert(index < 0 ? pending.Count : index, entry);
			if (pending.Count > Capacity)
				pending.RemoveAt(Capacity);

			return true;
		}

		bool Start(Entry entry)
		{
			sound = entry.Play();
			active = sound == null ? null : entry;
			return sound != null;
		}

		public void Tick(long now)
		{
			pending.RemoveAll(e => e.Expires <= now);
			if (sound != null && !sound.Complete)
				return;

			sound = null;
			active = null;
			while (pending.Count > 0)
			{
				var next = pending[0];
				pending.RemoveAt(0);
				if (Start(next))
					break;
			}
		}

		public void Clear()
		{
			if (sound != null)
				stop(sound);
			sound = null;
			active = null;
			pending.Clear();
		}
	}
}
