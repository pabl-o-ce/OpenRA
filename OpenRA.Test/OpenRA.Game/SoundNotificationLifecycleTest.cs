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
using System.IO;
using NUnit.Framework;
using OpenRA.FileSystem;
using OpenRA.GameRules;
using OpenRA.Graphics;
using OpenRA.Primitives;

namespace OpenRA.Test
{
	[TestFixture, NonParallelizable]
	public class SoundNotificationLifecycleTest
	{
		sealed class Clip : ISound
		{
			public float Volume { get; set; }
			public float SeekPosition => 0;
			public bool Complete { get; set; }
			public void SetPosition(WPos pos) { }
		}

		sealed class Source : ISoundSource { public void Dispose() { } }

		sealed class Backend : ISoundEngine
		{
			public readonly List<Clip> Clips = new();
			public bool Dummy => false;
			public float Volume { get; set; }
			public SoundDevice[] AvailableDevices() => Array.Empty<SoundDevice>();
			public ISoundSource AddSoundSourceFromMemory(byte[] data, int channels, int sampleBits, int sampleRate) => new Source();
			public ISound Play2D(ISoundSource source, bool loop, bool relative, WPos pos, float volume, bool attenuateVolume)
			{
				var clip = new Clip { Volume = volume };
				Clips.Add(clip);
				return clip;
			}
			public ISound Play2DStream(Stream stream, int channels, int bits, int rate, bool loop, bool relative, WPos pos, float volume) =>
				Play2D(new Source(), loop, relative, pos, volume, false);
			public void StopSound(ISound sound) { ((Clip)sound).Complete = true; }
			public void StopAllSounds() { Clips.ForEach(c => c.Complete = true); }
			public void PauseSound(ISound sound, bool paused) { }
			public void SetAllSoundsPaused(bool paused) { }
			public void SetListenerPosition(WPos position) { }
			public void SetSoundVolume(float volume, ISound music, ISound video) { }
			public void SetSoundLooping(bool looping, ISound sound) { }
			public void SetSoundPosition(ISound sound, WPos position) { }
			public void Dispose() { }
		}

		sealed class TestPlatform : IPlatform
		{
			public readonly Backend Backend = new();
			public ISoundEngine CreateSound(string device) => Backend;
			public IFont CreateFont(byte[] data) => throw new NotSupportedException();
			public IPlatformWindow CreateWindow(Size size, WindowMode mode, float scale, int vertices, int indices, int display, GLProfile profile) =>
				throw new NotSupportedException();
		}

		sealed class Files : IReadOnlyFileSystem
		{
			public Stream Open(string filename) => new MemoryStream(new byte[2]);
			public bool Exists(string filename) => true;
			public bool IsExternalFile(string filename) => false;
			public bool TryOpen(string filename, out Stream stream) { stream = Open(filename); return true; }
			public bool TryGetPackageContaining(string path, out IReadOnlyPackage package, out string filename)
			{ package = null; filename = path; return false; }
		}

		sealed class Format : ISoundFormat
		{
			public int Channels => 1;
			public int SampleBits => 16;
			public int SampleRate => 44100;
			public float LengthInSeconds => 1;
			public Stream GetPCMInputStream() => new MemoryStream(new byte[2]);
			public void Dispose() { }
		}

		sealed class Loader : ISoundLoader
		{
			public bool TryParseSound(Stream stream, out ISoundFormat format) { format = new Format(); return true; }
		}

		[TestCase("mute")]
		[TestCase("effects")]
		[TestCase("stop")]
		[TestCase("initialize")]
		[TestCase("disabled")]
		public void SoundLifecycleDiscardsPendingAnnouncements(string transition)
		{
			var previousSettings = Game.Settings;
			try
			{
				Game.Settings = new Settings(Path.Combine(Path.GetTempPath(), Guid.NewGuid() + ".yaml"), new Arguments(Array.Empty<string>()));
				var platform = new TestPlatform();
				using var sound = new Sound(platform, Game.Settings.Sound);
				var loaders = new ISoundLoader[] { new Loader() };
				var files = new Files();
				sound.Initialize(loaders, files);
				var info = new SoundInfo(new MiniYaml(null, MiniYaml.FromString("Notifications:\n\tFirst: first.wav\n\t\tUseFullPath: true\n\t\tGroup: test\n\tSecond: second.wav\n\t\tUseFullPath: true\n\t\tGroup: test\n", "test")));
				var rules = new Ruleset(new Dictionary<string, ActorInfo>(), new Dictionary<string, WeaponInfo>(),
					new Dictionary<string, SoundInfo>(), new Dictionary<string, SoundInfo> { ["speech"] = info },
					new Dictionary<string, MusicInfo>(), null, new Dictionary<string, MiniYamlNode>());
				Assert.That(sound.PlayNotification(rules, null, "Speech", "First", null), Is.True);
				Assert.That(sound.PlayNotification(rules, null, "Speech", "Second", null), Is.True);
				Assert.That(platform.Backend.Clips.Count, Is.EqualTo(1));
				// Music-only changes must not discard the effects announcement group.
				sound.MusicVolume = 0;
				sound.Tick();
				Assert.That(platform.Backend.Clips[0].Complete, Is.False);
				switch (transition)
				{
					case "mute": sound.MuteAudio(); sound.UnmuteAudio(); break;
					case "effects": sound.SoundVolume = 0; sound.SoundVolume = 1; break;
					case "stop": sound.StopAudio(); break;
					case "initialize": sound.Initialize(loaders, files); break;
					case "disabled": sound.DisableAllSounds = true; sound.Tick(); sound.DisableAllSounds = false; break;
				}
				Assert.That(platform.Backend.Clips[0].Complete, Is.True);
				sound.Tick();
				Assert.That(platform.Backend.Clips.Count, Is.EqualTo(1), "Stale second notification must not restart");
				Assert.That(sound.PlayNotification(rules, null, "Speech", "Second", null), Is.True);
				Assert.That(platform.Backend.Clips.Count, Is.EqualTo(2), "New notifications must still work");
			}
			finally { Game.Settings = previousSettings; }
		}
	}
}
