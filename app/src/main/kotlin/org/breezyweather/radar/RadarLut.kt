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

import android.graphics.Bitmap
import kotlin.math.floor

/**
 * Pure-Kotlin radar helpers (no Android imports): tile math + LUT inversion
 * for the tap-for-value readout. Tile pixels are exact LUT entries
 * (verified PC-side), so inversion is an exact color match; anything else
 * (transparent, edge-resampled) degrades honestly to no-rain/trace.
 */
object RadarLut {

    /** Slippy-map tile + in-tile pixel for lon/lat at zoom [z] (clamped). */
    fun tileFor(lon: Double, lat: Double, z: Int): TileRef {
        val n = 1 shl z
        val x = floor((lon + 180.0) / 360.0 * n).toInt().coerceIn(0, n - 1)
        val latRad = Math.toRadians(lat.coerceIn(-85.05112878, 85.05112878))
        val y = floor(
            (1.0 - Math.log(Math.tan(latRad) + 1.0 / Math.cos(latRad)) / Math.PI) / 2.0 * n
        ).toInt().coerceIn(0, n - 1)
        val px = (((lon + 180.0) / 360.0 * n - x) * 256).toInt().coerceIn(0, 255)
        val yFrac = (1.0 - Math.log(Math.tan(latRad) + 1.0 / Math.cos(latRad)) / Math.PI) / 2.0 * n
        val py = ((yFrac - y) * 256).toInt().coerceIn(0, 255)
        return TileRef(z, x, y, px, py)
    }

    /** Band label for a tile pixel, or null when dry/unknown. */
    fun bandLabel(pixel: Int, lut: List<RadarLutStop>): String? {
        val alpha = pixel ushr 24
        if (alpha == 0) return null
        val rgb = listOf((pixel shr 16) and 0xFF, (pixel shr 8) and 0xFF, pixel and 0xFF)
        val idx = lut.indexOfFirst { it.color == rgb }
        if (idx < 0) return null
        val lo = lut[idx].minMmH
        return if (idx == lut.lastIndex) {
            "≥${fmt(lo)} mm/h"
        } else {
            "${fmt(lo)}–${fmt(lut[idx + 1].minMmH)} mm/h"
        }
    }

    /** Readout line for a tap, or null when nothing to report. */
    fun readout(bitmap: Bitmap?, ref: TileRef, lut: List<RadarLutStop>): String? {
        if (bitmap == null) return null
        if (ref.px >= bitmap.width || ref.py >= bitmap.height) return null
        return bandLabel(bitmap.getPixel(ref.px, ref.py), lut)
    }

    private fun fmt(v: Double): String = if (v == floor(v)) v.toInt().toString() else v.toString()

    data class TileRef(val z: Int, val x: Int, val y: Int, val px: Int, val py: Int) {
        fun key() = "$z/$x/$y"
    }
}
