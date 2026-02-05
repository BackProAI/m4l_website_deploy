'use client';

import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';

export default function BackendWarmup() {
  const [isWarming, setIsWarming] = useState(true);

  useEffect(() => {
    const warmupBackend = async () => {
      const API_BASE = process.env.NEXT_PUBLIC_A3_API || '';
      if (!API_BASE) {
        setIsWarming(false);
        return;
      }

      const toastId = toast.loading('🔥 Waking up backend server...', {
        duration: Infinity,
      });

      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout

        const response = await fetch(API_BASE, {
          signal: controller.signal,
          cache: 'no-store',
        });

        clearTimeout(timeoutId);

        if (response.ok) {
          toast.success('✅ Backend ready!', { id: toastId, duration: 2000 });
        } else {
          toast.dismiss(toastId);
          console.warn('Backend warmup returned non-OK status:', response.status);
        }
      } catch (error) {
        // If it times out or fails, just dismiss silently - backend might still be starting
        toast.dismiss(toastId);
        console.warn('Backend warmup error (backend may still be starting):', error);
      } finally {
        setIsWarming(false);
      }
    };

    warmupBackend();
  }, []);

  return null; // This component doesn't render anything
}
