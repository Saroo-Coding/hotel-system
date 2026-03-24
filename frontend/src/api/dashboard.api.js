import { request } from "./http";

export function listRoom() {
  return request("/rooms/list_room", { method: "GET" });
}

export function roomDetail(roomId) {
  return request(`/rooms/room_details?room_id=${roomId}`, { method: "GET" });
}

export function searchGuest(keyword) {
  return request(`/guests/search?keyword=${encodeURIComponent(keyword)}`, {
    method: "GET",
  });
}

export function createGuest(payload) {
  return request("/guests/create", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createBooking(payload) {
  return request("/bookings/bookings", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
