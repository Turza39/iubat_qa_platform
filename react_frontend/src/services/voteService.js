import api from '@/lib/axios'
import { API_BASE_URL } from "./config";

export const voteService = {
  toggleQuestionVote: async (questionId) => {
    const response = await api.post(`${API_BASE_URL}/votes/questions/${questionId}/`)
    return response.data
  },

  toggleAnswerVote: async (answerId) => {
    const response = await api.post(`${API_BASE_URL}/votes/answers/${answerId}/`)
    return response.data
  },
}
