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
import android.graphics.BitmapFactory
import kotlinx.serialization.json.Json
import okhttp3.Call
import okhttp3.Callback
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import java.io.IOException

/**
 * Fetches the radar manifest + snapshot bitmap. Plain OkHttp callbacks
 * (no new dependencies); callers must check the view is still bound.
 */
object RadarRepository {

    private val client = OkHttpClient()
    private val json = Json { ignoreUnknownKeys = true }

    fun fetchManifest(callback: (RadarManifest?) -> Unit) {
        client.newCall(Request.Builder().url(RadarConfig.MANIFEST_URL).build())
            .enqueue(object : Callback {
                override fun onFailure(call: Call, e: IOException) {
                    callback(null)
                }

                override fun onResponse(call: Call, response: Response) {
                    callback(
                        response.use {
                            if (!it.isSuccessful) {
                                null
                            } else {
                                runCatching {
                                    json.decodeFromString<RadarManifest>(
                                        it.body!!.string()
                                    )
                                }.getOrNull()
                            }
                        }
                    )
                }
            })
    }

    fun downloadBitmap(url: String, callback: (Bitmap?) -> Unit) {
        client.newCall(Request.Builder().url(url).build())
            .enqueue(object : Callback {
                override fun onFailure(call: Call, e: IOException) {
                    callback(null)
                }

                override fun onResponse(call: Call, response: Response) {
                    callback(
                        response.use {
                            if (!it.isSuccessful) {
                                null
                            } else {
                                runCatching {
                                    BitmapFactory.decodeStream(it.body!!.byteStream())
                                }.getOrNull()
                            }
                        }
                    )
                }
            })
    }
}
