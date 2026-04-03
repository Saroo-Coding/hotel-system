import { request } from "./http";

export function listRoom() {
  return request("/rooms/list_room", { method: "GET" });
}

export function listAdminRooms(params = {}) {
  const searchParams = new URLSearchParams();
  if (params.hotelId) searchParams.set("hotel_id", params.hotelId);
  if (params.bedType && params.bedType !== "ALL") searchParams.set("bed_type", params.bedType);
  if (params.statusRoom && params.statusRoom !== "ALL") searchParams.set("status_room", params.statusRoom);
  if (params.keyword) searchParams.set("keyword", params.keyword.trim());

  const query = searchParams.toString();
  const url = query ? `/rooms/list_room?${query}` : "/rooms/list_room";
  return request(url, { method: "GET" });
}

export function createAdminRoom(payload) {
  return request("/rooms/admin/create", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateAdminRoom(roomId, payload) {
  return request(`/rooms/manager/update?room_id=${roomId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function setRoomMaintenance(roomId) {
  return request(`/rooms/manager/room_maintenance?room_id=${roomId}`, {
    method: "PATCH",
  });
}

export function setRoomAvailable(roomId) {
  return request(`/rooms/manager/room_available?room_id=${roomId}`, {
    method: "PATCH",
  });
}

export function roomDetail(roomId) {
  return request(`/rooms/room_details?room_id=${roomId}`, { method: "GET" });
}

export function searchGuest(keyword) {
  return request(`/guests/search?keyword=${encodeURIComponent(keyword)}`, {
    method: "GET",
  });
}

export function listAdminGuests(params = {}) {
  const searchParams = new URLSearchParams();
  searchParams.set("page", String(params.page || 1));
  searchParams.set("limit", String(params.limit || 100));
  if (params.keyword) searchParams.set("keyword", params.keyword.trim());
  return request(`/guests/manager/list_guest?${searchParams.toString()}`, { method: "GET" });
}

export function getAdminGuestDetail(guestId) {
  return request(`/guests/manager/details?guest_id=${guestId}`, { method: "GET" });
}

export function updateAdminGuest(guestId, payload) {
  return request(`/guests/manager/update?guest_id=${guestId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteAdminGuest(guestId) {
  return request(`/guests/manager/delete?guest_id=${guestId}`, { method: "DELETE" });
}

export function restoreAdminGuest(guestId) {
  return request(`/guests/admin/restore?guest_id=${guestId}`, { method: "PATCH" });
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

export function listHotels() {
  return request("/hotels/list_hotels", { method: "GET" });
}

export function listAdminUsers(params = {}) {
  const searchParams = new URLSearchParams();
  searchParams.set("page", String(params.page || 1));
  searchParams.set("limit", String(params.limit || 100));
  if (params.role) searchParams.set("role", params.role);
  if (params.statusUser) searchParams.set("status_user", params.statusUser);
  if (params.keyword) searchParams.set("keyword", params.keyword.trim());
  return request(`/users/manager/list?${searchParams.toString()}`, { method: "GET" });
}

export function getAdminUserDetail(userId) {
  return request(`/users/manager/details?user_id=${userId}`, { method: "GET" });
}

export function createAdminUser(payload) {
  return request("/users/admin/create", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateAdminUser(userId, payload) {
  return request(`/users/manager/update?user_id=${userId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function changeAdminUserStatus(userId, userStatus) {
  return request(`/users/manager/status?user_id=${userId}&user_status=${userStatus}`, {
    method: "PATCH",
  });
}

export function deactivateHotel(hotelId) {
  return request(`/hotels/admin/deactivate?hotel_id=${hotelId}`, { method: "PATCH" });
}

export function activateHotel(hotelId) {
  return request(`/hotels/admin/activate?hotel_id=${hotelId}`, { method: "PATCH" });
}

export function searchRooms(checkinDate, checkoutDate, bedType) {
  let url = `/rooms/search?checkin_date=${checkinDate}&checkout_date=${checkoutDate}`;
  if (bedType && bedType !== "ALL") {
    url += `&bed_type=${bedType}`;
  }
  return request(url, { method: "GET" });
}
