import api from '@/lib/axios'
import { API_BASE_URL } from "./config";

export const questionService = {
  getAllQuestions: async (search = '', tag = '', skip = 0, limit = 20) => {
    const params = { skip, limit }
    if (search) params.search = search
    if (tag) params.tag = tag
    const response = await api.get('${API_BASE_URL}/questions/', { params })
    return response.data
  },

  getQuestionDetail: async (id, skip = 0, limit = 5) => {
    const params = { skip, limit }
    const response = await api.get(`${API_BASE_URL}/questions/${id}/`, { params })
    return response.data
  },

  createQuestion: async (data) => {
    const response = await api.post('${API_BASE_URL}/questions/', data)
    return response.data
  },

  getAllTags: async () => {
    const response = await api.get('${API_BASE_URL}/questions/tags/')
    return response.data
  },
}
