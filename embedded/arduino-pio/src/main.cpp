#include "serialcmd/Types.hpp"
#include "serialcmd/StreamSerializer.hpp"
#include "serialcmd/Protocol.hpp"
#include "MotorEncoder.hpp"

#include <Arduino.h>


static void encoder_int_handler();

auto m = Motor(5, 4);

auto e = Encoder(2, 8, encoder_int_handler);

void encoder_int_handler() { e.onPinA(); }

namespace cmd {
    using serialcmd::StreamSerializer;

    enum Result : serialcmd::u8 {
        ok = 0x00,
        error = 0x01
    };

    // set_motor_speed<00>(i16) -> (None, MotorEncoderError<u8>)
    void set_motor_speed(StreamSerializer &serializer) {
        serialcmd::i16 speed;
        serializer.read(speed);
        m.setSpeed(speed);

        serializer.write(Result::ok);
    }

    // get_encoder_ticks<01>(None) -> (i32, MotorEncoderError<u8>)
    void get_encoder_ticks(StreamSerializer &serializer) {
        serializer.write(Result::ok);

        serialcmd::i32 ret = e.position_ticks;
        serializer.write(ret);
    }

    typedef void(*Cmd)(StreamSerializer &);

    Cmd commands[] = {
        set_motor_speed,
        get_encoder_ticks
    };
}

serialcmd::Protocol<uint8_t, uint8_t> protocol(cmd::commands, 2, Serial);

void setup() {
    Serial.begin(115200);
    protocol.begin(0x01);
}

void loop() {
    protocol.pull();
}


