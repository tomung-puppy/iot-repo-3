// pin Setting
const int FIRST00_PIN = A0;
const int FIRST01_PIN = 2;
const int FIRST02_PIN = 3;
const int SECOND00_PIN = 4;
const int SECOND01_PIN = 5;
const int SECOND02_PIN = 6;
const int THIRD00_PIN = 7;
const int LEDFIRST_PIN = 10;
const int LEDSECOND_PIN = 9;
const int LEDTHIRD_PIN = 8;
const int BUTTONFIRST_PIN = 11;
const int BUTTONSECOND_PIN = 12;
const int BUTTONTHIRD_PIN = 13;

// time/count control
unsigned long previous_time = 0;
unsigned long current_time = 0;
int current_button_state[] = {LOW, LOW, LOW};
int last_button_state[] = {LOW, LOW, LOW};
unsigned long wait_time = 0;

// variables
const int button_pin_arr[] = {BUTTONFIRST_PIN, BUTTONSECOND_PIN, BUTTONTHIRD_PIN};
const int LED_pin_arr[] = {LEDFIRST_PIN, LEDSECOND_PIN, LEDTHIRD_PIN};
const int ele_LED_pin_arr[] = {FIRST00_PIN, FIRST01_PIN, FIRST02_PIN, SECOND00_PIN, SECOND01_PIN, SECOND02_PIN, THIRD00_PIN};
bool LED_stat[] = {false, false, false};

enum{WAIT, UP, DOWN};
int ele_mode = WAIT;
int ele_dst[] = {0, 0};
int ele_pos = 0;

// 변환 함수

int fromFloorToElepos(int floor)
{
  int elepos;
  elepos = floor*3;
  return elepos;
}

int fromEleposeToFloor(int elepos)
{
  int floor;
  floor = elepos/3;
  return floor;
}

void assignEleDst()
{
    int min_req = -1; 
    int max_req = -1; 
    
    for (int i = 0; i < sizeof(LED_stat)/sizeof(LED_stat[0]); i++) 
    {
      if (LED_stat[i] == true) 
      {
        min_req = i;
        break; 
      }
    }

    for (int i = sizeof(LED_stat)/sizeof(LED_stat[0])-1; i >= 0; i--) 
    {
      if (LED_stat[i] == true) 
      {
        max_req = i;
        break; 
      }
    }
    
    if (min_req != -1) // 켜진 LED가 존재 -> destination 설정
    {
      switch (ele_mode)
      {
        case UP:
          if (ele_pos <= fromFloorToElepos(max_req))
          {
            ele_dst[1] = max_req;
            ele_dst[0] = min_req;
          }
          else
          {
            if (ele_pos % 3 == 0) max_req = fromEleposeToFloor(ele_pos);
            else max_req = fromEleposeToFloor(ele_pos) + 1;
            ele_dst[1] = max_req;
            ele_dst[0] = min_req;
          }
          break;
        case DOWN:
          if (ele_pos >= fromFloorToElepos(min_req))
          {
            ele_dst[0] = min_req;
            ele_dst[1] = max_req;
          }
          else
          {
            min_req = fromEleposeToFloor(ele_pos);
            ele_dst[0] = min_req;
            ele_dst[1] = max_req;
          }
          break;
        case WAIT:
          ele_dst[0] = min_req;
          ele_dst[1] = max_req;
          if (ele_pos > fromFloorToElepos(min_req))
            ele_mode = DOWN;
          else if (ele_pos < fromFloorToElepos(min_req))
            ele_mode = UP;
          else
            Serial.println("The elevator is already on the floor!");
      }
    } 
    else //다 꺼진 상태 -> 가장 가까운데로 가야됨
    {
      switch (ele_mode)
      {
        case UP:
          if (ele_pos % 3 == 0)
          {
            min_req = fromEleposeToFloor(ele_pos);
            max_req = fromEleposeToFloor(ele_pos);
          }
          else
          {
            min_req = fromEleposeToFloor(ele_pos) + 1;
            max_req = fromEleposeToFloor(ele_pos) + 1;
          }
          break;
        case DOWN:
          if (ele_pos % 3 == 0)
          {
            min_req = fromEleposeToFloor(ele_pos);
            max_req = fromEleposeToFloor(ele_pos);
          }
          else
          {
            min_req = fromEleposeToFloor(ele_pos) - 1;
            max_req = fromEleposeToFloor(ele_pos) - 1;
          }
          break;
      }
      ele_dst[0] = min_req;
      ele_dst[1] = max_req;
    }
}

void buttonEvent(byte floor)
{
  if (LED_stat[floor] == false)
  {
    digitalWrite(LED_pin_arr[floor], HIGH);
    LED_stat[floor] = true;
    Serial.print("Call at Floor "); Serial.println(floor+1);
  }
  else
  {
    digitalWrite(LED_pin_arr[floor], LOW);
    LED_stat[floor] = false;
    Serial.print("Cancel the Floor "); Serial.println(floor+1);
  }

  assignEleDst();

}

void arriveAtDstUpdateMode()
{

  if (ele_pos % 3 == 0)
  {
    int ele_cur_floor= fromEleposeToFloor(ele_pos);
    if (LED_stat[ele_cur_floor] == true)
    {
      digitalWrite(LED_pin_arr[ele_cur_floor], LOW);
      LED_stat[ele_cur_floor] = false;
      Serial.print("This is floor "); Serial.println(ele_cur_floor+1);
      Serial.println("Door is Opend");
      wait_time = 5000; 
    }

    assignEleDst();


    switch (ele_mode)
    {
      case WAIT:
        break;

      case UP:
        if (ele_cur_floor ==  ele_dst[1])
        {
          if (ele_cur_floor == ele_dst[0])
          {
            ele_mode = WAIT;
            Serial.println("Switch Mode : UP -> WAIT");
          }
          else
          {
            ele_mode = DOWN;
            Serial.println("Switch Mode : UP -> DOWN");
          }
        }
        break;

      case DOWN:
        if (ele_cur_floor ==  ele_dst[0])
        {
          if (ele_cur_floor == ele_dst[1])
          {
            ele_mode = WAIT;
            Serial.println("Switch Mode : DOWN -> WAIT");
          }
          else
          {
            ele_mode = UP;
            Serial.println("Switch Mode : DOWN -> UP");
          }
        }
        break;

      default:
        Serial.println("Something wrong: cannot convert elevator mode");
        break;      
    }
  }
}

void updateElePos()
{
  switch (ele_mode)
  {
  case WAIT:
    digitalWrite(ele_LED_pin_arr[ele_pos], HIGH);
    break;
  case UP:
    if (ele_pos == 6) // 안전장치
    {
      digitalWrite(ele_LED_pin_arr[ele_pos], HIGH);
      Serial.println("Arrive at the upper limit but still on the mode of UP");
    }
    else
    {
      digitalWrite(ele_LED_pin_arr[ele_pos], LOW);
      ele_pos += 1;
      digitalWrite(ele_LED_pin_arr[ele_pos], HIGH);
    }
    break;
  case DOWN:
    if (ele_pos == 0) // 안전장치
    {
      digitalWrite(ele_LED_pin_arr[ele_pos], HIGH);
      Serial.println("Arrive at the lower limit but still on the mode of DOWN");
    }
    else
    {
      digitalWrite(ele_LED_pin_arr[ele_pos], LOW);
      ele_pos -= 1;
      digitalWrite(ele_LED_pin_arr[ele_pos], HIGH);
    }
    break;
  default:
    break;
  }
}


void setup() {
  Serial.begin(9600);
  pinMode(FIRST00_PIN, OUTPUT);
  pinMode(FIRST01_PIN, OUTPUT);
  pinMode(FIRST02_PIN, OUTPUT);
  pinMode(SECOND00_PIN, OUTPUT);
  pinMode(SECOND01_PIN, OUTPUT);
  pinMode(SECOND02_PIN, OUTPUT);
  pinMode(THIRD00_PIN, OUTPUT);

  pinMode(LEDFIRST_PIN, OUTPUT);
  pinMode(LEDSECOND_PIN, OUTPUT);
  pinMode(LEDTHIRD_PIN, OUTPUT);
  pinMode(BUTTONFIRST_PIN, INPUT);
  pinMode(BUTTONSECOND_PIN, INPUT);
  pinMode(BUTTONTHIRD_PIN, INPUT);

}

void loop() {

  byte button;

  for (int i = 0; i < sizeof(button_pin_arr)/sizeof(button_pin_arr[0]); i++)
  {
    button = digitalRead(button_pin_arr[i]);
    if (button != last_button_state[i])
    {
      if (button == HIGH)
      {
        buttonEvent(i);
        last_button_state[i] = button;
      }
      else
        last_button_state[i] = button;
    }
  }
  
  arriveAtDstUpdateMode();

  if (wait_time != 0) 
  {
    // Serial.print(wait_time);
    wait_time--;
    if (wait_time == 0)
    {
      Serial.println("Door is closed");
    }
  }
  else
  {
    current_time = millis();
    if (current_time - previous_time > 1000) // 1초마다 엘리베이터 이동
    {
      if (ele_mode != WAIT)
      {
        Serial.print("Upper Dst: "); Serial.print(ele_dst[1]+1); Serial.print(" Lower Dst: "); Serial.println(ele_dst[0]+1);
      }
      updateElePos();
      previous_time = current_time;
    }
  }


}