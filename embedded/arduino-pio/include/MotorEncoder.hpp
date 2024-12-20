#pragma once

#include "Arduino.h"


class Motor {
private:
    static constexpr int MAX_ABS_PWM = 255;

    const uint8_t dir_pin;
    const uint8_t speed_pin;

public:
    Motor(uint8_t s, uint8_t d) :
        dir_pin{d}, speed_pin{s} {
        pinMode(s, OUTPUT);
        pinMode(d, OUTPUT);
    }

    void setSpeed(int16_t speed) const {
        speed = constrain(speed, -MAX_ABS_PWM, MAX_ABS_PWM);
        digitalWrite(dir_pin, speed > 0);
        analogWrite(speed_pin, abs(speed));
    }
};

class Encoder {
private:
    const uint8_t pin_b;

public:
    mutable volatile int32_t position_ticks{0};

    Encoder(uint8_t a, uint8_t b, void(*interrupt_handler)()) :
        pin_b{b} {
        pinMode(a, INPUT);
        pinMode(b, INPUT);
        attachInterrupt(digitalPinToInterrupt(a), interrupt_handler, RISING);
    }

    /// Вызывать в обработчике прерываний
    void onPinA() const {
        if (digitalRead(pin_b)) {
            position_ticks++;
        } else {
            position_ticks--;
        }
    }
};

/// Хронометр - Рассчитывает dt
class Chronometer {
private:
    /// Время предыдущего расчёта
    uint32_t last_time{0};

public:
    /// Рассчитать dt с предыдущей итерации
    uint32_t getDeltaTime() {
        uint32_t dt = millis() - last_time;
        last_time = millis();
        return dt;
    }
};

/// Вспомогательный класс находит производную значения
class Differentiator {
private:
    /// Значение в предыдущий момент
    mutable float last_value{0};
    /// Возвращаемое значение
    mutable float diff{0};
public:
    /// Рассчитать производную
    float calc(float current_value, float dt) const {
        if (dt > 0) {
            diff = (current_value - last_value) / dt;
            last_value = current_value;
        }

        return diff;
    }
};

/// Вспомогательный класс аккумулирует значения
class Integrator {
private:
    /// Ограничение значений
    const float max_abs_value;
    mutable float integral{0};

public:
    explicit Integrator(float max_abs_value) :
        max_abs_value(max_abs_value) {}

    float calc(float value, float dt) const {
        if (dt > 0) {
            integral += value * dt;
            integral = constrain(integral, -max_abs_value, max_abs_value);
        }

        return integral;
    }
};

/// Pid-регулятор
class PID {
private:
    const float kp, ki, kd;
    const Integrator integrator;
    const Differentiator differentiator;
    mutable Chronometer chronometer;

public:
    int32_t target{0};

    explicit PID(float kp, float ki, float kd, float max_abs_i) :
        kp(kp), ki(ki), kd(kd), integrator(max_abs_i) {}

    /// Рассчитать управляющее воздействие регулятора
    float calc(int32_t input) const {
        const auto error = float(target - input);
        const auto dt = float(chronometer.getDeltaTime());

        const float p = error * kp;
        const float i = integrator.calc(error, dt) * ki;
        const float d = differentiator.calc(error, dt) * kd;

        return (p + i + d);
    }
};

class PositionServo {

private:
    const Motor motor;
    const Encoder encoder;
    PID position_regulator;

public:
    explicit PositionServo(Motor &&motor, Encoder &&encoder, PID &&pid) :
        motor{motor}, encoder{encoder}, position_regulator{pid} {}

    inline const Encoder &getEncoder() {
        return encoder;
    }

    /// Установить целевую позицию
    void setPosition(int32_t new_target) {
        position_regulator.target = new_target;
    }

    /// Обновить регулятор
    void update() {
        const auto speed_u = int16_t(position_regulator.calc(encoder.position_ticks));
        motor.setSpeed(speed_u);
    }
};
