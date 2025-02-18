class DataService {
  static BASE_URL = "http://localhost:5000";
  static POLLING_INTERVAL = 1000; // 1 second interval

  static async fetchData(endpoint) {
    try {
      const response = await fetch(`${this.BASE_URL}${endpoint}`);
      if (!response.ok) throw new Error("Network response was not ok");
      return await response.json();
    } catch (error) {
      console.error(`Error fetching from ${endpoint}:`, error);
      throw error;
    }
  }
}

export default DataService;
