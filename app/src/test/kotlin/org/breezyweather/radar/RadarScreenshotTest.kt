package org.breezyweather.radar

import android.graphics.BitmapFactory
import android.view.LayoutInflater
import android.widget.ImageView
import android.widget.TextView
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import com.github.takahirom.roborazzi.captureRoboImage
import org.breezyweather.R
import org.breezyweather.ui.radar.RadarDetailContent
import org.breezyweather.ui.theme.compose.BreezyWeatherTheme
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode
import java.io.File

/**
 * JVM screenshots (Roborazzi, no device): the radar card inflated with the
 * real live snapshot PNG, and the detail chrome with a snapshot stand-in
 * for the GL map (MapLibre cannot render on JVM).
 */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w1080dp-h2400dp-420dpi")
class RadarScreenshotTest {

    private fun fixtureBitmap() =
        BitmapFactory.decodeStream(File("src/test/resources/radar-snapshot.png").inputStream())

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
    fun radarCard() {
        androidx.test.core.app.ActivityScenario.launch(ScreenshotActivity::class.java)
            .use { scenario ->
                scenario.onActivity { activity ->
                    val card = LayoutInflater.from(activity)
                        .inflate(R.layout.container_main_radar, null)
                    card.findViewById<ImageView>(R.id.radar_snapshot)
                        .setImageBitmap(fixtureBitmap())
                    card.findViewById<TextView>(R.id.radar_subtitle).text =
                        "Updated 10 min ago"
                    activity.setContentView(card)
                }
                androidx.test.espresso.Espresso.onView(
                    androidx.test.espresso.matcher.ViewMatchers.isRoot()
                ).captureRoboImage()
            }
    }

    @Test
    fun radarDetail() {
        // Snapshot stand-in for the GL map (MapLibre cannot render on JVM).
        val bitmap = fixtureBitmap().asImageBitmap()
        val manifest = fakeManifest()
        captureRoboImage {
            BreezyWeatherTheme {
                RadarDetailContent(
                    manifest = manifest,
                    frame = manifest.frames[1],
                    frameIndex = 1,
                    onFrameChange = {},
                    readout = "1.0–2.0 mm/h · obs",
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

    @Test
    @Config(qualifiers = "w1080dp-h2400dp-420dpi-night")
    fun radarDetailNight() {
        val bitmap = fixtureBitmap().asImageBitmap()
        val manifest = fakeManifest()
        captureRoboImage {
            BreezyWeatherTheme {
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
