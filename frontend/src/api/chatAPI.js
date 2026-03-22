
import axiosClient from "./axiosClient"

export const sendChatMessage = async (message) => {
  const response = await axiosClient.post("/chat", {
    message: message
  })

  return response.data
}