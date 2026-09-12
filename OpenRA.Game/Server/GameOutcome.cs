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

namespace OpenRA.Server
{
	public enum GameOutcomeReason
	{
		/// <summary>Every win state became defined while the game was running.</summary>
		Result,

		/// <summary>The game ended because the server closed it (usually after the last player left).</summary>
		EndGame,

		/// <summary>The clients disagreed on the game state and the game was aborted.</summary>
		OutOfSync,

		/// <summary>The server thread is shutting down.</summary>
		Shutdown
	}

	/// <summary>What the server knows about a game's outcome when an <see cref="INotifyGameOutcome"/> notification fires.</summary>
	public sealed class GameOutcome
	{
		public readonly GameOutcomeReason Reason;

		/// <summary>The live game information. Its players are the playable players, in world player order.</summary>
		public readonly GameInformation GameInfo;

		/// <summary>File name of the server replay, or null when the server is not recording one.</summary>
		public readonly string ReplayFilename;

		public readonly DateTime FinalizedUtc;

		/// <summary>Profile IDs of the clients that authenticated against the player database, by client index.</summary>
		public readonly IReadOnlyDictionary<int, int> ProfileIdsByClientIndex;

		public readonly string EngineVersion;

		public GameOutcome(GameOutcomeReason reason, GameInformation gameInfo, string replayFilename, DateTime finalizedUtc,
			IReadOnlyDictionary<int, int> profileIdsByClientIndex, string engineVersion)
		{
			Reason = reason;
			GameInfo = gameInfo;
			ReplayFilename = replayFilename;
			FinalizedUtc = finalizedUtc;
			ProfileIdsByClientIndex = profileIdsByClientIndex;
			EngineVersion = engineVersion;
		}
	}
}
