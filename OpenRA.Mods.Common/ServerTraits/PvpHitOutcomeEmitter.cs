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
using System.IO;
using OpenRA.Server;

namespace OpenRA.Mods.Common.Server
{
	/// <summary>
	/// Reports the PvPHit match outcome as `&lt;SupportDir&gt;/pvphit/outcome-&lt;match&gt;.json` plus one
	/// `pvphit-outcome: &lt;json&gt;` STDOUT line. The first outcome of a match wins: the dedicated server
	/// builds a new Server (and a new trait instance) per game while PVPHIT_MATCH_ID stays the same,
	/// so the file on disk, not instance state, decides whether an outcome was already reported.
	/// </summary>
	public class PvpHitOutcomeEmitter : ServerTrait, INotifyServerStart, INotifyGameOutcome
	{
		public const string MatchIdVariable = "PVPHIT_MATCH_ID";
		public const string StdoutPrefix = "pvphit-outcome: ";

		readonly string matchId;
		readonly string directory;

		public PvpHitOutcomeEmitter()
		{
			if (Guid.TryParse(Environment.GetEnvironmentVariable(MatchIdVariable), out var id))
				matchId = id.ToString("D");

			directory = Path.Combine(Platform.SupportDir, "pvphit");
		}

		void INotifyServerStart.ServerStarted(OpenRA.Server.Server server)
		{
			// Printed so a missing Engine.SupportDir (outcomes silently landing in the default support dir) is obvious
			var message = matchId != null
				? $"PvPHit outcome emitter: match {matchId}, writing to {directory}"
				: $"PvPHit outcome emitter disabled: {MatchIdVariable} is not set to a UUID";

			Log.Write("server", message);
			Console.WriteLine(message);
		}

		void INotifyGameOutcome.GameOutcomeDetermined(OpenRA.Server.Server server, GameOutcome outcome)
		{
			if (matchId == null)
				return;

			var outcomeEvent = OutcomeEventBuilder.Build(outcome, matchId);
			var json = OutcomeEventBuilder.Serialize(outcomeEvent);
			if (!OutcomeEventWriter.TryWrite(directory, matchId, json))
			{
				// Never echo again: a second STDOUT line could become a second delivery
				Log.Write("server", $"PvPHit outcome for match {matchId} was already reported; ignoring {outcomeEvent.State}/{outcomeEvent.Reason}");
				return;
			}

			Log.Write("server", $"PvPHit outcome for match {matchId}: {outcomeEvent.State}/{outcomeEvent.Reason}");
			Console.WriteLine(StdoutPrefix + json);
		}
	}
}
