import { request } from "./http";

export function listRoom() {
  return request("/rooms/list_room", { method: "GET" });
}
