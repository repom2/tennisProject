import axios from 'axios';
import {Players} from "data/openapi";


export async function getData(): Promise<{data: Players[];}> {
  try {
    const response = await axios.get('http://localhost:8000/tennisapi/players/', {
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
