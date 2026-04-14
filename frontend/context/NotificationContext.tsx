import React, { createContext, useContext, useState, useCallback, useRef } from 'react';
import { View, Text, StyleSheet, Animated, Dimensions } from 'react-native';

const { width: SW } = Dimensions.get('window');

interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'success' | 'warning' | 'error' | 'achievement' | 'drop' | 'levelup';
  icon?: string;
  duration?: number;
}

interface NotificationContextType {
  showNotification: (notif: Omit<Notification, 'id'>) => void;
}

const NotificationContext = createContext<NotificationContextType>({
  showNotification: () => {},
});

const TYPE_STYLES: Record<string, { bg: string; border: string; iconDefault: string }> = {
  success: { bg: 'rgba(68,204,68,0.15)', border: '#44cc44', iconDefault: '\u2705' },
  warning: { bg: 'rgba(255,215,0,0.15)', border: '#ffd700', iconDefault: '\u26A0\uFE0F' },
  error: { bg: 'rgba(255,68,68,0.15)', border: '#ff4444', iconDefault: '\u274C' },
  achievement: { bg: 'rgba(255,215,0,0.20)', border: '#ffd700', iconDefault: '\u2B50' },
  drop: { bg: 'rgba(153,68,255,0.15)', border: '#9944ff', iconDefault: '\u2728' },
  levelup: { bg: 'rgba(68,204,68,0.20)', border: '#44cc44', iconDefault: '\u26A1' },
};

export function NotificationProvider({ children }: { children: React.ReactNode }) {
  const [notifications, setNotifications] = useState<(Notification & { anim: Animated.Value })[]>([]);
  const counterRef = useRef(0);

  const showNotification = useCallback((notif: Omit<Notification, 'id'>) => {
    const id = `notif_${++counterRef.current}_${Date.now()}`;
    const anim = new Animated.Value(0);
    const duration = notif.duration || 3000;

    const newNotif = { ...notif, id, anim };
    setNotifications(prev => [...prev.slice(-3), newNotif]);

    Animated.spring(anim, { toValue: 1, useNativeDriver: true, tension: 80, friction: 10 }).start();

    setTimeout(() => {
      Animated.timing(anim, { toValue: 0, duration: 300, useNativeDriver: true }).start(() => {
        setNotifications(prev => prev.filter(n => n.id !== id));
      });
    }, duration);
  }, []);

  return (
    <NotificationContext.Provider value={{ showNotification }}>
      {children}
      <View style={styles.container} pointerEvents="none">
        {notifications.map((notif) => {
          const typeStyle = TYPE_STYLES[notif.type] || TYPE_STYLES.success;
          return (
            <Animated.View
              key={notif.id}
              style={[
                styles.toast,
                {
                  backgroundColor: typeStyle.bg,
                  borderColor: typeStyle.border,
                  transform: [
                    { translateY: notif.anim.interpolate({ inputRange: [0, 1], outputRange: [-60, 0] }) },
                    { scale: notif.anim.interpolate({ inputRange: [0, 0.5, 1], outputRange: [0.8, 1.05, 1] }) },
                  ],
                  opacity: notif.anim,
                },
              ]}
            >
              <Text style={styles.toastIcon}>{notif.icon || typeStyle.iconDefault}</Text>
              <View style={styles.toastContent}>
                <Text style={[styles.toastTitle, { color: typeStyle.border }]}>{notif.title}</Text>
                <Text style={styles.toastMsg} numberOfLines={2}>{notif.message}</Text>
              </View>
            </Animated.View>
          );
        })}
      </View>
    </NotificationContext.Provider>
  );
}

export const useNotification = () => useContext(NotificationContext);

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 4,
    left: 0,
    right: 0,
    alignItems: 'center',
    zIndex: 9999,
    gap: 4,
  },
  toast: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 10,
    borderWidth: 1.5,
    maxWidth: SW * 0.85,
    minWidth: SW * 0.5,
    gap: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
  },
  toastIcon: { fontSize: 20 },
  toastContent: { flex: 1 },
  toastTitle: { fontSize: 11, fontWeight: '900', letterSpacing: 0.5 },
  toastMsg: { color: '#ccc', fontSize: 9, marginTop: 1 },
});
