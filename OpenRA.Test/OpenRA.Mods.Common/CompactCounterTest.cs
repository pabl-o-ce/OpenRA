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
using OpenRA.Mods.Common.Widgets.Logic;

namespace OpenRA.Test
{
	[TestFixture]
	public class CompactCounterTest
	{
		[TestCase(5000, "5000")]
		[TestCase(10000, "10k")]
		[TestCase(999999, "999k")]
		[TestCase(1000000, "1M")]
		[TestCase(-12345, "-12.3k")]
		[TestCase(int.MaxValue, "2147M")]
		[TestCase(int.MinValue, "-2147M")]
		public void LargeValuesFitWithoutIntegerOverflow(int value, string expected)
		{
			Assert.That(IngameCashCounterLogic.CompactValue(value), Is.EqualTo(expected));
		}
	}
}
