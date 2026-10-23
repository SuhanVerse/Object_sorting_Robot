#include "esp_camera.h"
#include <WiFi.h>
#include "esp_http_server.h"

// --- Wi-Fi Credentials ---
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// --- ESP32-S3 WROOM Pinout ---
#define PWDN_GPIO_NUM  -1
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM  15
#define SIOD_GPIO_NUM  4
#define SIOC_GPIO_NUM  5
#define Y9_GPIO_NUM    16
#define Y8_GPIO_NUM    17
#define Y7_GPIO_NUM    18
#define Y6_GPIO_NUM    12
#define Y5_GPIO_NUM    10
#define Y4_GPIO_NUM    8
#define Y3_GPIO_NUM    9
#define Y2_GPIO_NUM    11
#define VSYNC_GPIO_NUM 6
#define HREF_GPIO_NUM  7
#define PCLK_GPIO_NUM  13

#define ARDUINO_TX_PIN 43
#define ARDUINO_RX_PIN 44

httpd_handle_t stream_httpd = NULL;
char dummyDecision = 'A'; // Start the cycle with 'A'

static esp_err_t stream_handler(httpd_req_t *req) {
  camera_fb_t * fb = NULL;
  esp_err_t res = ESP_OK;
  char * part_buf[64];
  static const char* _STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=123456789000000000000987654321";
  static const char* _STREAM_BOUNDARY = "\r\n--123456789000000000000987654321\r\n";
  static const char* _STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

  res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
  if(res != ESP_OK) return res;

  while(true) {
    fb = esp_camera_fb_get();
    if (!fb) {
      res = ESP_FAIL;
    } else {
      res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
      if(res == ESP_OK) {
        size_t hlen = snprintf((char *)part_buf, 64, _STREAM_PART, fb->len);
        res = httpd_resp_send_chunk(req, (const char *)part_buf, hlen);
      }
      if(res == ESP_OK) {
        res = httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);
      }
      esp_camera_fb_return(fb);
    }
    if(res != ESP_OK) break;
  }
  return res;
}

void startCameraServer() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 80;
  
  httpd_uri_t stream_uri = {
    .uri       = "/",
    .method    = HTTP_GET,
    .handler   = stream_handler,
    .user_ctx  = NULL
  };
  
  if (httpd_start(&stream_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(stream_httpd, &stream_uri);
  }
}

void setup() {
  Serial.begin(115200);
  Serial1.begin(115200, SERIAL_8N1, ARDUINO_RX_PIN, ARDUINO_TX_PIN); // Connect to Arduino
  
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  
  config.xclk_freq_hz = 16000000; 
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_VGA; 
  config.jpeg_quality = 12; 
  
  if (psramFound()) {
    config.fb_count = 2; 
    config.grab_mode = CAMERA_GRAB_LATEST; 
  } else {
    config.fb_count = 1;
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  }

  esp_camera_init(&config);

  // --- NEW WI-FI CONNECTION LOGIC ---
  Serial.println("\n--- Initializing System ---");
  Serial.print("Connecting to Wi-Fi network: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  // Try to connect for 10 seconds (20 attempts * 500ms)
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  Serial.println(); // Move to the next line

  // Check if connection was successful
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("SUCCESS: Wi-Fi Connected!");
    Serial.print("IP Address for Camera Stream: http://");
    Serial.println(WiFi.localIP());
    startCameraServer();
    Serial.println("Camera Server Started.");
  } else {
    Serial.println("ERROR: Wi-Fi Connection FAILED!");
    Serial.println("Check your SSID and Password, or ensure you are on a 2.4GHz network.");
  }
  // ----------------------------------
}

void loop() {
  // Listen for the '?' ping from the Arduino
  if (Serial1.available()) {
    char incoming = Serial1.read();
    
    if (incoming == '?') {
      // Send the current dummy decision
      Serial1.print(dummyDecision);
      Serial.print("Received Ping. Sent Dummy Decision: ");
      Serial.println(dummyDecision); // Print this to Serial monitor so you can see it working
      
      // Cycle to the next decision for the next time an object arrives
      if (dummyDecision == 'A') {
        dummyDecision = 'B';
      } else if (dummyDecision == 'B') {
        dummyDecision = 'C';
      } else {
        dummyDecision = 'A';
      }
    }
  }
}