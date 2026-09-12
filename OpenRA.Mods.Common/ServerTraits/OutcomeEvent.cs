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
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using Newtonsoft.Json;
using OpenRA.Server;

namespace OpenRA.Mods.Common.Server
{
	/// <summary>The PvPHit `openra.outcome` event, contract_version 1 (pvphit docs/openra/results.md).</summary>
	public class OutcomeEvent
	{
		[JsonProperty("schema_version", Order = 0)]
		public int SchemaVersion = OutcomeEventBuilder.SchemaVersion;

		[JsonProperty("event", Order = 1)]
		public string Event = OutcomeEventBuilder.EventName;

		[JsonProperty("event_id", Order = 2)]
		public string EventId;

		[JsonProperty("match_id", Order = 3)]
		public string MatchId;

		[JsonProperty("state", Order = 4)]
		public string State;

		[JsonProperty("reason", Order = 5)]
		public string Reason;

		[JsonProperty("engine_version", Order = 6)]
		public string EngineVersion;

		[JsonProperty("mod_id", Order = 7)]
		public string ModId;

		[JsonProperty("mod_version", Order = 8)]
		public string ModVersion;

		[JsonProperty("map", Order = 9)]
		public string Map;

		[JsonProperty("replay", Order = 10)]
		public string Replay;

		[JsonProperty("started_at", Order = 11)]
		public string StartedAt;

		[JsonProperty("finalized_at", Order = 12)]
		public string FinalizedAt;

		[JsonProperty("duration_seconds", Order = 13)]
		public int DurationSeconds;

		[JsonProperty("players", Order = 14)]
		public List<OutcomeEventPlayer> Players = new();
	}

	public class OutcomeEventPlayer
	{
		[JsonProperty("slot", Order = 0)]
		public int Slot;

		[JsonProperty("name", Order = 1)]
		public string Name;

		[JsonProperty("is_bot", Order = 2)]
		public bool IsBot;

		[JsonProperty("fingerprint", Order = 3)]
		public string Fingerprint;

		[JsonProperty("profile_id", Order = 4)]
		public int? ProfileId;

		[JsonProperty("outcome", Order = 5)]
		public string Outcome;

		[JsonProperty("outcome_at", Order = 6)]
		public string OutcomeAt;

		[JsonProperty("disconnect_frame", Order = 7)]
		public int? DisconnectFrame;
	}

	public static class OutcomeEventBuilder
	{
		public const int SchemaVersion = 1;
		public const string EventName = "openra.outcome";

		/// <summary>RFC 4122 namespace for the name-based (version 5) event_id.</summary>
		public const string EventIdNamespace = "fe305223-7ee0-4081-844f-0b01f57c3dc5";

		/// <summary>Prefixed to the lowercase match_id to form the version 5 name.</summary>
		public const string EventIdNamePrefix = "pvphit:openra.outcome:";

		static readonly JsonSerializerSettings SerializerSettings = new()
		{
			Formatting = Formatting.None,
			NullValueHandling = NullValueHandling.Include,
			Culture = CultureInfo.InvariantCulture,
		};

		public static OutcomeEvent Build(GameOutcome outcome, string matchId)
		{
			var gameInfo = outcome.GameInfo;

			// Slots index the playable players; spectators are never part of GameInformation.Players
			var players = gameInfo.Players.Select((p, slot) => new OutcomeEventPlayer
			{
				Slot = slot,
				Name = p.Name,
				IsBot = p.IsBot,
				Fingerprint = string.IsNullOrEmpty(p.Fingerprint) ? null : p.Fingerprint,
				ProfileId = outcome.ProfileIdsByClientIndex.TryGetValue(p.ClientIndex, out var profileId) ? profileId : null,
				Outcome = p.Outcome.ToString(),
				OutcomeAt = p.Outcome == WinState.Undefined ? null : FormatUtc(p.OutcomeTimestampUtc),
				DisconnectFrame = p.DisconnectFrame == 0 ? null : p.DisconnectFrame,
			}).ToList();

			return new OutcomeEvent
			{
				EventId = DeriveEventId(matchId),
				MatchId = matchId,
				State = StateName(outcome),
				Reason = ReasonName(outcome.Reason),
				EngineVersion = outcome.EngineVersion,
				ModId = gameInfo.Mod,
				ModVersion = gameInfo.Version,
				Map = gameInfo.MapUid,
				Replay = outcome.ReplayFilename,
				StartedAt = FormatUtc(gameInfo.StartTimeUtc),
				FinalizedAt = FormatUtc(outcome.FinalizedUtc),
				DurationSeconds = DurationSeconds(gameInfo.StartTimeUtc, outcome.FinalizedUtc),
				Players = players,
			};
		}

		/// <summary>Single-line JSON with explicit nulls and timestamps pre-formatted as strings.</summary>
		public static string Serialize(OutcomeEvent outcomeEvent)
		{
			return JsonConvert.SerializeObject(outcomeEvent, SerializerSettings);
		}

		public static string StateName(GameOutcome outcome)
		{
			switch (outcome.Reason)
			{
				// A desynced game is never a settlement source, even if every outcome is defined
				case GameOutcomeReason.OutOfSync:
					return "desync";
				case GameOutcomeReason.Result:
					return "final";
				default:
					return outcome.GameInfo.Players.Any(p => p.Outcome == WinState.Undefined) ? "unresolved" : "final";
			}
		}

		public static string ReasonName(GameOutcomeReason reason)
		{
			switch (reason)
			{
				case GameOutcomeReason.Result:
					return "result";
				case GameOutcomeReason.EndGame:
					return "end_game";
				case GameOutcomeReason.OutOfSync:
					return "out_of_sync";
				case GameOutcomeReason.Shutdown:
					return "shutdown";
				default:
					throw new ArgumentOutOfRangeException(nameof(reason), reason, null);
			}
		}

		public static string FormatUtc(DateTime value)
		{
			return value.ToString("yyyy-MM-dd'T'HH:mm:ss'Z'", CultureInfo.InvariantCulture);
		}

		public static int DurationSeconds(DateTime startedUtc, DateTime finalizedUtc)
		{
			return (int)Math.Max(0, Math.Floor((finalizedUtc - startedUtc).TotalSeconds));
		}

		/// <summary>RFC 4122 version 5 UUID of <see cref="EventIdNamePrefix"/> + matchId in <see cref="EventIdNamespace"/>.</summary>
		public static string DeriveEventId(string matchId)
		{
			var namespaceBytes = ParseUuid(EventIdNamespace);
			var nameBytes = Encoding.UTF8.GetBytes(EventIdNamePrefix + matchId);
			var data = new byte[namespaceBytes.Length + nameBytes.Length];
			Buffer.BlockCopy(namespaceBytes, 0, data, 0, namespaceBytes.Length);
			Buffer.BlockCopy(nameBytes, 0, data, namespaceBytes.Length, nameBytes.Length);

			byte[] hash;
			using (var sha1 = SHA1.Create())
				hash = sha1.ComputeHash(data);

			hash[6] = (byte)((hash[6] & 0x0F) | 0x50);
			hash[8] = (byte)((hash[8] & 0x3F) | 0x80);

			// Network byte order, unlike Guid.ToByteArray
			var hex = string.Concat(hash.Take(16).Select(b => b.ToString("x2", CultureInfo.InvariantCulture)));
			return $"{hex[..8]}-{hex[8..12]}-{hex[12..16]}-{hex[16..20]}-{hex[20..]}";
		}

		static byte[] ParseUuid(string uuid)
		{
			var hex = uuid.Replace("-", "");
			var bytes = new byte[16];
			for (var i = 0; i < bytes.Length; i++)
				bytes[i] = Convert.ToByte(hex.Substring(2 * i, 2), 16);

			return bytes;
		}
	}

	public static class OutcomeEventWriter
	{
		public static string OutcomeFilePath(string directory, string matchId)
		{
			return Path.Combine(directory, $"outcome-{matchId}.json");
		}

		/// <summary>
		/// Writes the outcome file for a match exactly once: UTF-8 without a BOM, one trailing newline,
		/// written to a temporary file and renamed into place. Returns false and leaves the existing file
		/// untouched when the match already has an outcome file.
		/// </summary>
		public static bool TryWrite(string directory, string matchId, string json)
		{
			var target = OutcomeFilePath(directory, matchId);
			if (File.Exists(target))
				return false;

			Directory.CreateDirectory(directory);
			var temp = target + ".tmp";
			var bytes = new UTF8Encoding(false).GetBytes(json + "\n");
			using (var stream = new FileStream(temp, FileMode.Create, FileAccess.Write, FileShare.None))
			{
				stream.Write(bytes, 0, bytes.Length);
				stream.Flush(true);
			}

			try
			{
				// The two-argument File.Move never overwrites: losing a race means the other write stands
				File.Move(temp, target);
			}
			catch (IOException) when (File.Exists(target))
			{
				File.Delete(temp);
				return false;
			}

			return true;
		}
	}
}
