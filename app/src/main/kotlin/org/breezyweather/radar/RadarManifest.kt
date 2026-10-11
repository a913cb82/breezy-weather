/*
 * This file is part of Breezy Weather.
 *
 * Breezy Weather is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by the
 * Free Software Foundation, version 3 of the License.
 *
 * Breezy Weather is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
 * License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with Breezy Weather. If not, see <https://www.gnu.org/licenses/>.
 */

package org.breezyweather.radar

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * Subset of the tile pipeline manifest.json needed by the app.
 * Full contract: plan/ARCHITECTURE.md (LUT entries are {min_mm_h, color}).
 */
@Serializable
data class RadarLutStop(
    @SerialName("min_mm_h") val minMmH: Double,
    val color: List<Int>,
)

@Serializable
data class RadarFrame(
    val t: String,
    val kind: String, // "obs" | "model"
    val run: String,
    val tiles: String, // "<url>/{z}/{x}/{y}.png"
)

@Serializable
data class RadarManifest(
    val generated: String, // "%Y-%m-%dT%H:%M:%SZ"
    @SerialName("now_index") val nowIndex: Int,
    val lut: List<RadarLutStop> = emptyList(),
    val frames: List<RadarFrame> = emptyList(),
    val snapshot: String = "",
    val coverage: String = "",
) {
    /** Frame closest to "now" (latest obs), or null when empty. */
    val nowFrame: RadarFrame?
        get() = frames.getOrNull(nowIndex)

    fun isObs(frame: RadarFrame) = frame.kind == "obs"
}
