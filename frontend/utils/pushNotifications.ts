import { Platform } from 'react-native';
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import Constants from 'expo-constants';
import { apiCall } from './api';

// Configure notification behavior
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export async function registerForPushNotifications(): Promise<string | null> {
  if (!Device.isDevice) {
    console.log('Push notifications require a physical device');
    return null;
  }

  // Check existing permissions
  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') {
    console.log('Push notification permission denied');
    return null;
  }

  // Get push token
  try {
    const projectId = Constants.expoConfig?.extra?.eas?.projectId;
    const tokenData = await Notifications.getExpoPushTokenAsync({
      projectId: projectId || undefined,
    });
    const token = tokenData.data;
    console.log('Push token:', token);

    // Register token with backend
    try {
      await apiCall('/api/push/register', {
        method: 'POST',
        body: JSON.stringify({ push_token: token, platform: Platform.OS }),
      });
    } catch (e) {
      console.log('Failed to register push token with backend:', e);
    }

    return token;
  } catch (e) {
    console.log('Failed to get push token:', e);
    return null;
  }
}

// Schedule a local notification
export async function scheduleLocalNotification(title: string, body: string, seconds: number = 1) {
  await Notifications.scheduleNotificationAsync({
    content: { title, body, sound: true },
    trigger: seconds > 0 ? { seconds, type: Notifications.SchedulableTriggerInputTypes.TIME_INTERVAL } : null,
  });
}

// Listen for notifications
export function addNotificationListener(callback: (notification: Notifications.Notification) => void) {
  return Notifications.addNotificationReceivedListener(callback);
}

export function addNotificationResponseListener(callback: (response: Notifications.NotificationResponse) => void) {
  return Notifications.addNotificationResponseReceivedListener(callback);
}
