// Keep the Saturn digital controller protocol; merge physical D-pad and stick.
#pragma once
#include <array>
static const int ACTIONPI_DIGITAL_DEADZONE = 32768 / 2;

// Bits: up, down, left, right. Opposite directions cancel until one is released.
inline unsigned actionpiDirectionMask(unsigned physical, int x, int y,
                                     int leftSign, int upSign, int deadzone) {
    if (x * leftSign > deadzone) physical |= 4;
    if (x * leftSign < -deadzone) physical |= 8;
    if (y * upSign > deadzone) physical |= 1;
    if (y * upSign < -deadzone) physical |= 2;
    if ((physical & 3) == 3) physical &= ~3u;
    if ((physical & 12) == 12) physical &= ~12u;
    return physical;
}

struct ActionPiDirectionBinding {
    // type: 0 absent, 1 button, 2 hat, 3 axis, 4 keyboard.
    SDL_JoystickID device = -1;
    int type = 0, id = -1, value = 0;
    bool valid() const { return type && id >= 0 && (type == 4 || device >= 0); }
    int axis() const {
        SDL_Joystick* joy = SDL_JoystickFromInstanceID(device);
        return joy && id >= 0 && id < SDL_JoystickNumAxes(joy)
            ? SDL_JoystickGetAxis(joy, id) : 0;
    }
    bool pressed() const {
        if (type == 4) {
            const SDL_Scancode scan = SDL_GetScancodeFromKey(id);
            return scan != SDL_SCANCODE_UNKNOWN && SDL_GetKeyboardState(nullptr)[scan];
        }
        SDL_Joystick* joy = SDL_JoystickFromInstanceID(device);
        if (!joy || id < 0) return false;
        if (type == 1) return id < SDL_JoystickNumButtons(joy) && SDL_JoystickGetButton(joy, id);
        if (type == 2) return value && id < SDL_JoystickNumHats(joy) &&
            (SDL_JoystickGetHat(joy, id) & value) == value;
        return type == 3 && axis() * (value < 0 ? -1 : 1) > ACTIONPI_DIGITAL_DEADZONE;
    }
};

class ActionPiDigitalDirections {
    PerPad_struct* pad_ = nullptr;
    std::array<ActionPiDirectionBinding, 4> dpad_;
    ActionPiDirectionBinding x_, y_;
    unsigned held_ = 0;
public:
    void reset() { pad_ = nullptr; held_ = 0; }
    void configure(PerPad_struct* pad, const std::array<ActionPiDirectionBinding, 4>& dirs,
                   ActionPiDirectionBinding x, ActionPiDirectionBinding y) {
        for (const auto& d : dirs) if (!d.valid()) return;
        if (!x.valid() || !y.valid() || x.type != 3 || y.type != 3) return;
        pad_ = pad; dpad_ = dirs; x_ = x; y_ = y; held_ = 0;
        // The merger owns these four Saturn buttons. Raw polling must not
        // release a direction which the other input source still holds.
        const unsigned char names[] = {PERPAD_UP, PERPAD_DOWN, PERPAD_LEFT, PERPAD_RIGHT};
        for (auto name : names) PerSetKey(PERKEY_UNBOUND, name, pad_);
    }
    void update() {
        if (!pad_) return;
        unsigned physical = 0;
        for (unsigned i = 0; i < 4; ++i) if (dpad_[i].pressed()) physical |= 1u << i;
        const unsigned next = actionpiDirectionMask(physical, x_.axis(), y_.axis(),
            x_.value < 0 ? -1 : 1, y_.value < 0 ? -1 : 1, ACTIONPI_DIGITAL_DEADZONE);
        void (*press[])(PerPad_struct*) = {PerPadUpPressed, PerPadDownPressed, PerPadLeftPressed, PerPadRightPressed};
        void (*release[])(PerPad_struct*) = {PerPadUpReleased, PerPadDownReleased, PerPadLeftReleased, PerPadRightReleased};
        for (unsigned i = 0; i < 4; ++i) {
            const unsigned bit = 1u << i;
            if ((next ^ held_) & bit) (next & bit ? press[i] : release[i])(pad_);
        }
        held_ = next;
    }
};
