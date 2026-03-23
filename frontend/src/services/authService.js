import api from '@/lib/axios';

export const authService = {
  register: async (data) => {
    const response = await api.post('/users/register/', data);
    return response.data;
  },

  login: async (data) => {
    const response = await api.post('/users/login/', data);
    return response.data;
  },

  getProfile: async () => {
    const response = await api.get('/users/profile/');
    return response.data;
  },

  updateProfile: async (data) => {
    const response = await api.put('/users/profile/', data);
    return response.data;
  },

  getVerificationStatus: async () => {
    const response = await api.get('/users/verify/');
    return response.data;
  },

  submitVerification: async (formData) => {
    const response = await api.post('/users/verify/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};