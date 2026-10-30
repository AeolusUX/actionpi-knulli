// Host-side input behavior check; does not launch an emulator or touch the device.
#include <cassert>
#include <cstdio>
#include <cstdint>
using SDL_JoystickID = int;
using SDL_Scancode = int;
static const int SDL_SCANCODE_UNKNOWN = 0;
struct SDL_Joystick { int axes[2] = {}; unsigned char hats[1] = {}; unsigned char buttons[12] = {}; } joystick;
bool attached = true;
SDL_Joystick* SDL_JoystickFromInstanceID(int id) { return attached && id == 0 ? &joystick : nullptr; }
int SDL_JoystickNumAxes(SDL_Joystick*) { return 2; }
int SDL_JoystickNumHats(SDL_Joystick*) { return 1; }
int SDL_JoystickNumButtons(SDL_Joystick*) { return 12; }
int SDL_JoystickGetAxis(SDL_Joystick* j,int i) { return j->axes[i]; }
int SDL_JoystickGetHat(SDL_Joystick* j,int i) { return j->hats[i]; }
int SDL_JoystickGetButton(SDL_Joystick* j,int i) { return j->buttons[i]; }
SDL_Scancode SDL_GetScancodeFromKey(int key) { return key < 512 ? key : 0; }
const unsigned char* SDL_GetKeyboardState(void*) { static unsigned char state[512] = {}; return state; }
struct PerPad_struct { unsigned state = 0x100; } pad;
enum { PERPAD_UP, PERPAD_RIGHT, PERPAD_DOWN, PERPAD_LEFT };
static const unsigned PERKEY_UNBOUND = 0xffffffffu;
unsigned unbound = 0, transitions = 0;
void PerSetKey(unsigned key,unsigned char,void* p) { assert(key == PERKEY_UNBOUND && p == &pad); ++unbound; }
#define DIR_FUNCS(name,mask) \
void PerPad##name##Pressed(PerPad_struct* p) { p->state |= mask; ++transitions; } \
void PerPad##name##Released(PerPad_struct* p) { p->state &= ~mask; ++transitions; }
DIR_FUNCS(Up,1u) DIR_FUNCS(Down,2u) DIR_FUNCS(Left,4u) DIR_FUNCS(Right,8u)
#include "actionpi_digital_directions.h"
ActionPiDirectionBinding bind(int type,int id,int value) {
    ActionPiDirectionBinding b;b.device=0;b.type=type;b.id=id;b.value=value;return b;
}
int main() {
    ActionPiDigitalDirections input;
    std::array<ActionPiDirectionBinding,4> dirs={{bind(2,0,1),bind(2,0,4),bind(2,0,8),bind(2,0,2)}};
    input.configure(&pad,dirs,bind(3,0,-1),bind(3,1,-1));assert(unbound==4);
    input.update();assert(pad.state==0x100);
    joystick.axes[0]=-26000;input.update();assert(pad.state==0x104);
    joystick.hats[0]=8;input.update();assert(pad.state==0x104 && transitions==1);
    joystick.axes[0]=0;input.update();assert(pad.state==0x104 && transitions==1);
    joystick.axes[0]=-26000;joystick.hats[0]=0;input.update();assert(pad.state==0x104 && transitions==1);
    joystick.axes[1]=-26000;input.update();assert(pad.state==0x105);
    joystick.hats[0]=2;input.update();assert(pad.state==0x101); // opposite sources cancel
    joystick.hats[0]=0;input.update();assert(pad.state==0x105);
    joystick.axes[0]=joystick.axes[1]=0;joystick.hats[0]=4;input.update();assert(pad.state==0x102);
    joystick.hats[0]=0;input.update();assert(pad.state==0x100);
    joystick.axes[0]=10000;joystick.axes[1]=-10000;input.update();assert(pad.state==0x100);
    input.configure(&pad,dirs,bind(3,0,1),bind(3,1,-1));
    joystick.axes[0]=26000;joystick.axes[1]=0;input.update();assert(pad.state==0x104);
    attached=false;input.update();assert(pad.state==0x100); // disconnect releases held direction
    input.reset();attached=true;const unsigned count=transitions;input.update();assert(transitions==count);
    puts("PASS: D-pad/stick merge, release ordering, diagonals, opposites, deadzone, inversion, disconnect, START preservation, analog bypass");
}
