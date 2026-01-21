const BASE_URL = 'http://127.0.0.1:8000/api/v1'

export async function request(url, options = {}) {
  const token = localStorage.getItem('token')

  const res = await fetch(BASE_URL + url, {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    },
    ...options
  })

  const data = await res.json()

  if (!res.ok) {
    throw data
  }

  return data
}
