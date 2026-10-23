/**
 * Edge Impulse image collection server for ESP32-CAM + OV3660.
 *
 * If Serial Monitor shows repeated:
 *   cam_hal: FB-OVF
 *
 * the camera is pushing frames faster than the ESP32 camera driver can consume
 * them. For OV3660 modules, using a slower XCLK is usually the first fix.
 *
 * Arduino IDE settings:
 * - Board: AI Thinker ESP32-CAM, if using the common ESP32-CAM module
 * - PSRAM: Enabled
 * - Core Debug Level: Info
 */

#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASS "YOUR_WIFI_PASSWORD"
#define HOSTNAME "esp32cam"

#include "esp_camera.h"
#include <eloquent_esp32cam.h>
#include <eloquent_esp32cam/extra/esp32/wifi/sta.h>
#include <eloquent_esp32cam/viz/image_collection.h>

using eloq::camera;
using eloq::wifi;
using eloq::viz::collectionServer;

// Most ESP32-CAM boards use the AI Thinker pinout, even if the sensor is OV3660.
// If your board is an ESP32-S3 camera board, set AI Thinker to 0 and WROOM S3 to 1.
#define USE_AITHINKER_PINOUT 1
#define USE_WROOM_S3_PINOUT 0

// Set these after checking the browser preview.
// VFLIP fixes upside-down images. HMIRROR fixes left-right mirrored images.
#define CAMERA_VFLIP 1
#define CAMERA_HMIRROR 0

void setupCameraPinout() {
#if USE_AITHINKER_PINOUT
  camera.pinout.aithinker();
#elif USE_WROOM_S3_PINOUT
  camera.pinout.wroom_s3();
#else
  camera.pinout.autodetect();
#endif
}

void setupCameraOrientation() {
  sensor_t *sensor = esp_camera_sensor_get();

  if (sensor == NULL) {
    Serial.println("Could not get camera sensor settings");
    return;
  }

  sensor->set_vflip(sensor, CAMERA_VFLIP);
  sensor->set_hmirror(sensor, CAMERA_HMIRROR);

  // OV3660 modules often look a little saturated with default settings.
  if (sensor->id.PID == OV3660_PID) {
    sensor->set_brightness(sensor, 1);
    sensor->set_saturation(sensor, 0);
  }
}

void setup() {
  delay(3000);
  Serial.begin(115200);
  Serial.println();
  Serial.println("___IMAGE COLLECTION SERVER - OV3660 SAFE MODE___");
  Serial.printf("PSRAM: %s\n", psramFound() ? "FOUND" : "NOT FOUND");

  setupCameraPinout();
  camera.brownout.disable();

  // OV3660 can overflow the frame buffer at the default 20 MHz XCLK.
  camera.xclk.slow();          // 10 MHz, more stable for OV3660
  camera.resolution.face();    // 240x240, good for Edge Impulse image projects
  camera.quality.low();        // smaller JPEG than high/best, helps WiFi server stability

  while (!camera.begin().isOk()) {
    Serial.println(camera.exception.toString());
    delay(1000);
  }
  setupCameraOrientation();

  while (!wifi.connect().isOk()) {
    Serial.println(wifi.exception.toString());
    delay(1000);
  }

  while (!collectionServer.begin().isOk()) {
    Serial.println(collectionServer.exception.toString());
    delay(1000);
  }

  Serial.println("Camera OK");
  Serial.println("WiFi OK");
  Serial.println("Image Collection Server OK");
  Serial.println(collectionServer.address());
}

void loop() {
  // The collection server runs in its own task.
  delay(1000);
}
