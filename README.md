# 스마트홈 IoT 통합 제어 시스템
<p align="center">
<img width="500" height="500" alt="ChatGPT Image Nov 21, 2025, 05_59_30 PM" src="https://github.com/user-attachments/assets/e77fd823-041e-43db-b68f-6cae45c90900" />
</p>


## 프로젝트 개요

아두이노 기반 마이크로컨트롤러와 중앙 제어 PC를 연동하여 공동현관, 엘리베이터, 실내 환경, 커튼을 통합으로 관리하는 스마트홈 IoT 시스템입니다.

### 기술 스택

| 카테고리 | 기술 |
|---------|------|
| **백엔드 & 서버** | ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white) ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) |
| **프론트엔드 & UI** | ![PyQt6](https://img.shields.io/badge/PyQt6-41CD52?style=for-the-badge&logo=qt&logoColor=white) |
| **하드웨어** | ![Arduino](https://img.shields.io/badge/Arduino-00979D?style=for-the-badge&logo=arduino&logoColor=white) ![C++](https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=cplusplus&logoColor=white) |
| **데이터베이스** | ![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white) ![AWS RDS](https://img.shields.io/badge/AWS%20RDS-527FFF?style=for-the-badge&logo=amazon-aws&logoColor=white) |
| **협업 & 관리** | ![Jira](https://img.shields.io/badge/Jira-0052CC?style=for-the-badge&logo=jira&logoColor=white) ![Confluence](https://img.shields.io/badge/Confluence-172B4D?style=for-the-badge&logo=confluence&logoColor=white) |


## 팀 정보
| 이름 | 역할 | GitHub |
|------|------|--------|
| 양효인 | 팀장, 공동현관 기능 구현, Flask 서버 구현 | [@hyoinYang](https://github.com/hyoinYang) |
| 박용우 | 대시보드 구현, 엘리베이터 기능 구현 | [@tomung-puppy](https://github.com/tomung-puppy) |
| 이준규 | 실내 환경 제어 기능 구현 | [@yesbandyok](https://github.com/yesbandyok) |
| 최종명 | 커튼 자동 제어 기능 구현 | [@northpard](https://github.com/northpard) |
| 한창희 | ppt 제작, 발표 | [@Jihye080498](https://github.com/Jihye080498) |


## 주요 기능

- **RFID 기반 공동현관 제어**: 카드 인식을 통한 보안 출입 관리
- **엘리베이터 통합 제어**: 공동현관 연동 자동 호출 및 층수 관리
- **실내 환경 모니터링**: 온습도 기반 자동 에어컨/히터/가습기 제어
- **조도 기반 커튼 제어**: 외부 밝기에 따른 자동/수동 커튼 조절
- **통합 대시보드**: 모든 기능을 한눈에 모니터링하고 제어
- **데이터 로깅**: 모든 센서 데이터 및 제어 기록을 DB에 저장

## 아키텍처
### 하드웨어 아키텍처
<img width="1074" height="498" alt="Screenshot from 2025-12-12 16-51-28" src="https://github.com/user-attachments/assets/5ba88891-1cf6-49fc-b8a3-39233ce36e3d" />

### 소프트웨어 아키텍처
<img width="1074" height="578" alt="Screenshot from 2025-12-12 16-52-07" src="https://github.com/user-attachments/assets/eccbe14e-d07f-44d9-8937-899468cdd350" />


## 모듈별 기능

### 공동현관 (Entry)
- 사전에 인가된 태그가 인식되면 공동현관 열기
- 문 사이에 물체를 인지해 공동현관이 닫히는 타이밍 조절
- 태그 정보, 공동현관 열림/닫힘 여부를 모니터링
- 수동 제어 모드 지원

### 엘리베이터 (Elevator)
- 공동현관이 열리면 엘리베이터 자동 호출
- 다른 층의 호출 구현

### 실내 환경 제어 (Climate)
- 온도, 습도 실시간 모니터링
- 자동 에어컨/히터/가습기 제어
- 수동 제어 모드 지원

### 커튼 제어 (Curtain)
- 조도 센서 기반 자동 커튼 제어
- 수동 제어 모드 지원
- 모터 위치 및 방향 모니터링

## 통신 프로토콜

모든 아두이노는 중앙 PC와 직렬 통신으로 통신합니다. 상세한 프로토콜 명세는 [PROTOCOL.md](./docs/PROTOCOL.md)를 참조하세요.

## 데이터베이스

모든 장치의 로그는 AWS RDS MySQL에 통합 저장됩니다:

```sql
CREATE TABLE curtain_log (
    log_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    timestamp DATETIME,
    device_id VARCHAR(50),
    data_type VARCHAR(20),
    metric_name VARCHAR(50),
    value VARCHAR(255)
);
```

- **저장 시점**: 센서 데이터 - 3초 주기, 이벤트 데이터 - 이벤트 발생 당시
- **접근 제어**: 아두이노는 DB에 직접 접근 불가 (중앙 서버를 통해서만 접근)


## 프로젝트 구조

```
smart-home-iot/
├── README.md
├── PROTOCOL.md                # 통신 프로토콜 상세 명세
├── requirements.txt
├── main.py                    # 메인 애플리케이션
|
├── ui/
│   ├── dashboard.py          # 메인 대시보드 UI
│   ├── log_viewer.py         # 로그 뷰어
│   └── widgets/              # UI 컴포넌트
├── devices/
│   ├── entrance/
│   │   └── entry.ino         # 공동현관 제어
│   ├── curtain/
│   │   └── curtain.ino       # 커튼 제어
│   ├── elevator/
│   │   └── elevator.ino      # 엘리베이터 제어
│   ├── dht/
│   │   └── dht.ino           # 온습도 제어
├── service/
│   ├── app/
│   │   └── main.py           # Flask 서버 실행
└── ├── pyqt/
        └── dashboard.py      # PyQT6 대시보드 실행

```

