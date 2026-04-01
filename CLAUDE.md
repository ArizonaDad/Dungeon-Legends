# Souls MMO - Multiplayer Game Framework

## Project Overview
Clean multiplayer game framework built in **NVGT** (NonVisual Gaming Toolkit, AngelScript-like). Stripped from the Tabletop Tavern platform — all game-specific logic removed, keeping only core infrastructure.

## Architecture
- **Client-server** model using ENet networking with JSON message passing
- **Server** (`Server/`): Authoritative state, SQLite persistence, room/user management
- **Client** (`Client/`): Input handling, TTS output, menu UI, network dispatcher
- **Common** (`common/`): Shared message type constants and utilities

## Key Files
| File | Purpose |
|------|---------|
| `Server/Server.nvgt` | Main server entry, network loop, bot utilities |
| `Server/account.nvgt` | Account persistence (SQLite + JSON data blob) |
| `Server/rooms_Dom.nvgt` | Room/lobby creation and management |
| `Server/users _dom.nvgt` | User class, message handler dispatch |
| `Server/game_manager.nvgt` | Game lifecycle (placeholder) |
| `Client/client.nvgt` | Main client entry, login, lobby menus |
| `Client/net.nvgt` | Network message dispatcher + connection |
| `Client/forms.nvgt` | Form UI utilities |
| `Client/UI.nvgt` | Generic UI helpers |
| `common/message_types.nvgt` | All network message type constants |
| `common/utils.nvgt` | Shared utilities |

## Core Systems Preserved

### Networking
- ENet-based client-server with reliable/unreliable channels
- JSON message passing (`json_object` serialization)
- Connection, disconnection, reconnection handling
- Message dispatch by type string

### Account System
- SQLite database (`Server/data/user.db`)
- Login/signup with password hashing
- Persistent JSON data blob per account
- Credits, XP, level tracking

### Room/Lobby System
- Create rooms with name, password, game type
- Join/leave rooms
- Player list broadcasting
- Host controls (kick, start game)
- Bot management (add/remove AI players)

### Chat & Social
- Room chat (broadcast to room members)
- Private messages / tells
- Friend system (request, accept, decline, remove, list)
- Player reporting
- Game invites
- Online status checking

### User Management
- User class with connection state, room reference, account reference
- Bot user creation with silly generated names
- Status tracking (online, in_game, etc.)

## Message Types (Kept)
- `login`, `signup`, `error`, `announce`, `pop_text`
- `chat_message`, `tell`, `private_message`
- `new_room`, `list_rooms`, `join_room`, `leave_room`, `leave_game`
- `room_players`, `kick_player`, `room_closed`, `start_game`
- `friend_request`, `friend_accept`, `friend_decline`, `friend_remove`, `friend_list`
- `pending_requests`, `check_online`
- `report_player`, `report_confirm`
- `add_bot`, `remove_bot`
- `password_required`, `password_submit`
- `game_invite`, `game_invite_received`, `game_invite_response`

## NVGT Language Notes
- AngelScript-based: `@` = handle (reference), `@obj = null` = null check
- `uint64` for timestamps, `ticks()` returns current time in ms
- `json_object` / `json_array` for serialization
- `speak(text, interrupt)` for TTS (client-side)
- `menu` / `setup_sub_menu(prompt)` for accessible popup menus
- `network.send(peer_id, message, channel, reliable)` for networking
- `wait(ms)` yields execution in game loops

## Development
- Compile: `c:\nvgt\nvgt.exe -c Server/Server.nvgt` and `c:\nvgt\nvgt.exe -c Client/client.nvgt`
- Both server and client compile clean
- Ready for new game logic to be built on top
