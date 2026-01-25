import { request } from "./http";

export async function loginApi(payload) {
  const formData = new URLSearchParams();

  const email = payload.email?.trim();
  const phone = payload.phone?.trim();

  if (email) {
    formData.append("email", email);
  } else if (phone) {
    formData.append("phone", phone);
  }

  formData.append("password", payload.password);

  const res = await request("/auth/login", {
    method: "POST",
    body: formData,
    headers: {},
    credentials: "include",
  });

  return res;
}

export async function logoutApi() {
  return request("/auth/logout", {
    method: "POST",
    credentials: "include", //để nhận refresh_token cookie
  });
}
