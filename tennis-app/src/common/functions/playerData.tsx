import axios from 'axios';
import {EloRatings} from "data/openapi";


export async function getData(): Promise<{data: EloRatings[];}> {
  try {
    const response = await axios.get('http://localhost:8000/tennisapi/atp-elo/', {
    method: 'get',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    return response;
  } catch (error) {
    if (error instanceof axios.AxiosError) {
      throw new Error(`HTTP ${error}`);
    }
    throw error;
  }
}
