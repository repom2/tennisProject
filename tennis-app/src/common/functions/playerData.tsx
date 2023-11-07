import fetch from 'node-fetch';

export async function getData(): Promise<any> {
  const response = await fetch('http://localhost:8000/players', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      // 'Authorization': 'Token ' + token // if you use token authentication
    }
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status} ${response.statusText}`);
  }
  return await response.json();
}