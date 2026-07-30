const API_BASE_URL = 'http://127.0.0.1:8000';

export const getBackendMessage = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching from backend:', error);
    throw error;
  }
};
