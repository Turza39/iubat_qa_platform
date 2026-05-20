import api from '@/lib/axios'
import { API_BASE_URL } from "./config";

export const authService = {
  register: async (data) => {
    const response = await api.post('${API_BASE_URL}/users/register/', data)
    return response.data
  },

  login: async (data) => {
    const response = await api.post('${API_BASE_URL}/users/login/', data)
    return response.data
  },

  getProfile: async () => {
    const response = await api.get('${API_BASE_URL}/users/profile/')
    return response.data
  },

  updateProfile: async (data) => {
    const response = await api.put('${API_BASE_URL}/users/profile/', data)
    return response.data
  },

  getVerificationStatus: async () => {
    const response = await api.get('${API_BASE_URL}/users/verify/')
    return response.data
  },

  submitVerification: async (formData) => {
    const response = await api.post('${API_BASE_URL}/users/verify/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
}
