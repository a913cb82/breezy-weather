package org.breezyweather.radar

import android.graphics.BitmapFactory
import android.view.LayoutInflater
import android.widget.ImageView
import android.widget.TextView
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import com.github.takahirom.roborazzi.captureRoboImage
import org.breezyweather.R
import org.breezyweather.ui.radar.RadarDetailContent
import org.breezyweather.ui.radar.RadarLoadingContent
import org.breezyweather.ui.radar.RadarUnavailableContent
import org.breezyweather.ui.theme.compose.BreezyWeatherTheme
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode
import java.io.File

/**
 * JVM screenshots (Roborazzi, no device): the radar card inflated on a
 * home-screen-style background, and the detail chrome with a stand-in
 * for the GL map (MapLibre cannot render on JVM).
 *
 * Stand-ins composite the real live snapshot over an Esri light/dark-gray
 * reference basemap (test fixtures only — production renders OFM vector
 * tiles; basemap (c) Esri, TomTom, Garmin, FAO, NOAA, USGS,
 * (c) OpenStreetMap contributors).
 */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w1080dp-h2400dp-420dpi")
class RadarScreenshotTest {

    private fun fixtureBitmap(name: String) =
        BitmapFactory.decodeStream(File("src/test/resources/$name.png").inputStream())

    private fun fakeManifest() = RadarManifest(
        generated = "2026-10-11T11:10:10Z",
        nowIndex = 1,
        lut = listOf(
            RadarLutStop(0.1, listOf(168, 230, 240)),
            RadarLutStop(0.5, listOf(120, 200, 250)),
            RadarLutStop(1.0, listOf(60, 140, 250)),
            RadarLutStop(16.0, listOf(255, 60, 60))
        ),
        frames = listOf(
            RadarFrame("2026-10-11T10:45:00Z", "obs", "-", "https://x/obs/{z}/{x}/{y}.png"),
            RadarFrame("2026-10-11T11:00:00Z", "obs", "-", "https://x/obs/{z}/{x}/{y}.png"),
            RadarFrame("2026-10-11T11:15:00Z", "model", "20261011T0600Z", "https://x/model/{z}/{x}/{y}.png")
        ),
        snapshot = "https://x/snapshot.png",
        coverage = "https://x/mask/{z}/{x}/{y}.png"
    )

    @Test
    @Config(qualifiers = "w1080dp-h800dp-420dpi")
    fun radarCard() {
        captureCard("Updated 10 min ago", art = "radar-map-day", background = 0xFFC9E8F7.toInt())
    }

    @Test
    @Config(qualifiers = "w1080dp-h800dp-420dpi")
    fun radarCardUnavailable() {
        captureCard("Radar unavailable", art = null, background = 0xFFC9E8F7.toInt())
    }

    @Test
    @Config(qualifiers = "w1080dp-h800dp-night-420dpi")
    fun radarCardNight() {
        captureCard("Updated 10 min ago", art = "radar-map-night", background = 0xFF0E141B.toInt())
    }

    // Card hosted the way the home list shows it: wallpaper-tinted
    // background, 16dp list margins.
    private fun captureCard(subtitle: String, art: String?, background: Int) {
        androidx.test.core.app.ActivityScenario.launch(ScreenshotActivity::class.java)
            .use { scenario ->
                scenario.onActivity { activity ->
                    val card = LayoutInflater.from(activity)
                        .inflate(R.layout.container_main_radar, null)
                    val artView = card.findViewById<ImageView>(R.id.radar_snapshot)
                    if (art != null) {
                        artView.setImageBitmap(fixtureBitmap(art))
                    } else {
                        artView.visibility = android.view.View.GONE
                    }
                    card.findViewById<TextView>(R.id.radar_subtitle).text = subtitle
                    val pad = (16 * activity.resources.displayMetrics.density).toInt()
                    val host = android.widget.FrameLayout(activity).apply {
                        setBackgroundColor(background)
                        setPadding(pad, pad, pad, pad)
                        addView(
                            card,
                            android.widget.FrameLayout.LayoutParams(
                                android.widget.FrameLayout.LayoutParams.MATCH_PARENT,
                                android.widget.FrameLayout.LayoutParams.WRAP_CONTENT
                            )
                        )
                    }
                    activity.setContentView(host)
                }
                androidx.test.espresso.Espresso.onView(
                    androidx.test.espresso.matcher.ViewMatchers.isRoot()
                ).captureRoboImage()
            }
    }

    @Test
    fun radarDetail() {
        // Basemap + live-snapshot composite stand-in for the GL map.
        val bitmap = fixtureBitmap("radar-map-day").asImageBitmap()
        val manifest = fakeManifest()
        captureRoboImage {
            BreezyWeatherTheme {
                DetailShell { padding ->
                    RadarDetailContent(
                        manifest = manifest,
                        frame = manifest.frames[1],
                        frameIndex = 1,
                        onFrameChange = {},
                        readout = "1.0–2.0 mm/h · obs",
                        modifier = Modifier.padding(padding),
                        mapContent = {
                            Image(
                                bitmap = bitmap,
                                contentDescription = null,
                                modifier = Modifier.fillMaxSize(),
                                contentScale = ContentScale.Crop
                            )
                        }
                    )
                }
            }
        }
    }

    @Test
    fun radarLoading() {
        captureRoboImage {
            BreezyWeatherTheme {
                DetailShell { padding ->
                    RadarLoadingContent(
                        androidx.compose.ui.Modifier
                            .fillMaxSize()
                            .padding(padding)
                    )
                }
            }
        }
    }

    @Test
    fun radarDetailUnavailable() {
        captureRoboImage {
            BreezyWeatherTheme {
                DetailShell { padding ->
                    RadarUnavailableContent(
                        androidx.compose.ui.Modifier
                            .fillMaxSize()
                            .padding(padding)
                    )
                }
            }
        }
    }

    @Test
    @Config(qualifiers = "w1080dp-h2400dp-night-420dpi")
    fun radarDetailNight() {
        val bitmap = fixtureBitmap("radar-map-night").asImageBitmap()
        val manifest = fakeManifest()
        captureRoboImage {
            BreezyWeatherTheme {
                DetailShell { _ ->
                    RadarDetailContent(
                        manifest = manifest,
                        frame = manifest.frames[2],
                        frameIndex = 2,
                        onFrameChange = {},
                        readout = null,
                        mapContent = {
                            Image(
                                bitmap = bitmap,
                                contentDescription = null,
                                modifier = Modifier.fillMaxSize(),
                                contentScale = ContentScale.Crop
                            )
                        }
                    )
                }
            }
        }
    }

    @androidx.compose.runtime.Composable
    private fun DetailShell(
        content: @androidx.compose.runtime.Composable (
            androidx.compose.foundation.layout.PaddingValues,
        ) -> Unit,
    ) {
        androidx.compose.material3.Surface(
            color = androidx.compose.material3.MaterialTheme.colorScheme.background
        ) {
            androidx.compose.material3.Scaffold(
                topBar = {
                    androidx.compose.material3.TopAppBar(
                        title = {
                            androidx.compose.material3.Text("Radar")
                        },
                        navigationIcon = {
                            androidx.compose.material3.IconButton(onClick = {}) {
                                androidx.compose.material3.Icon(
                                    Icons.AutoMirrored.Filled.ArrowBack,
                                    contentDescription = null
                                )
                            }
                        }
                    )
                }
            ) { padding ->
                content(padding)
            }
        }
    }
}
