// 28BYJ-48 스텝모터와 LDR(조도센서) 기반 자동 커튼 제어
#include <Stepper.h>

// 자동 커튼 제어를 담당하는 클래스 (PascalCase)
class CurtainController {
public:
  CurtainController(
    int motorPin1,
    int motorPin2,
    int motorPin3,
    int motorPin4,
    int lightSensorPin,
    int lightThreshold,
    long fullOpenSteps,
    int motorRpm,
    const char* deviceIdParam
  )
    : stepsPerRevolution(2048),
      stepper(stepsPerRevolution, motorPin1, motorPin2, motorPin3, motorPin4),
      ldrPin(lightSensorPin),
      threshold(lightThreshold),
      curtainMaxSteps(fullOpenSteps),
      currentStep(0),
      motorDirection(0),
      lastReadTime(0),
      motorSpeedRpm(motorRpm),
      deviceId(deviceIdParam) {
  }

  void begin() {
    Serial.begin(9600);
    pinMode(ldrPin, INPUT);
    stepper.setSpeed(motorSpeedRpm);
  }

  // loop() 안에서 매번 호출되는 메서드 (camelCase)
  void update() {
    unsigned long now = millis();

    // 3초마다 조도값 측정 및 모터 방향 결정 + 로그 출력
    if (now - lastReadTime >= 3000) {
      int lightValue = analogRead(ldrPin);
      lastReadTime = now;

      if (lightValue > threshold && currentStep < curtainMaxSteps) {
        motorDirection = 1; // 열림
      } else if (lightValue < threshold && currentStep > 0) {
        motorDirection = -1; // 닫힘
      } else {
        motorDirection = 0; // 정지
      }

      // DB에 넣기 좋은 CSV 한 줄 출력
      // device_id,light_value,motor_direction,current_step,max_steps
      Serial.print(deviceId);
      Serial.print(",");
      Serial.print(lightValue);
      Serial.print(",");
      Serial.print(motorDirection);
      Serial.print(",");
      Serial.print(currentStep);
      Serial.print(",");
      Serial.println(curtainMaxSteps);
    }

    // 모터를 한 스텝씩 이동
    if (motorDirection == 1 && currentStep < curtainMaxSteps) {
      stepper.setSpeed(motorSpeedRpm);
      stepper.step(1);
      currentStep++;
    } else if (motorDirection == -1 && currentStep > 0) {
      stepper.setSpeed(motorSpeedRpm);
      stepper.step(-1);
      currentStep--;
    }

    delay(5);
  }

private:
  const int stepsPerRevolution; // 28BYJ-48 한 바퀴 스텝 수
  Stepper stepper;              // 스텝모터 인스턴스

  const int ldrPin;             // LDR 센서 핀
  const int threshold;          // 밝기 임계값
  const long curtainMaxSteps;   // 커튼 완전 개폐 스텝 수

  long currentStep;             // 현재 커튼 위치(스텝)
  int motorDirection;           // 1: 열림, -1: 닫힘, 0: 정지
  unsigned long lastReadTime;   // 마지막 센서 측정 시각(ms)
  int motorSpeedRpm;            // 모터 속도(RPM)
  const char* deviceId;         // ← 추가
};

// 전역에서 컨트롤러 인스턴스 생성 (PascalCase 타입, camelCase 변수명)
CurtainController curtainController(
  8,   // motorPin1
  10,  // motorPin2
  9,   // motorPin3
  11,  // motorPin4
  A0,  // lightSensorPin (LDR)
  500, // lightThreshold
  3L * 2048, // fullOpenSteps (3바퀴)
  20,  // motorRpm
  "curtain-01" // deviceId
);

void setup() {
  curtainController.begin();
}

void loop() {
  curtainController.update();
}