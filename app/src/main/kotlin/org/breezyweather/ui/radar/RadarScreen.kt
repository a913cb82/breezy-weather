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

package org.breezyweather.ui.radar

import android.graphics.Bitmap
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Slider
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import org.breezyweather.R
import org.breezyweather.radar.RadarConfig
import org.breezyweather.radar.RadarFrame
import org.breezyweather.radar.RadarLut
import org.breezyweather.radar.RadarManifest
import org.breezyweather.radar.RadarRepository
import org.maplibre.compose.camera.CameraPosition
import org.maplibre.compose.camera.rememberCameraState
import org.maplibre.compose.expressions.dsl.const
import org.maplibre.compose.layers.RasterLayer
import org.maplibre.compose.map.MapOptions
import org.maplibre.compose.map.MaplibreMap
import org.maplibre.compose.map.OrnamentOptions
import org.maplibre.compose.sources.RasterSource
import org.maplibre.compose.sources.TileSetOptions
import org.maplibre.compose.util.ClickResult
import org.maplibre.spatialk.geojson.Position

/**
 * Scrubbable radar detail screen: MapLibre map (OFM basemap, day/night)
 * + one raster layer per frame (active frame opaque, rest hidden —
 * RoadTripRadar pattern, MIT) + manual scrub bar + tap-for-value readout.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RadarScreen(
    onBackPressed: () -> Unit,
) {
    var manifest by remember { mutableStateOf<RadarManifest?>(null) }
    var failed by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        RadarRepository.fetchManifest { m ->
            manifest = m
            failed = m == null
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(stringResource(R.string.radar)) },
                navigationIcon = {
                    IconButton(onClick = onBackPressed) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = null)
                    }
                }
            )
        }
    ) { padding ->
        val m = manifest
        when {
            m == null && !failed -> Box(
                modifier = Modifier.fillMaxSize().padding(padding),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
            m == null -> Box(
                modifier = Modifier.fillMaxSize().padding(padding),
                contentAlignment = Alignment.Center
            ) {
                Text(stringResource(R.string.radar_unavailable))
            }
            m.frames.isEmpty() -> Box(
                modifier = Modifier.fillMaxSize().padding(padding),
                contentAlignment = Alignment.Center
            ) {
                Text(stringResource(R.string.radar_unavailable))
            }
            else -> RadarMap(
                manifest = m,
                modifier = Modifier.fillMaxSize().padding(padding)
            )
        }
    }
}

@Composable
private fun RadarMap(
    manifest: RadarManifest,
    modifier: Modifier = Modifier,
) {
    val dark = isSystemInDarkTheme()
    val cameraState = rememberCameraState(
        firstPosition = CameraPosition(
            target = Position(-2.5, 54.2),
            zoom = 5.0
        )
    )
    var frameIndex by remember(manifest) {
        mutableIntStateOf(manifest.nowIndex.coerceIn(0, manifest.frames.lastIndex))
    }
    val frame: RadarFrame = manifest.frames[frameIndex]
    var readout by remember { mutableStateOf<String?>(null) }
    // Small tile cache for tap-for-value (z7 tiles, ~50KB each).
    val tileCache = remember { mutableMapOf<String, Bitmap>() }

    RadarDetailContent(
        manifest = manifest,
        frame = frame,
        frameIndex = frameIndex,
        onFrameChange = { frameIndex = it },
        readout = readout,
        modifier = modifier,
        mapContent = {
            MaplibreMap(
                baseStyle = org.maplibre.compose.style.BaseStyle.Uri(
                    if (dark) RadarConfig.STYLE_NIGHT else RadarConfig.STYLE_DAY
                ),
                cameraState = cameraState,
                modifier = Modifier.fillMaxSize(),
                options = MapOptions(
                    ornamentOptions = OrnamentOptions(
                        isScaleBarEnabled = false,
                        isCompassEnabled = false
                    )
                ),
                onMapClick = { position, _ ->
                    probeTap(
                        position = position,
                        frame = frame,
                        lut = manifest.lut,
                        tileCache = tileCache
                    ) { readout = it }
                    ClickResult.Pass
                },
                onMapLongClick = { _, _ -> ClickResult.Pass }
            ) {
                manifest.frames.forEachIndexed { index, f ->
                    key(f.t) {
                        val source = remember {
                            RasterSource(
                                id = "radar-src-$index",
                                tiles = listOf(f.tiles),
                                options = TileSetOptions(maxZoom = RadarConfig.MAX_TILE_ZOOM),
                                tileSize = 256
                            )
                        }
                        RasterLayer(
                            id = "radar-lyr-$index",
                            source = source,
                            visible = index == frameIndex,
                            opacity = const(if (index == frameIndex) 0.85f else 0f)
                        )
                    }
                }
            }
        }
    )
}

/**
 * Map chrome (scrub bar, labels, readout) with a swappable map slot —
 * production passes the live MapLibre map, JVM screenshots pass a stand-in.
 */
@Composable
internal fun RadarDetailContent(
    manifest: RadarManifest,
    frame: RadarFrame,
    frameIndex: Int,
    onFrameChange: (Int) -> Unit,
    readout: String?,
    modifier: Modifier = Modifier,
    mapContent: @Composable () -> Unit,
) {
    Column(modifier = modifier) {
        Box(modifier = Modifier.fillMaxWidth().weight(1f)) {
            mapContent()
        }
        Column(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp)) {
            Text(
                text = frameLabel(frame, frameIndex == manifest.nowIndex),
                style = MaterialTheme.typography.titleMedium
            )
            Slider(
                value = frameIndex.toFloat(),
                onValueChange = { onFrameChange(it.toInt()) },
                valueRange = 0f..manifest.frames.lastIndex.toFloat(),
                steps = (manifest.frames.size - 2).coerceAtLeast(0),
                modifier = Modifier.fillMaxWidth()
            )
            Text(
                text = readout ?: "",
                style = MaterialTheme.typography.bodyMedium,
                minLines = 1
            )
        }
    }
}

private fun frameLabel(frame: RadarFrame, isNow: Boolean): String {
    // "t" is "%Y-%m-%dT%H:%M:%SZ" → show "dd MMM HH:mm".
    val date = frame.t.substring(0, 10)
    val time = frame.t.substring(11, 16)
    val badge = if (frame.kind == "obs") "obs" else "model"
    return if (isNow) "$date $time · $badge · now" else "$date $time · $badge"
}

/** Sample the z7 tile under the tap and invert the pixel into a band readout. */
private fun probeTap(
    position: Position,
    frame: RadarFrame,
    lut: List<org.breezyweather.radar.RadarLutStop>,
    tileCache: MutableMap<String, Bitmap>,
    done: (String?) -> Unit,
) {
    val ref = RadarLut.tileFor(position.longitude, position.latitude, RadarConfig.MAX_TILE_ZOOM)
    val cached = tileCache[ref.key()]
    if (cached != null) {
        done(RadarLut.readout(cached, ref, lut)?.let { "$it · ${frame.kind}" })
        return
    }
    val url = frame.tiles
        .replace("{z}", ref.z.toString())
        .replace("{x}", ref.x.toString())
        .replace("{y}", ref.y.toString())
    RadarRepository.downloadBitmap(url) { bitmap ->
        if (bitmap != null) {
            if (tileCache.size >= 24) tileCache.clear()
            tileCache[ref.key()] = bitmap
        }
        done(RadarLut.readout(bitmap, ref, lut)?.let { "$it · ${frame.kind}" })
    }
}
