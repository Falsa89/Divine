import React, { useState, useEffect } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  KeyboardAvoidingView, Platform, ActivityIndicator, Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Animated, {
  useSharedValue, useAnimatedStyle, withRepeat, withSequence,
  withTiming, Easing, FadeIn, FadeInDown, FadeInUp,
} from 'react-native-reanimated';
import { useRouter } from 'expo-router';
import { useAuth } from '../context/AuthContext';
import { COLORS } from '../constants/theme';

const { width, height } = Dimensions.get('window');

export default function LoginScreen() {
  const { login, register, loading, user } = useAuth();
  const router = useRouter();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Animations
  const glowPulse = useSharedValue(0.4);
  const floatY = useSharedValue(0);
  const shimmer = useSharedValue(0);

  useEffect(() => {
    glowPulse.value = withRepeat(
      withSequence(
        withTiming(1, { duration: 2000, easing: Easing.inOut(Easing.ease) }),
        withTiming(0.4, { duration: 2000, easing: Easing.inOut(Easing.ease) }),
      ), -1, true
    );
    floatY.value = withRepeat(
      withSequence(
        withTiming(-8, { duration: 3000, easing: Easing.inOut(Easing.ease) }),
        withTiming(8, { duration: 3000, easing: Easing.inOut(Easing.ease) }),
      ), -1, true
    );
    shimmer.value = withRepeat(
      withTiming(1, { duration: 4000, easing: Easing.linear }),
      -1
    );
  }, []);

  const glowStyle = useAnimatedStyle(() => ({
    opacity: glowPulse.value,
    transform: [{ scale: 0.9 + glowPulse.value * 0.2 }],
  }));

  const floatStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: floatY.value }],
  }));

  React.useEffect(() => {
    if (!loading && user) {
      router.replace('/(tabs)/home');
    }
  }, [loading, user]);

  if (loading) {
    return (
      <LinearGradient colors={[COLORS.bgPrimary, '#0A0A2E', COLORS.bgPrimary]} style={styles.container}>
        <ActivityIndicator size="large" color={COLORS.accent} />
        <Text style={styles.loadingText}>Caricamento...</Text>
      </LinearGradient>
    );
  }

  const handleSubmit = async () => {
    if (!email || !password) { setError('Compila tutti i campi!'); return; }
    setError(''); setSubmitting(true);
    try {
      if (isLogin) { await login(email, password); }
      else { await register(email, password, username); }
      router.replace('/(tabs)/home');
    } catch (e: any) { setError(e.message || 'Errore'); }
    finally { setSubmitting(false); }
  };

  return (
    <LinearGradient
      colors={[COLORS.bgPrimary, '#0D0D35', '#150828', COLORS.bgPrimary]}
      style={styles.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
    >
      <KeyboardAvoidingView
        style={styles.inner}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        {/* Decorative orbs */}
        <Animated.View style={[styles.orb, styles.orb1, glowStyle]} />
        <Animated.View style={[styles.orb, styles.orb2, glowStyle]} />
        <Animated.View style={[styles.orb, styles.orb3, glowStyle]} />

        {/* Logo */}
        <Animated.View style={[styles.logoContainer, floatStyle]}>
          <Animated.View entering={FadeInDown.duration(800)}>
            <Text style={styles.logoText}>DIVINE</Text>
          </Animated.View>
          <Animated.View entering={FadeInUp.duration(800).delay(200)}>
            <Text style={styles.logoSubtext}>WAIFUS</Text>
          </Animated.View>
          <Animated.View entering={FadeIn.duration(600).delay(500)}>
            <View style={styles.taglineWrap}>
              <View style={styles.taglineLine} />
              <Text style={styles.tagline}>IDLE AUTO-BATTLE RPG</Text>
              <View style={styles.taglineLine} />
            </View>
          </Animated.View>
        </Animated.View>

        {/* Form */}
        <Animated.View entering={FadeInDown.duration(600).delay(300)} style={styles.formOuter}>
          <LinearGradient
            colors={['rgba(20, 20, 60, 0.8)', 'rgba(10, 10, 40, 0.9)']}
            style={styles.formContainer}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
          >
            <Text style={styles.formTitle}>
              {isLogin ? 'Accedi' : 'Registrati'}
            </Text>

            {!isLogin && (
              <View style={styles.inputWrap}>
                <Text style={styles.inputLabel}>USERNAME</Text>
                <TextInput
                  style={styles.input}
                  placeholder="Il tuo nome di battaglia"
                  placeholderTextColor="#4A4A6A"
                  value={username}
                  onChangeText={setUsername}
                  autoCapitalize="none"
                />
              </View>
            )}

            <View style={styles.inputWrap}>
              <Text style={styles.inputLabel}>EMAIL</Text>
              <TextInput
                style={styles.input}
                placeholder="La tua email"
                placeholderTextColor="#4A4A6A"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
              />
            </View>

            <View style={styles.inputWrap}>
              <Text style={styles.inputLabel}>PASSWORD</Text>
              <TextInput
                style={styles.input}
                placeholder="La tua password"
                placeholderTextColor="#4A4A6A"
                value={password}
                onChangeText={setPassword}
                secureTextEntry
              />
            </View>

            {error ? (
              <View style={styles.errorWrap}>
                <Text style={styles.errorText}>{error}</Text>
              </View>
            ) : null}

            <TouchableOpacity
              style={[styles.submitBtn, submitting && styles.btnDisabled]}
              onPress={handleSubmit}
              disabled={submitting}
              activeOpacity={0.8}
            >
              <LinearGradient
                colors={[COLORS.accent, '#FF4444']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={styles.submitGradient}
              >
                {submitting ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <Text style={styles.submitText}>
                    {isLogin ? 'ENTRA NEL GIOCO' : 'CREA ACCOUNT'}
                  </Text>
                )}
              </LinearGradient>
            </TouchableOpacity>

            <TouchableOpacity onPress={() => { setIsLogin(!isLogin); setError(''); }}>
              <Text style={styles.switchText}>
                {isLogin ? 'Non hai un account? ' : 'Hai gia un account? '}
                <Text style={styles.switchHighlight}>
                  {isLogin ? 'Registrati' : 'Accedi'}
                </Text>
              </Text>
            </TouchableOpacity>
          </LinearGradient>
        </Animated.View>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  inner: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 40,
  },
  loadingText: {
    color: COLORS.textSecondary,
    fontSize: 16,
    marginTop: 16,
  },
  // Decorative orbs
  orb: {
    position: 'absolute',
    borderRadius: 200,
  },
  orb1: {
    width: 200,
    height: 200,
    backgroundColor: 'rgba(255, 107, 53, 0.08)',
    top: -40,
    left: -60,
  },
  orb2: {
    width: 150,
    height: 150,
    backgroundColor: 'rgba(136, 68, 255, 0.06)',
    bottom: -30,
    right: -40,
  },
  orb3: {
    width: 100,
    height: 100,
    backgroundColor: 'rgba(255, 215, 0, 0.05)',
    top: '40%',
    right: '30%',
  },
  // Logo
  logoContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoText: {
    fontSize: 48,
    fontWeight: '900',
    color: COLORS.accent,
    letterSpacing: 10,
    textShadowColor: 'rgba(255, 107, 53, 0.6)',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 30,
  },
  logoSubtext: {
    fontSize: 34,
    fontWeight: '800',
    color: COLORS.gold,
    letterSpacing: 14,
    marginTop: -2,
    textShadowColor: 'rgba(255, 215, 0, 0.4)',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 20,
  },
  taglineWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
    gap: 10,
  },
  taglineLine: {
    width: 30,
    height: 1,
    backgroundColor: 'rgba(255,215,0,0.3)',
  },
  tagline: {
    color: COLORS.textMuted,
    fontSize: 10,
    letterSpacing: 4,
    fontWeight: '700',
  },
  // Form
  formOuter: {
    flex: 1,
    maxWidth: 360,
    borderRadius: 18,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: 'rgba(255, 107, 53, 0.15)',
  },
  formContainer: {
    padding: 28,
  },
  formTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: COLORS.textPrimary,
    textAlign: 'center',
    marginBottom: 20,
    letterSpacing: 1,
  },
  inputWrap: {
    marginBottom: 14,
  },
  inputLabel: {
    color: COLORS.textMuted,
    fontSize: 9,
    fontWeight: '800',
    letterSpacing: 2,
    marginBottom: 6,
  },
  input: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 14,
    color: COLORS.textPrimary,
    fontSize: 14,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.08)',
  },
  errorWrap: {
    backgroundColor: 'rgba(255, 68, 68, 0.1)',
    borderRadius: 8,
    padding: 8,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: 'rgba(255, 68, 68, 0.2)',
  },
  errorText: {
    color: COLORS.error,
    fontSize: 12,
    textAlign: 'center',
    fontWeight: '600',
  },
  submitBtn: {
    marginTop: 4,
    borderRadius: 12,
    overflow: 'hidden',
  },
  btnDisabled: {
    opacity: 0.6,
  },
  submitGradient: {
    padding: 14,
    alignItems: 'center',
    borderRadius: 12,
  },
  submitText: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '900',
    letterSpacing: 2,
  },
  switchText: {
    color: COLORS.textMuted,
    fontSize: 12,
    textAlign: 'center',
    marginTop: 16,
  },
  switchHighlight: {
    color: COLORS.accent,
    fontWeight: '700',
  },
});
