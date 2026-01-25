import { request } from "./http";

export function userApi() {
  return request("/users/me", { method: "GET" });
}
