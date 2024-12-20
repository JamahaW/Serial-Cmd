#include "serialcmd/Types.hpp"
#include "serialcmd/StreamSerializer.hpp"
#include "serialcmd/Protocol.hpp"
#include "MotorEncoder.hpp"

#include <Arduino.h>


static void encoder_int_handler();

auto m = Motor(5, 4);

auto e = Encoder(2, 8, encoder_int_handler);

void encoder_int_handler() { e.onPinA(); }



//serialcmd::Protocol<uint8_t, uint8_t> protocol(cmd::commands, 5, Serial);

void setup() {
    Serial.begin(115200);
//    protocol.begin(0x01);
}

void loop() {
//    protocol.pull();
}

//namespace cmd {
//    using serialcmd::StreamSerializer;
//
//    using serialcmd::u8;
//    using serialcmd::u32;
//
//    enum Result : serialcmd::u8 {
//        ok = 0x00,
//        error = 0x01
//    };
//
//    inline bool isDigitalPin(u8 pin) {
//        return pin < 14;
//    }
//
//    /// pinMode<00>({u8, u8}) -> (None, ArduinoError<u8>)
//    void pin_mode(StreamSerializer &serializer) {
//        struct { u8 pin, mode; } data{};
//        serializer.read(data);
//
//        pinMode(data.pin, data.mode);
//
//        serializer.write(Result::ok);
//    }
//
//    /// digitalWrite<01>({u8, u8}) -> (None, ArduinoError<u8>)
//    void digital_write(StreamSerializer &serializer) {
//        u8 pin;
//        serializer.read(pin);
//
//        if (not isDigitalPin(pin)) {
//            serializer.write(Result::error);
//            return;
//        }
//
//        u8 state;
//        serializer.read(state);
//
//        digitalWrite(pin, state);
//
//        serializer.write(Result::ok);
//    }
//
//    /// digitalRead<02>(u8) -> (u8, ArduinoError<u8>)
//    void digital_read(StreamSerializer &serializer) {
//        u8 v;
//        serializer.read(v);
//
//        if (not isDigitalPin(v)) {
//            serializer.write(Result::error);
//            return;
//        }
//
//        serializer.write(Result::ok);
//
//        v = digitalRead(v);
//        serializer.write(v);
//    }
//
//    /// millis<03>(None) -> (u32, ArduinoError<u8>)
//    void millis(StreamSerializer &serializer) {
//        u32 ret = ::millis();
//
//        serializer.write(Result::ok);
//        serializer.write(ret);
//    }
//
//    /// delay<04>(u32) -> (None, ArduinoError<u8>)
//    void delay(StreamSerializer &serializer) {
//        u32 v;
//        serializer.read(v);
//
//        ::delay(v);
//
//        serializer.write(Result::ok);
//    }
//
//    typedef void(*Cmd)(StreamSerializer &);
//
//    Cmd commands[] = {
//        pin_mode,
//        digital_write,
//        digital_read,
//        millis,
//        delay
//    };
//}
