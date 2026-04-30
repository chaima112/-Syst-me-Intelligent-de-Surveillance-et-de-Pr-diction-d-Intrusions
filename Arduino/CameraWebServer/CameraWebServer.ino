#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>

// --- إعدادات الشبكة ---
const char* ssid = "Orange-7E99";
const char* password = "JRN8GQ7J9BD";
// تأكدي أن هذا هو الـ IP اللي يظهر في الـ CMD متاع السيرفر
const char* serverUrl = "http://192.168.1.110:5000/detect"; 

// --- دبابيس الكاميرا (AI-Thinker) ---
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

void setup() {
  Serial.begin(115200);
  
  // إعداد الكاميرا
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
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QVGA; // حجم صورة صغير للسرعة
  config.jpeg_quality = 12;
  config.fb_count = 1;

  // تشغيل الكاميرا
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed: 0x%x", err);
    return;
  }

  // الاتصال بالـ Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected!");
}

void loop() {
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Capture failed");
    delay(1000);
    return;
  }

  HTTPClient http;
  http.begin(serverUrl);
  
  // نبعثوا التصويرة كـ JPEG مباشرة
  http.addHeader("Content-Type", "image/jpeg");

  Serial.println("Sending image to YOLO...");
  int httpCode = http.POST(fb->buf, fb->len); // إرسال بسيط ومضمون

  if (httpCode > 0) {
    String payload = http.getString();
    Serial.print("YOLO Result: ");
    Serial.println(payload);
  } else {
    Serial.printf("Error: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
  esp_camera_fb_return(fb);
  delay(5000); // استراحة بـ 5 ثواني
}
