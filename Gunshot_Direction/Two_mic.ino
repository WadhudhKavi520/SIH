#include <driver/i2s.h>
#include <math.h>

#define I2S_WS 33   // I2S Word Select (WS) line
#define I2S_SCK 32  // I2S Clock (SCK) line
#define I2S_SD 25   // I2S Data In for microphone

// INMP441 microphone specifications
const float SENSITIVITY = -26;      // dBV/Pa
const float REF_DB = 70.0;          // Reference dB SPL (1 Pa)
const float SAMPLE_RATE = 16000.0;  // Sample rate in Hz

void setup() {
  Serial.begin(115200);

  // I2S configuration
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = 64,
    .use_apll = false
  };

  // I2S pin configuration
  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD
  };

  // Install and start I2S driver
  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pin_config);
}

float convertRawToDb(int32_t raw_value) {
  // Convert 32-bit raw value to voltage
  float voltage = (float)raw_value / 2147483648.0;  // 2^31 for 32-bit sample

  // Avoid log of zero or negative numbers
  if (voltage <= 0) {
    return -INFINITY;
  }

  // Calculate dB SPL
  float db_spl = 20 * log10(voltage / pow(10, SENSITIVITY / 20)) + REF_DB;

  return db_spl;
}

int crossCorrelate(int32_t *right, int32_t *left, size_t length) {
  int max_index = 0;
  float max_value = -INFINITY;

  for (int lag = -((int)length - 1); lag < (int)length; lag++) {
    float sum = 0.0;

    for (size_t i = 0; i < length; i++) {
      int left_index = i + lag;

      if (left_index >= 0 && left_index < length) {
        sum += (float)right[i] * left[left_index];
      }
    }

    if (sum > max_value) {
      max_value = sum;
      max_index = lag;
    }
  }

  return max_index;
}

void loop() {
  int32_t i2s_read_buff[64];
  size_t bytes_read;

  // Read data from the I2S interface
  i2s_read(I2S_NUM_0, (char *)i2s_read_buff, sizeof(i2s_read_buff), &bytes_read, portMAX_DELAY);

  // Split data into right and left channels
  int32_t right_channel[32];
  int32_t left_channel[32];

  for (int i = 0; i < bytes_read / 8; i++) {     // 8 bytes for two 32-bit samples (right + left)
    right_channel[i] = i2s_read_buff[i * 2];     // Right channel
    left_channel[i] = i2s_read_buff[i * 2 + 1];  // Left channel
  }

  // Calculate SPL for both channels
  float sum_db_right = 0;
  float sum_db_left = 0;
  int valid_samples_right = 0;
  int valid_samples_left = 0;

  for (int i = 0; i < 32; i++) {
    float db_right = convertRawToDb(right_channel[i]);
    float db_left = convertRawToDb(left_channel[i]);

    if (!isinf(db_right)) {
      sum_db_right += db_right;
      valid_samples_right++;
    }

    if (!isinf(db_left)) {
      sum_db_left += db_left;
      valid_samples_left++;
    }
  }

  if (valid_samples_right > 0) {
    float avg_db_right = sum_db_right / valid_samples_right;
    Serial.printf("Right Channel SPL: %.2f dB\n", avg_db_right);
  } else {
    Serial.println("Right channel sound level too low to measure");
  }

  if (valid_samples_left > 0) {
    float avg_db_left = sum_db_left / valid_samples_left;
    Serial.printf("Left Channel SPL: %.2f dB\n", avg_db_left);
  } else {
    Serial.println("Left channel sound level too low to measure");
  }

  // Calculate time delay using cross-correlation
  int lag_samples = crossCorrelate(right_channel, left_channel, 32);
  float time_delay = (float)lag_samples / SAMPLE_RATE;

  //Calculate angle of arrival
  float speedOfSound = 343.0;  // Speed of sound in air in m/s
  float micDistance = 0.15;     // Distance between microphones in meters
  float angle = asin(fmin(fmax((time_delay * speedOfSound) / micDistance, -1.0), 1.0));


  Serial.printf("Time delay between right and left channel: %.6f seconds\n", time_delay);

  Serial.printf("Angle of arrival: %.2f degrees\n", angle * (180.0 / M_PI));



  delay(1000);  
}
