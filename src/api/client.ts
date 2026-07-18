
Input
import axios, { AxiosInstance } from "axios"

const client: AxiosInstance = axios.create({
  baseURL: "http://127.0.0.1:37210/api/v1",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
})

client.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error.code === "ECONNREFUSED" || error.code === "ERR_NETWORK") {
      console.error("[API] Backend not available")
    }
    return Promise.reject(error)
  }
)

export const api = {
  get:    async <T>(url: string, params?: object) =>
            (await client.get<T>(url, { params })).data,
  post:   async <T>(url: string, data?: object) =>
            (await client.post<T>(url, data)).data,
  put:    async <T>(url: string, data?: object) =>
            (await client.put<T>(url, data)).data,
  patch:  async <T>(url: string, data?: object) =>
            (await client.patch<T>(url, data)).data,
  delete: async <T>(url: string) =>
            (await client.delete<T>(url)).data,
  upload: async <T>(url: string, file: File, extra?: object) => {
    const fd = new FormData()
    fd.append("file", file)
    if (extra) Object.entries(extra).forEach(([k, v]) => fd.append(k, String(v)))
    return (await client.post<T>(url, fd, {
      headers: { "Content-Type": "multipart/form-data" }
    })).data
  },
  checkHealth: async (): Promise<boolean> => {
    try {
      await axios.get("http://127.0.0.1:37210/health", { timeout: 3000 })
      return true
    } catch { return false }
  },
}

export default client
