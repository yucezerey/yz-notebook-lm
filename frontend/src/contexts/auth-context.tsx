"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import {
  onAuthStateChanged,
  signInWithPopup,
  signOut as firebaseSignOut,
  type User,
} from "firebase/auth";
import { getFirebaseAuth, getGoogleProvider } from "@/lib/firebase";

const isFirebaseConfigured =
  !!process.env.NEXT_PUBLIC_FIREBASE_API_KEY &&
  process.env.NEXT_PUBLIC_FIREBASE_API_KEY !== "";

// Dev mode mock user when Firebase is not configured
const DEV_USER = {
  uid: "dev-user",
  displayName: "Dev User",
  email: "dev@localhost",
  photoURL: null,
  getIdToken: async () => "dev-token",
} as unknown as User;

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isDevMode: boolean;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isFirebaseConfigured) {
      // Dev mode: no Firebase, skip auth
      setLoading(false);
      return;
    }

    const auth = getFirebaseAuth();
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });
    return unsubscribe;
  }, []);

  const signInWithGoogle = async () => {
    if (!isFirebaseConfigured) {
      // Dev mode: fake sign in
      setUser(DEV_USER);
      return;
    }

    try {
      const auth = getFirebaseAuth();
      const provider = getGoogleProvider();
      await signInWithPopup(auth, provider);
    } catch (error: unknown) {
      const message =
        error instanceof Error ? error.message : "Sign in failed";
      console.error("Sign in error:", message);
      throw error;
    }
  };

  const signOut = async () => {
    if (!isFirebaseConfigured) {
      setUser(null);
      return;
    }

    const auth = getFirebaseAuth();
    await firebaseSignOut(auth);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isDevMode: !isFirebaseConfigured,
        signInWithGoogle,
        signOut,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
