import { useEffect, useMemo, useState } from 'react';
import { createClient } from '@supabase/supabase-js';

type SessionPresenceProps = {
  sessionId: string;
};

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

const supabase = createClient(supabaseUrl, supabaseAnonKey);

export function SessionPresence({ sessionId }: SessionPresenceProps) {
  const [listenerCount, setListenerCount] = useState(1);

  const listenerId = useMemo(() => crypto.randomUUID(), []);

  useEffect(() => {
    const channel = supabase.channel(`session:${sessionId}`, {
      config: {
        presence: {
          key: listenerId,
        },
      },
    });

    channel
      .on('presence', { event: 'sync' }, () => {
        const state = channel.presenceState();
        const count = Object.keys(state).length;
        setListenerCount(count);
      })
      .subscribe(async (status) => {
        if (status === 'SUBSCRIBED') {
          await channel.track({
            listenerId,
            joinedAt: new Date().toISOString(),
          });
        }
      });

    return () => {
      channel.unsubscribe();
    };
  }, [sessionId, listenerId]);

  return (
    <p>
      {listenerCount === 1
        ? 'Listening alone'
        : `${listenerCount} listeners connected`}
    </p>
  );
}