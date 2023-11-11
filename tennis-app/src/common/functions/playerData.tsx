import axios from 'axios';

export async function getData(): Promise<any> {
  try {
    const response = await axios.get('http://localhost:8000/tennisapi/players/', {
    method: 'get',
      headers: {
        'Content-Type': 'application/json',
        //'Access-Control-Allow-Origin' : '*',
        //'Access-Control-Allow-Methods':'GET,HEAD,OPTIONS',
        //'Vary':'Accept',
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
