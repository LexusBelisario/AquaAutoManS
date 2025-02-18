import { useState, useEffect, useCallback } from "react";
import DataService from "../services/DataService";

export function useRealtimeData(endpoint, initialValue = null) {
  const [data, setData] = useState(initialValue);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const result = await DataService.fetchData(endpoint);
      setData(result);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [endpoint]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, DataService.POLLING_INTERVAL);
    return () => clearInterval(interval);
  }, [fetchData]);

  return { data, error, loading, refetch: fetchData };
}
