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

package org.breezyweather.ui.main.adapters.main.holder

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import breezyweather.domain.location.model.Location
import org.breezyweather.R
import org.breezyweather.common.activities.BreezyActivity
import org.breezyweather.radar.RadarManifest
import org.breezyweather.radar.RadarRepository
import org.breezyweather.ui.theme.resource.providers.ResourceProvider
import java.time.Duration
import java.time.Instant

class RadarViewHolder(parent: ViewGroup) : AbstractMainCardViewHolder(
    LayoutInflater.from(parent.context).inflate(R.layout.container_main_radar, parent, false)
) {
    private val snapshotView: ImageView = itemView.findViewById(R.id.radar_snapshot)
    private val subtitleView: TextView = itemView.findViewById(R.id.radar_subtitle)

    override fun onBindView(
        activity: BreezyActivity,
        location: Location,
        provider: ResourceProvider,
        listAnimationEnabled: Boolean,
        itemAnimationEnabled: Boolean,
    ) {
        super.onBindView(activity, location, provider, listAnimationEnabled, itemAnimationEnabled)

        val token = Any()
        itemView.setTag(R.id.container_main_radar, token)
        subtitleView.text = ""
        snapshotView.setImageDrawable(null)
        itemView.contentDescription = context.getString(R.string.radar)

        RadarRepository.fetchManifest { manifest ->
            if (itemView.getTag(R.id.container_main_radar) !== token) return@fetchManifest
            if (manifest == null || manifest.snapshot.isEmpty()) {
                // Pipeline unreachable: graceful degraded state, card stays.
                itemView.post {
                    if (itemView.getTag(R.id.container_main_radar) !== token) return@post
                    subtitleView.text = context.getString(R.string.radar_unavailable)
                    snapshotView.visibility = View.GONE
                }
                return@fetchManifest
            }
            RadarRepository.downloadBitmap(manifest.snapshot) { bitmap ->
                itemView.post {
                    if (itemView.getTag(R.id.container_main_radar) !== token) return@post
                    if (bitmap != null) {
                        snapshotView.setImageBitmap(bitmap)
                        snapshotView.visibility = View.VISIBLE
                    } else {
                        snapshotView.visibility = View.GONE
                    }
                    subtitleView.text = freshnessText(manifest)
                    itemView.contentDescription =
                        "${context.getString(R.string.radar)}: ${subtitleView.text}"
                }
            }
        }
    }

    private fun freshnessText(manifest: RadarManifest): String {
        val minutes = runCatching {
            Duration.between(Instant.parse(manifest.generated), Instant.now()).toMinutes()
        }.getOrDefault(-1)
        return when {
            minutes < 0 -> context.getString(R.string.radar_unavailable)
            minutes < 1 -> context.getString(R.string.radar_updated_just_now)
            else -> context.getString(R.string.radar_updated_minutes_ago, minutes)
        }
    }
}
