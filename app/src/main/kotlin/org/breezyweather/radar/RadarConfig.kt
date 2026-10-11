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

/** Personal tile backend (GitHub Pages, see .github/workflows/tiles-deploy.yml). */
object RadarConfig {
    const val BASE_URL = "https://a913cb82.github.io/breezy-weather/tiles"
    const val MANIFEST_URL = "$BASE_URL/manifest.json"

    // Keyless OpenFreeMap basemaps (plan deviation: official dark style
    // instead of self-hosted darkened positron — maintained, same source).
    const val STYLE_DAY = "https://tiles.openfreemap.org/styles/positron"
    const val STYLE_NIGHT = "https://tiles.openfreemap.org/styles/dark"

    /** Finest tile zoom the pipeline renders; the SDK overzooms beyond it. */
    const val MAX_TILE_ZOOM = 7

    /** Country codes with radar coverage (Met Office UK composite). */
    val COVERED_COUNTRIES = arrayOf("GB", "GG", "IM", "JE")
}
