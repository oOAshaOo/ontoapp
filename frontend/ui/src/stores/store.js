import { defineStore } from "pinia";
import { ref } from "vue";

export const storeLoginFormAlert = defineStore("storeLoginFormAlert", () => {
  const statusMessage = ref("");
  const statusType = ref("");

  const setStatusMessage = (message) => {
    statusMessage.value = message;
  };

  const setStatusType = (type) => {
    statusType.value = type;
  };

  return {
    statusMessage,
    statusType,
    setStatusMessage,
    setStatusType,
  };
});

export const storeToken = defineStore("storeToken", () => {
  const accessToken = ref(null);
  const refreshToken = ref(null);

  const setTokens = (newAccessToken, newRefreshToken) => {
    accessToken.value = newAccessToken;
    refreshToken.value = newRefreshToken;
    sessionStorage.setItem("access_token", newAccessToken);
    sessionStorage.setItem("refresh_token", newRefreshToken);
  };

  const loadTokens = () => {
    accessToken.value = sessionStorage.getItem("access_token");
    refreshToken.value = sessionStorage.getItem("refresh_token");
  };

  const clearTokens = () => {
    accessToken.value = null;
    refreshToken.value = null;
    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("refresh_token");
  };

  return {
    accessToken,
    refreshToken,
    setTokens,
    loadTokens,
    clearTokens,
  };
});
