import axios, { AxiosError, type AxiosRequestConfig } from "axios";

import type { ApiResponse } from "../types";

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL;

export class ApiError extends Error {
  code: number;

  constructor(message: string, code = 1) {
    super(message);
    this.name = "ApiError";
    this.code = code;
  }
}

export const httpClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
});

export async function request<T>(config: AxiosRequestConfig): Promise<T> {
  try {
    const response = await httpClient.request<ApiResponse<T>>(config);
    const payload = response.data;

    if (payload.code !== 0) {
      throw new ApiError(payload.message, payload.code);
    }

    if (payload.data === null) {
      throw new ApiError("response data is empty", payload.code);
    }

    return payload.data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof AxiosError) {
      const payload = error.response?.data as ApiResponse<null> | undefined;
      if (payload?.message) {
        throw new ApiError(payload.message, payload.code ?? 1);
      }

      throw new ApiError(error.message || "request failed");
    }

    if (error instanceof Error) {
      throw new ApiError(error.message);
    }

    throw new ApiError("unknown request error");
  }
}
