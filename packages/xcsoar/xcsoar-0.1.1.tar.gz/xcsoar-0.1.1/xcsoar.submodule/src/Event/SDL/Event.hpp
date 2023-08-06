/*
Copyright_License {

  XCSoar Glide Computer - http://www.xcsoar.org/
  Copyright (C) 2000-2013 The XCSoar Project
  A detailed list of copyright holders can be found in the file "AUTHORS".

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
}
*/

#ifndef XCSOAR_EVENT_SDL_HPP
#define XCSOAR_EVENT_SDL_HPP

#include <SDL_version.h>
#include <SDL_events.h>

#include <assert.h>

enum {
  /**
   * A "user" event for a #Window.
   */
  EVENT_USER = SDL_USEREVENT,

  /**
   * A function pointer with a pointer argument gets called.
   */
  EVENT_CALLBACK,
};

struct Event {
  SDL_Event event;

  bool IsKeyDown() const {
    return event.type == SDL_KEYDOWN;
  }

  bool IsKey() const {
    return IsKeyDown() || event.type == SDL_KEYUP;
  }

  unsigned GetKeyCode() const {
    assert(IsKey());

    return event.key.keysym.sym;
  }

  bool IsCharacter() const {
    return IsKeyDown() && event.key.keysym.unicode != 0;
  }

  unsigned GetCharacter() const {
    assert(IsCharacter());

    return event.key.keysym.unicode;
  }

  bool IsMouseDown() const {
    return event.type == SDL_MOUSEBUTTONDOWN;
  }

  bool IsMouse() const {
    return IsMouseDown() || event.type == SDL_MOUSEBUTTONUP ||
      event.type == SDL_MOUSEMOTION;
  }

  bool IsUserInput() const {
    return IsKey() || IsMouse();
  }
};

#endif
