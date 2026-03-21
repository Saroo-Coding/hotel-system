import { request } from "./http";

export function listRoom() {
  return request("/rooms/list_room", { method: "GET" });
}

export function roomDetail(roomId) {
  return request(`/rooms/room_details?room_id=${roomId}`, { method: "GET" });
}
