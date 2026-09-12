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
using System.IO;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using NUnit.Framework;
using OpenRA.Mods.Common.Server;
using OpenRA.Server;

namespace OpenRA.Test
{
	[TestFixture]
	public class OutcomeEventTest
	{
		const string AliceFingerprint = "2c05c8594a171cfd4ff340155092e89d3d1d64d7";
		const string BobFingerprint = "9e107d9d372bb6826bd81d3542a419d6f0b7a1c3";
		const string PvpHitVersion = "pvphit-20250330.1";
		const string MapUid = "8b0f4a7d2c3e1f9a6b5c4d3e2f1a0b9c8d7e6f5a";

		static readonly Dictionary<int, int> RosterProfiles = new() { { 0, 100042 }, { 1, 100057 } };

		static string ReadFixture(string name)
		{
			using (var stream = typeof(OutcomeEventTest).Assembly.GetManifestResourceStream("OpenRaOutcome." + name))
			using (var reader = new StreamReader(stream))
				return reader.ReadToEnd();
		}

		// Re-serializes a fixture compactly, keeping timestamps as the strings they are and property order as written
		static string Compact(string json)
		{
			using (var reader = new JsonTextReader(new StringReader(json)) { DateParseHandling = DateParseHandling.None })
				return JToken.ReadFrom(reader).ToString(Formatting.None);
		}

		static DateTime Utc(string value)
		{
			return DateTime.Parse(value, CultureInfo.InvariantCulture, DateTimeStyles.AssumeUniversal | DateTimeStyles.AdjustToUniversal);
		}

		static GameInformation.Player MakePlayer(int clientIndex, string name, string fingerprint,
			WinState outcome = WinState.Undefined, string outcomeAt = null, int disconnectFrame = 0)
		{
			return new GameInformation.Player
			{
				ClientIndex = clientIndex,
				Name = name,
				IsHuman = true,
				Fingerprint = fingerprint,
				Outcome = outcome,
				OutcomeTimestampUtc = outcomeAt != null ? Utc(outcomeAt) : default,
				DisconnectFrame = disconnectFrame,
			};
		}

		static GameInformation MakeGameInfo(string startedAt, params GameInformation.Player[] players)
		{
			var gameInfo = new GameInformation
			{
				Mod = "pvphit",
				Version = PvpHitVersion,
				MapUid = MapUid,
				StartTimeUtc = Utc(startedAt),
			};

			foreach (var p in players)
				gameInfo.Players.Add(p);

			return gameInfo;
		}

		static GameOutcome MakeOutcome(GameOutcomeReason reason, GameInformation gameInfo, string finalizedAt,
			string replay = "pvphit-Server-2026-09-07T140102Z.orarep", Dictionary<int, int> profiles = null)
		{
			return new GameOutcome(reason, gameInfo, replay, Utc(finalizedAt), profiles ?? RosterProfiles, PvpHitVersion);
		}

		static string BuildJson(GameOutcome outcome, string matchId = "8d3f1c2a-1b2c-4d5e-8f90-0a1b2c3d4e5f")
		{
			return OutcomeEventBuilder.Serialize(OutcomeEventBuilder.Build(outcome, matchId));
		}

		static JObject Parse(string json)
		{
			using (var reader = new JsonTextReader(new StringReader(json)) { DateParseHandling = DateParseHandling.None })
				return (JObject)JToken.ReadFrom(reader);
		}

		[TestCase(TestName = "Result matches the final fixture")]
		public void FinalFixture()
		{
			var gameInfo = MakeGameInfo("2026-09-07T14:01:02Z",
				MakePlayer(0, "alice", AliceFingerprint, WinState.Won, "2026-09-07T14:23:40Z"),
				MakePlayer(1, "bob", BobFingerprint, WinState.Lost, "2026-09-07T14:23:40Z"));

			var outcome = MakeOutcome(GameOutcomeReason.Result, gameInfo, "2026-09-07T14:23:40Z");
			Assert.That(BuildJson(outcome), Is.EqualTo(Compact(ReadFixture("final.json"))));
		}

		[TestCase(TestName = "End game without a result matches the unresolved fixture")]
		public void UnresolvedFixture()
		{
			var gameInfo = MakeGameInfo("2026-09-07T15:10:00Z",
				MakePlayer(0, "alice", AliceFingerprint),
				MakePlayer(1, "bob", BobFingerprint, disconnectFrame: 12750));

			var outcome = MakeOutcome(GameOutcomeReason.EndGame, gameInfo, "2026-09-07T15:18:31Z", "pvphit-Server-2026-09-07T151000Z.orarep");
			Assert.That(BuildJson(outcome, "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f"), Is.EqualTo(Compact(ReadFixture("unresolved.json"))));
		}

		[TestCase(TestName = "Out of sync matches the desync fixture")]
		public void DesyncFixture()
		{
			var gameInfo = MakeGameInfo("2026-09-07T16:00:00Z",
				MakePlayer(0, "alice", AliceFingerprint),
				MakePlayer(1, "bob", BobFingerprint));

			var outcome = MakeOutcome(GameOutcomeReason.OutOfSync, gameInfo, "2026-09-07T16:04:12Z", "pvphit-Server-2026-09-07T160000Z.orarep");
			Assert.That(BuildJson(outcome, "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f70"), Is.EqualTo(Compact(ReadFixture("desync.json"))));
		}

		[TestCase(TestName = "Serialized event is a single line")]
		public void SingleLine()
		{
			var gameInfo = MakeGameInfo("2026-09-07T14:01:02Z", MakePlayer(0, "line\nbreak", AliceFingerprint), MakePlayer(1, "bob", BobFingerprint));
			var json = BuildJson(MakeOutcome(GameOutcomeReason.EndGame, gameInfo, "2026-09-07T14:02:02Z"));

			Assert.That(json, Does.Not.Contain("\n"));
			Assert.That(json, Does.Not.Contain("\r"));
		}

		[TestCase("8d3f1c2a-1b2c-4d5e-8f90-0a1b2c3d4e5f", "a50faa44-9662-5c5d-bae2-4d5275dece77", TestName = "event_id is the RFC 4122 v5 id (final)")]
		[TestCase("c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f", "a55ea9eb-02d8-5527-9e95-64d6bac084c1", TestName = "event_id is the RFC 4122 v5 id (unresolved)")]
		[TestCase("d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f70", "11531046-6e01-5f6f-974d-232e024df2e4", TestName = "event_id is the RFC 4122 v5 id (desync)")]
		public void EventId(string matchId, string expected)
		{
			var eventId = OutcomeEventBuilder.DeriveEventId(matchId);

			Assert.That(eventId, Is.EqualTo(expected));
			Assert.That(OutcomeEventBuilder.DeriveEventId(matchId), Is.EqualTo(eventId));
			Assert.That(eventId[14], Is.EqualTo('5'));
			Assert.That("89ab", Does.Contain(eventId[19].ToString()));
		}

		[TestCase(GameOutcomeReason.Result, WinState.Won, WinState.Lost, "final", "result")]
		[TestCase(GameOutcomeReason.EndGame, WinState.Undefined, WinState.Undefined, "unresolved", "end_game")]
		[TestCase(GameOutcomeReason.EndGame, WinState.Won, WinState.Lost, "final", "end_game")]
		[TestCase(GameOutcomeReason.EndGame, WinState.Won, WinState.Undefined, "unresolved", "end_game")]
		[TestCase(GameOutcomeReason.Shutdown, WinState.Undefined, WinState.Undefined, "unresolved", "shutdown")]
		[TestCase(GameOutcomeReason.Shutdown, WinState.Lost, WinState.Won, "final", "shutdown")]
		[TestCase(GameOutcomeReason.OutOfSync, WinState.Undefined, WinState.Undefined, "desync", "out_of_sync")]
		[TestCase(GameOutcomeReason.OutOfSync, WinState.Won, WinState.Lost, "desync", "out_of_sync")]
		public void StateTable(GameOutcomeReason reason, WinState first, WinState second, string state, string reasonName)
		{
			var gameInfo = MakeGameInfo("2026-09-07T14:01:02Z",
				MakePlayer(0, "alice", AliceFingerprint, first, first == WinState.Undefined ? null : "2026-09-07T14:23:40Z"),
				MakePlayer(1, "bob", BobFingerprint, second, second == WinState.Undefined ? null : "2026-09-07T14:23:40Z"));

			var outcomeEvent = OutcomeEventBuilder.Build(MakeOutcome(reason, gameInfo, "2026-09-07T14:23:40Z"), "8d3f1c2a-1b2c-4d5e-8f90-0a1b2c3d4e5f");

			Assert.That(outcomeEvent.State, Is.EqualTo(state));
			Assert.That(outcomeEvent.Reason, Is.EqualTo(reasonName));
		}

		[TestCase(TestName = "Missing values serialize as explicit nulls")]
		public void NullMappings()
		{
			var gameInfo = MakeGameInfo("2026-09-07T14:01:02Z",
				MakePlayer(7, "guest", ""),
				MakePlayer(1, "bob", null, WinState.Lost, "2026-09-07T14:10:00Z", 4200));

			var json = Parse(BuildJson(MakeOutcome(GameOutcomeReason.EndGame, gameInfo, "2026-09-07T14:10:00Z", replay: null,
				profiles: new Dictionary<int, int>())));

			Assert.That(json["replay"].Type, Is.EqualTo(JTokenType.Null));

			var guest = json["players"][0];
			Assert.That(guest["fingerprint"].Type, Is.EqualTo(JTokenType.Null));
			Assert.That(guest["profile_id"].Type, Is.EqualTo(JTokenType.Null));
			Assert.That(guest["outcome"].Value<string>(), Is.EqualTo("Undefined"));
			Assert.That(guest["outcome_at"].Type, Is.EqualTo(JTokenType.Null));
			Assert.That(guest["disconnect_frame"].Type, Is.EqualTo(JTokenType.Null));

			var bob = json["players"][1];
			Assert.That(bob["fingerprint"].Type, Is.EqualTo(JTokenType.Null));
			Assert.That(bob["outcome_at"].Value<string>(), Is.EqualTo("2026-09-07T14:10:00Z"));
			Assert.That(bob["disconnect_frame"].Value<int>(), Is.EqualTo(4200));
		}

		[TestCase(TestName = "Slots follow the player list and profiles follow the client index")]
		public void SlotOrder()
		{
			var gameInfo = MakeGameInfo("2026-09-07T14:01:02Z",
				MakePlayer(5, "first", AliceFingerprint),
				MakePlayer(2, "second", BobFingerprint),
				MakePlayer(9, "bot", null));
			gameInfo.Players[2].IsHuman = false;
			gameInfo.Players[2].IsBot = true;

			var profiles = new Dictionary<int, int> { { 2, 222 }, { 5, 555 } };
			var players = OutcomeEventBuilder.Build(MakeOutcome(GameOutcomeReason.EndGame, gameInfo, "2026-09-07T14:02:02Z", profiles: profiles),
				"8d3f1c2a-1b2c-4d5e-8f90-0a1b2c3d4e5f").Players;

			Assert.That(players.ConvertAll(p => p.Slot), Is.EqualTo(new[] { 0, 1, 2 }));
			Assert.That(players.ConvertAll(p => p.Name), Is.EqualTo(new[] { "first", "second", "bot" }));
			Assert.That(players.ConvertAll(p => p.ProfileId), Is.EqualTo(new int?[] { 555, 222, null }));
			Assert.That(players[2].IsBot, Is.True);
		}

		[TestCase("2026-09-07T14:00:00Z", "2026-09-07T14:00:01.999Z", 1, TestName = "Duration floors partial seconds")]
		[TestCase("2026-09-07T14:00:00Z", "2026-09-07T14:22:38Z", 1358, TestName = "Duration counts whole seconds")]
		[TestCase("2026-09-07T14:00:05Z", "2026-09-07T14:00:00Z", 0, TestName = "Duration never goes negative")]
		public void Duration(string startedAt, string finalizedAt, int expected)
		{
			Assert.That(OutcomeEventBuilder.DurationSeconds(Utc(startedAt), Utc(finalizedAt)), Is.EqualTo(expected));
		}

		[TestCase(TestName = "Player names with backslashes, quotes and non-ASCII round-trip")]
		public void Escaping()
		{
			const string Name = "a\\b \"c\" Ünïcødé ✓";
			var gameInfo = MakeGameInfo("2026-09-07T14:01:02Z", MakePlayer(0, Name, AliceFingerprint), MakePlayer(1, "bob", BobFingerprint));
			var json = BuildJson(MakeOutcome(GameOutcomeReason.EndGame, gameInfo, "2026-09-07T14:02:02Z"));

			Assert.That(Parse(json)["players"][0]["name"].Value<string>(), Is.EqualTo(Name));
		}

		[TestCase(TestName = "Outcome file is written once and never replaced")]
		public void WriteOnce()
		{
			var directory = Path.Combine(Path.GetTempPath(), "openra-outcome-" + Guid.NewGuid().ToString("N"));
			const string MatchId = "8d3f1c2a-1b2c-4d5e-8f90-0a1b2c3d4e5f";
			try
			{
				Assert.That(OutcomeEventWriter.TryWrite(directory, MatchId, "{\"first\":true}"), Is.True);

				var path = OutcomeEventWriter.OutcomeFilePath(directory, MatchId);
				var expected = Encoding.UTF8.GetBytes("{\"first\":true}\n");
				Assert.That(File.ReadAllBytes(path), Is.EqualTo(expected));

				Assert.That(OutcomeEventWriter.TryWrite(directory, MatchId, "{\"first\":false}"), Is.False);
				Assert.That(File.ReadAllBytes(path), Is.EqualTo(expected));
				Assert.That(Directory.GetFiles(directory), Is.EqualTo(new[] { path }));
			}
			finally
			{
				if (Directory.Exists(directory))
					Directory.Delete(directory, true);
			}
		}

		[TestCase(TestName = "Two-argument File.Move refuses to replace an existing file")]
		public void MoveDoesNotOverwrite()
		{
			var directory = Path.Combine(Path.GetTempPath(), "openra-outcome-" + Guid.NewGuid().ToString("N"));
			Directory.CreateDirectory(directory);
			try
			{
				var source = Path.Combine(directory, "source");
				var target = Path.Combine(directory, "target");
				File.WriteAllText(source, "new");
				File.WriteAllText(target, "old");

				Assert.Throws<IOException>(() => File.Move(source, target));
				Assert.That(File.ReadAllText(target), Is.EqualTo("old"));
			}
			finally
			{
				Directory.Delete(directory, true);
			}
		}
	}
}
