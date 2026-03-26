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

export function searchBookingByCode(bookingCode) {
  return request(`/bookings/search?booking_code=${encodeURIComponent(bookingCode)}`, {
    method: "GET",
  });
}

export function cancelBooking(bookingCode) {
  return request(`/bookings/cancel?booking_code=${encodeURIComponent(bookingCode)}`, {
    method: "DELETE",
  });
}

export function createPayment(payload) {
  return request("/payments", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function searchRooms(checkinDate, checkoutDate, bedType) {
  let url = `/rooms/search?checkin_date=${checkinDate}&checkout_date=${checkoutDate}`;
  if (bedType && bedType !== "ALL") {
    url += `&bed_type=${bedType}`;
  }
  return request(url, { method: "GET" });
}
