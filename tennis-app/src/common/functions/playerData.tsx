import axios from 'axios';

export async function getData(): Promise<any> {
  try {
    const response = await axios.get('http://localhost:8000/tennisapi/players', {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
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
