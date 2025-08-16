import { useState, useEffect, useCallback } from 'react';
import { Job } from '../types';
import { jobsApi } from '../services/api';

interface UseJobResult {
  job: Job | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export const useJob = (jobId: string | null, pollInterval: number = 2000): UseJobResult => {
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchJob = useCallback(async () => {
    if (!jobId) return;

    try {
      setLoading(true);
      setError(null);
      const response = await jobsApi.get(jobId);
      setJob(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch job status');
    } finally {
      setLoading(false);
    }
  }, [jobId]);

  useEffect(() => {
    if (!jobId) return;

    // Initial fetch
    fetchJob();

    // Set up polling only if job is not completed or failed
    const shouldPoll = job?.status === 'pending' || job?.status === 'running';
    
    if (shouldPoll) {
      const interval = setInterval(fetchJob, pollInterval);
      return () => clearInterval(interval);
    }
  }, [jobId, fetchJob, pollInterval, job?.status]);

  return {
    job,
    loading,
    error,
    refetch: fetchJob,
  };
};