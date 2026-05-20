import api from '@/lib/axios'
import { API_BASE_URL } from "./config";
export const answerService = {
  postAnswer: async (questionId, data) => {
    const response = await api.post(`${API_BASE_URL}/answers/questions/${questionId}/`, data)
    return response.data
  },
}
