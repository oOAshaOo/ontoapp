import axios from "axios";
import { storeToken, storeLoginFormAlert } from "../stores/store";

const BASE_URL = "http://localhost:8000";

let isRefreshing = false;
let refreshPromise = null;

export const addUserApi = async (username, password) => {
  try {
    const response = await axios.post(`${BASE_URL}/user/add`, {
      username,
      password,
    });
    return response;
  } catch (error) {
    throw error;
  }
};

export const loginUserApi = async (username, password) => {
  try {
    const response = await axios.post(`${BASE_URL}/auth/login`, {
      username,
      password,
    });
    return response;
  } catch (error) {
    throw error;
  }
};

export const getUserApi = async (router) => {
  const token = storeToken();
  token.loadTokens();
  try {
    const response = await axios.get(`${BASE_URL}/user/get`, {
      headers: {
        accept: "application/json",
        jasonWebToken: token.accessToken,
      },
    });
    return response;
  } catch (error) {
    if (error.response.status === 403) {
      await refreshAuthTokenApi(router);
      token.loadTokens();
      return getUserApi(router);
    }
    throw error;
  }
};

export const logoutUserApi = async (router) => {
  const token = storeToken();
  token.loadTokens();
  try {
    const response = await axios.post(
      `${BASE_URL}/auth/logout`,
      {},
      {
        headers: {
          accept: "application/json",
          jasonWebToken: token.accessToken,
        },
      },
    );
    return response;
  } catch (error) {
    if (error.response.status === 403) {
      await refreshAuthTokenApi(router);
      token.loadTokens();

      return logoutUserApi(router);
    }
    throw error;
  }
};

export const deleteUserApi = async (password, router) => {
  const token = storeToken();
  token.loadTokens();
  try {
    const response = await axios.delete(`${BASE_URL}/user/delete`, {
      headers: {
        accept: "application/json",
        jasonWebToken: token.accessToken,
        "Content-Type": "application/json",
      },
      data: {
        password: password,
      },
    });
    return response;
  } catch (error) {
    if (error.response.status === 403) {
      await refreshAuthTokenApi(router);
      token.loadTokens();
      return deleteUserApi(password, router);
    }
    throw error;
  }
};

export const addTaxonomyApi = async (domain, description, router) => {
  const token = storeToken();
  token.loadTokens();
  try {
    const response = await axios.post(
      `${BASE_URL}/taxonomie/add`,
      {
        domain,
        description,
      },
      {
        headers: {
          accept: "application/json",
          jasonWebToken: token.accessToken,
          "Content-Type": "application/json",
        },
      },
    );
    return response;
  } catch (error) {
    if (error.response.status === 403) {
      await refreshAuthTokenApi(router);
      token.loadTokens();
      return addTaxonomyApi(domain, description, router);
    }
    throw error;
  }
};

export const getTaxonomyApi = async (taxonomy, router) => {
  const token = storeToken();
  token.loadTokens();
  try {
    const response = await axios.get(`${BASE_URL}/taxonomie/get`, {
      headers: {
        accept: "application/json",
        jasonWebToken: token.accessToken,
      },
      params: {
        taxonomie_id: taxonomy,
      },
    });
    return response;
  } catch (error) {
    if (error.response.status === 403) {
      await refreshAuthTokenApi(router);
      token.loadTokens();
      return getTaxonomyApi(taxonomy, router);
    }
    throw error;
  }
};

export const deleteTaxonomyApi = async (taxonomyId, password, router) => {
  const token = storeToken();
  token.loadTokens();
  try {
    const response = await axios.delete(`${BASE_URL}/taxonomie/delete`, {
      headers: {
        accept: "application/json",
        jasonWebToken: token.accessToken,
        "Content-Type": "application/json",
      },
      data: {
        id: parseInt(taxonomyId),
        password: password,
      },
    });
    return response;
  } catch (error) {
    if (error.response.status === 403) {
      await refreshAuthTokenApi(router);
      token.loadTokens();
      return deleteTaxonomyApi(taxonomyId, password, router);
    }
    throw error;
  }
};

export const saveTaxonomyApi = async (data, router) => {
  const token = storeToken();
  token.loadTokens();
  try {
    const response = await axios.put(`${BASE_URL}/taxonomie/save`, data, {
      headers: {
        accept: "application/json",
        jasonWebToken: token.accessToken,
        "Content-Type": "application/json",
      },
    });
    return response;
  } catch (error) {
    if (error.response.status === 403) {
      await refreshAuthTokenApi(router);
      token.loadTokens();
      return saveTaxonomyApi(data, router);
    }
    throw error;
  }
};

export const generateTaxonomyApi = async (data, router) => {
  const token = storeToken();
  token.loadTokens();
  try {
    const response = await axios.post(`${BASE_URL}/taxonomie/generate`, data, {
      headers: {
        accept: "application/json",
        jasonWebToken: token.accessToken,
        "Content-Type": "application/json",
      },
    });
    return response;
  } catch (error) {
    if (error.response.status === 403) {
      await refreshAuthTokenApi(router);
      token.loadTokens();
      return generateTaxonomyApi(data, router);
    }
    throw error;
  }
};

export const refreshAuthTokenApi = async (router) => {
  if (isRefreshing) {
    return refreshPromise;
  }
  isRefreshing = true;
  const token = storeToken();
  token.loadTokens();
  try {
    refreshPromise = axios.post(
      `${BASE_URL}/auth/refresh`,
      { refresh_token: token.refreshToken },
      {
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
      },
    );
    const response = await refreshPromise;
    if (response.status === 200) {
      token.setTokens(response.data.access_token, response.data.refresh_token);
    }
  } catch (error) {
    const status = error.response?.status;
    if (status === 403 || status === 400) {
      token.clearTokens();
      const loginFormAlert = storeLoginFormAlert();
      loginFormAlert.setStatusMessage("Session expired. Please login again");
      loginFormAlert.setStatusType("error");
      router.push("/");
      return refreshPromise;
    }
  } finally {
    isRefreshing = false;
    refreshPromise = null;
  }

  return refreshPromise;
};
